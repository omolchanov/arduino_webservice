import asyncio
import json
import logging
import re
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import serial
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
    r"^Pot:\s*([\d.]+)\s*V\s*\|\s*Logic:\s*(0|UNDEFINED|1)(?:\s*\|\s*PWM:\s*\d+)?$"
)

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
serial_stop = threading.Event()
serial_port: serial.Serial | None = None
serial_thread: threading.Thread | None = None

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


def parse_pot_line(line: str) -> tuple[float, float] | None:
    match = POT_PATTERN.match(line.strip())
    if not match:
        return None
    voltage = float(match.group(1))
    logic_raw = match.group(2)
    logic = 0.5 if logic_raw == "UNDEFINED" else float(logic_raw)
    return voltage, logic


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
            pot_v, detected = pot
            logger.info(
                "Pot: %.2f V logic=%s (clients: %d)",
                pot_v,
                detected,
                len(clients),
            )
            notify_potentiometer(pot_v)
            notify_detected(detected)
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
    }


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
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in clients:
            clients.remove(websocket)
