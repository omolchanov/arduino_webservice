import asyncio
import json
import logging
import re
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import serial
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COM_PORT = "COM8"
BAUD_RATE = 9600
RECONNECT_DELAY = 3
ARDUINO_BOOT_DELAY = 2
VALID_KEYS = set("0123456789*#ABCD")
PRESSED_PREFIX = "Pressed: "
IGNORED_LINES = {"Keypad ready"}
DISTANCE_PATTERN = re.compile(r"^Distance:\s*([\d.]+)\s*cm$")
LIGHT_PATTERN = re.compile(r"^Light:\s*(\d+)$")
TEMPERATURE_PATTERN = re.compile(r"^Temperature:\s*([\d.]+)\s*C$")
SIGNAL_PIN_PATTERN = re.compile(r"^SIGNAL_PIN:\s*Logic\s*([01])\s*\(")
POT_PATTERN = re.compile(
    r"^(?:Signal:\s*([01])\s*\|\s*)?"
    r"Pot:\s*([\d.]+)\s*V\s*\|\s*Logic:\s*(0(?:\s*\(LOW\))?|UNDEFINED|1(?:\s*\(HIGH\))?)"
    r"(?:\s*\|\s*PWM:\s*\d+)?"
    r"(?:\s*\|\s*Shunt:\s*[\d.]+\s*V)?"
    r"(?:\s*\|\s*Current:\s*([\d.]+)\s*mA)?"
    r"(?:\s*\|\s*LED Resistance:\s*([\d.]+)\s*Ohm)?$"
)
VALVE_PATTERN = re.compile(
    r"^A\s*=\s*(\d)\s*\|\s*B\s*=\s*(\d)\s*\|\s*Y\s*=\s*(\d)\s*\|\s*Gate\s*=\s*(AND|OR|NOT|NAND|NOR|XOR|XNOR)$"
)
DISPLAY_PATTERN = re.compile(r"^Display:\s*(\d{1,3})$")
VALID_VALVE_GATES = frozenset({"AND", "OR", "NOT", "NAND", "NOR", "XOR", "XNOR"})

clients: list[WebSocket] = []
key_queue: asyncio.Queue[str] | None = None
event_loop: asyncio.AbstractEventLoop | None = None
serial_connected = False
last_distance_cm: float | None = None
last_light_level: int | None = None
last_temperature_c: float | None = None
last_logic_value: int | None = None
last_potentiometer_v: float | None = None
last_detected_value: float | None = None
last_current_ma: float | None = None
last_led_resistance_ohm: float | None = None
last_valve_a: int | None = None
last_valve_b: int | None = None
last_valve_y: int | None = None
last_valve_gate: str | None = None
last_display_value: int | None = None
serial_stop = threading.Event()
serial_port: serial.Serial | None = None
serial_thread: threading.Thread | None = None
serial_lock = threading.Lock()

STATIC_DIR = Path(__file__).parent / "static"


def parse_key_line(line: str) -> str | None:
    line = line.strip()
    if not line or line in IGNORED_LINES:
        return None
    if line.startswith(PRESSED_PREFIX):
        key = line[len(PRESSED_PREFIX) :].strip()
        if len(key) == 1 and key in VALID_KEYS:
            return key
        return None
    if len(line) == 1 and line in VALID_KEYS:
        return line
    return None


def parse_distance_line(line: str) -> float | None:
    match = DISTANCE_PATTERN.match(line.strip())
    if not match:
        return None
    return float(match.group(1))


def parse_light_line(line: str) -> int | None:
    match = LIGHT_PATTERN.match(line.strip())
    if not match:
        return None
    return int(match.group(1))


def parse_temperature_line(line: str) -> float | None:
    match = TEMPERATURE_PATTERN.match(line.strip())
    if not match:
        return None
    return float(match.group(1))


def parse_signal_pin_line(line: str) -> int | None:
    match = SIGNAL_PIN_PATTERN.match(line.strip())
    if not match:
        return None
    return int(match.group(1))


def _map_logic_raw(logic_raw: str) -> float:
    if logic_raw == "UNDEFINED" or logic_raw.startswith("0"):
        return 0.0
    return 1.0


def parse_pot_line(
    line: str,
) -> tuple[float, float, float | None, float | None, int | None] | None:
    match = POT_PATTERN.match(line.strip())
    if not match:
        return None
    signal = int(match.group(1)) if match.group(1) is not None else None
    voltage = float(match.group(2))
    logic = _map_logic_raw(match.group(3))
    current_ma = float(match.group(4)) if match.group(4) is not None else None
    resistance_ohm = float(match.group(5)) if match.group(5) is not None else None
    return voltage, logic, current_ma, resistance_ohm, signal


def parse_valve_line(line: str) -> tuple[int, int, int, str] | None:
    match = VALVE_PATTERN.match(line.strip())
    if not match:
        return None
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        match.group(4),
    )


def parse_display_line(line: str) -> int | None:
    match = DISPLAY_PATTERN.match(line.strip())
    if not match:
        return None
    value = int(match.group(1))
    if value > 999:
        return None
    return value


async def broadcast_message(message: str) -> None:
    dead: list[WebSocket] = []
    for client in clients:
        try:
            await client.send_text(message)
        except Exception:
            dead.append(client)
    for client in dead:
        if client in clients:
            clients.remove(client)


async def broadcast_key(key: str) -> None:
    await broadcast_message(json.dumps({"type": "key", "key": key}))


async def broadcast_distance(cm: float) -> None:
    await broadcast_message(json.dumps({"type": "distance", "cm": cm}))


async def broadcast_light(level: int) -> None:
    await broadcast_message(json.dumps({"type": "light", "level": level}))


async def broadcast_temperature(c: float) -> None:
    await broadcast_message(json.dumps({"type": "temperature", "c": c}))


async def broadcast_logic(value: int) -> None:
    await broadcast_message(json.dumps({"type": "logic", "value": value}))


async def broadcast_potentiometer(v: float) -> None:
    await broadcast_message(json.dumps({"type": "potentiometer", "v": v}))


async def broadcast_detected(value: float) -> None:
    await broadcast_message(json.dumps({"type": "detected", "value": value}))


async def broadcast_current(ma: float) -> None:
    await broadcast_message(json.dumps({"type": "current", "ma": ma}))


async def broadcast_resistance(ohm: float) -> None:
    await broadcast_message(json.dumps({"type": "resistance", "ohm": ohm}))


async def broadcast_valve(a: int, b: int, y: int, gate: str) -> None:
    await broadcast_message(
        json.dumps({"type": "valve", "a": a, "b": b, "y": y, "gate": gate})
    )


async def broadcast_display(value: int) -> None:
    await broadcast_message(json.dumps({"type": "display", "value": value}))


async def broadcast_serial_status(connected: bool) -> None:
    await broadcast_message(
        json.dumps(
            {
                "type": "serial_status",
                "connected": connected,
                "com_port": COM_PORT,
            }
        )
    )


def notify_serial_status(connected: bool) -> None:
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_serial_status(connected), event_loop)


def notify_distance(cm: float) -> None:
    global last_distance_cm
    last_distance_cm = cm
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_distance(cm), event_loop)


def notify_light(level: int) -> None:
    global last_light_level
    last_light_level = level
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_light(level), event_loop)


def notify_temperature(c: float) -> None:
    global last_temperature_c
    last_temperature_c = c
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_temperature(c), event_loop)


def notify_logic(value: int) -> None:
    global last_logic_value
    last_logic_value = value
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_logic(value), event_loop)


def notify_potentiometer(v: float) -> None:
    global last_potentiometer_v
    last_potentiometer_v = v
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_potentiometer(v), event_loop)


def notify_detected(value: float) -> None:
    global last_detected_value
    last_detected_value = value
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_detected(value), event_loop)


def notify_current(ma: float) -> None:
    global last_current_ma
    last_current_ma = ma
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_current(ma), event_loop)


def notify_resistance(ohm: float) -> None:
    global last_led_resistance_ohm
    last_led_resistance_ohm = ohm
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_resistance(ohm), event_loop)


def notify_valve(a: int, b: int, y: int, gate: str) -> None:
    global last_valve_a, last_valve_b, last_valve_y, last_valve_gate
    last_valve_a = a
    last_valve_b = b
    last_valve_y = y
    last_valve_gate = gate
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_valve(a, b, y, gate), event_loop)


def notify_display(value: int) -> None:
    global last_display_value
    last_display_value = value
    if event_loop and event_loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast_display(value), event_loop)


def write_serial_gate(gate: str) -> bool:
    if gate not in VALID_VALVE_GATES:
        return False
    command = f"{gate}\n".encode()
    with serial_lock:
        if not serial_connected or serial_port is None or not serial_port.is_open:
            return False
        serial_port.write(command)
        return True


def write_serial_display(value: int) -> bool:
    if value < 0 or value > 999:
        return False
    command = f"S{value}\n".encode()
    with serial_lock:
        if not serial_connected or serial_port is None or not serial_port.is_open:
            return False
        serial_port.write(command)
        return True


async def consume_keys() -> None:
    while True:
        key = await key_queue.get()
        logger.info("Key pressed: %s (clients: %d)", key, len(clients))
        await broadcast_key(key)


def read_serial(port: serial.Serial) -> None:
    while not serial_stop.is_set():
        try:
            raw = port.readline()
        except serial.SerialException as exc:
            logger.error("Serial read failed: %s", exc)
            break
        if not raw:
            continue
        line = raw.decode(errors="ignore").strip()
        if not line:
            continue
        distance = parse_distance_line(line)
        if distance is not None:
            logger.info("Distance: %.2f cm (clients: %d)", distance, len(clients))
            notify_distance(distance)
            continue
        light = parse_light_line(line)
        if light is not None:
            logger.info("Light: %d (clients: %d)", light, len(clients))
            notify_light(light)
            continue
        temperature = parse_temperature_line(line)
        if temperature is not None:
            logger.info("Temperature: %.2f C (clients: %d)", temperature, len(clients))
            notify_temperature(temperature)
            continue
        signal_pin = parse_signal_pin_line(line)
        if signal_pin is not None:
            logger.info("SIGNAL_PIN logic=%d (clients: %d)", signal_pin, len(clients))
            notify_logic(signal_pin)
            continue
        pot = parse_pot_line(line)
        if pot is not None:
            pot_v, detected, current_ma, resistance_ohm, signal = pot
            logger.info(
                "Pot: %.2f V logic=%s (clients: %d)",
                pot_v,
                detected,
                len(clients),
            )
            if signal is not None:
                notify_logic(signal)
            notify_potentiometer(pot_v)
            notify_detected(detected)
            if current_ma is not None:
                notify_current(current_ma)
            if resistance_ohm is not None:
                notify_resistance(resistance_ohm)
            continue
        valve = parse_valve_line(line)
        if valve is not None:
            a, b, y, gate = valve
            logger.info(
                "Valve: A=%d B=%d Y=%d gate=%s (clients: %d)",
                a,
                b,
                y,
                gate,
                len(clients),
            )
            notify_valve(a, b, y, gate)
            continue
        display_value = parse_display_line(line)
        if display_value is not None:
            logger.info(
                "Display: %d (clients: %d)",
                display_value,
                len(clients),
            )
            notify_display(display_value)
            continue
        key = parse_key_line(line)
        if key:
            asyncio.run_coroutine_threadsafe(key_queue.put(key), event_loop)
        else:
            logger.debug("Ignored serial line: %r", line)


def close_port(port: serial.Serial | None) -> None:
    global serial_port
    if port and port.is_open:
        try:
            port.close()
        except serial.SerialException:
            pass
    if serial_port is port:
        serial_port = None


def serial_manager() -> None:
    global serial_connected, serial_port

    while not serial_stop.is_set():
        port = None
        try:
            port = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
            serial_port = port
            time.sleep(ARDUINO_BOOT_DELAY)
            port.reset_input_buffer()
            serial_connected = True
            notify_serial_status(True)
            logger.info("Serial connected on %s", COM_PORT)
            read_serial(port)
        except serial.SerialException as exc:
            logger.warning("Serial unavailable on %s: %s", COM_PORT, exc)
        except Exception as exc:
            logger.error("Serial manager error: %s", exc)
        finally:
            was_connected = serial_connected
            serial_connected = False
            close_port(port)
            if was_connected:
                notify_serial_status(False)
                logger.info("Serial disconnected from %s", COM_PORT)

        if not serial_stop.is_set():
            logger.info("Retrying serial on %s in %ds...", COM_PORT, RECONNECT_DELAY)
            serial_stop.wait(RECONNECT_DELAY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global key_queue, event_loop, serial_thread
    event_loop = asyncio.get_running_loop()
    key_queue = asyncio.Queue()
    consumer = asyncio.create_task(consume_keys())

    serial_stop.clear()
    serial_thread = threading.Thread(target=serial_manager, daemon=True)
    serial_thread.start()

    yield

    serial_stop.set()
    if serial_thread:
        serial_thread.join(timeout=5)
    serial_thread = None

    consumer.cancel()
    try:
        await consumer
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/sensors")
async def sensors():
    return FileResponse(STATIC_DIR / "sensors.html")


@app.get("/digital")
async def digital():
    return FileResponse(STATIC_DIR / "digital.html")


@app.get("/valves")
async def valves():
    return FileResponse(STATIC_DIR / "valves.html")


@app.get("/display")
async def display():
    return FileResponse(STATIC_DIR / "display.html")


@app.get("/api/status")
async def status():
    return {
        "serial_connected": serial_connected,
        "com_port": COM_PORT,
        "ws_clients": len(clients),
        "last_distance_cm": last_distance_cm,
        "last_light_level": last_light_level,
        "last_temperature_c": last_temperature_c,
        "last_logic_value": last_logic_value,
        "last_potentiometer_v": last_potentiometer_v,
        "last_detected_value": last_detected_value,
        "last_current_ma": last_current_ma,
        "last_led_resistance_ohm": last_led_resistance_ohm,
        "last_valve_a": last_valve_a,
        "last_valve_b": last_valve_b,
        "last_valve_y": last_valve_y,
        "last_valve_gate": last_valve_gate,
        "display_value": last_display_value,
    }


@app.post("/api/valve/gate")
async def set_valve_gate(body: dict):
    gate = body.get("gate")
    if gate not in VALID_VALVE_GATES:
        raise HTTPException(status_code=400, detail="Invalid gate")
    if not write_serial_gate(gate):
        raise HTTPException(status_code=503, detail="Serial not connected")
    return {"ok": True, "gate": gate}


@app.post("/api/display/value")
async def set_display_value(body: dict):
    value = body.get("value")
    if not isinstance(value, int) or value < 0 or value > 999:
        raise HTTPException(status_code=400, detail="Invalid value")
    if not write_serial_display(value):
        raise HTTPException(status_code=503, detail="Serial not connected")
    return {"ok": True, "value": value}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    await websocket.send_text(
        json.dumps(
            {
                "type": "serial_status",
                "connected": serial_connected,
                "com_port": COM_PORT,
            }
        )
    )
    if last_distance_cm is not None:
        await websocket.send_text(
            json.dumps({"type": "distance", "cm": last_distance_cm, "cached": True})
        )
    if last_light_level is not None:
        await websocket.send_text(
            json.dumps({"type": "light", "level": last_light_level, "cached": True})
        )
    if last_temperature_c is not None:
        await websocket.send_text(
            json.dumps(
                {"type": "temperature", "c": last_temperature_c, "cached": True}
            )
        )
    if last_logic_value is not None:
        await websocket.send_text(
            json.dumps({"type": "logic", "value": last_logic_value, "cached": True})
        )
    if last_potentiometer_v is not None:
        await websocket.send_text(
            json.dumps(
                {"type": "potentiometer", "v": last_potentiometer_v, "cached": True}
            )
        )
    if last_detected_value is not None:
        await websocket.send_text(
            json.dumps(
                {"type": "detected", "value": last_detected_value, "cached": True}
            )
        )
    if last_current_ma is not None:
        await websocket.send_text(
            json.dumps({"type": "current", "ma": last_current_ma, "cached": True})
        )
    if last_led_resistance_ohm is not None:
        await websocket.send_text(
            json.dumps(
                {
                    "type": "resistance",
                    "ohm": last_led_resistance_ohm,
                    "cached": True,
                }
            )
        )
    if last_valve_gate is not None:
        await websocket.send_text(
            json.dumps(
                {
                    "type": "valve",
                    "a": last_valve_a,
                    "b": last_valve_b,
                    "y": last_valve_y,
                    "gate": last_valve_gate,
                    "cached": True,
                }
            )
        )
    if last_display_value is not None:
        await websocket.send_text(
            json.dumps(
                {"type": "display", "value": last_display_value, "cached": True}
            )
        )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in clients:
            clients.remove(websocket)
