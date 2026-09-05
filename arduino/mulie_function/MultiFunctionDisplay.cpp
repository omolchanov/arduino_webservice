#include "MultiFunctionDisplay.h"
#include "display_math.h"

const byte SEGMENT_MAP[] = {
    0xC0,  // 0
    0xF9,  // 1
    0xA4,  // 2
    0xB0,  // 3
    0x99,  // 4
    0x92,  // 5
    0x82,  // 6
    0xF8,  // 7
    0x80,  // 8
    0x90   // 9
};

const byte DIGIT_SELECT[] = {
    0xF1,
    0xF2,
    0xF4,
    0xF8
};

const byte COLON_SEGMENT = 0xBF;

MultiFunctionDisplay::MultiFunctionDisplay(
    byte latchPin,
    byte clockPin,
    byte dataPin
) {
    _latchPin = latchPin;
    _clockPin = clockPin;
    _dataPin = dataPin;
    _clockMode = false;
}

void MultiFunctionDisplay::begin() {
    pinMode(_latchPin, OUTPUT);
    pinMode(_clockPin, OUTPUT);
    pinMode(_dataPin, OUTPUT);

    show(0);
}

void MultiFunctionDisplay::show(int number) {
    split_three_digit_display(number, _digits);
}

void MultiFunctionDisplay::showClock(byte hours, byte minutes) {
    split_clock_display(hours, minutes, _digits);
}

void MultiFunctionDisplay::setClockMode(bool enabled) {
    _clockMode = enabled;
}

void MultiFunctionDisplay::update() {
    static byte position = 0;

    if (!_clockMode && position == 0) {
        position = 1;
    }

    showDigit(position, _digits[position]);

    position++;
    if (_clockMode) {
        if (position >= 4) {
            position = 0;
        }
    } else if (position >= 4) {
        position = 1;
    }
}

void MultiFunctionDisplay::showDigit(
    byte position,
    byte number
) {
    byte segments = SEGMENT_MAP[number];
    if (_clockMode && position == 2) {
        segments |= COLON_SEGMENT;
    }

    digitalWrite(_latchPin, LOW);

    shiftOut(
        _dataPin,
        _clockPin,
        MSBFIRST,
        segments
    );

    shiftOut(
        _dataPin,
        _clockPin,
        MSBFIRST,
        DIGIT_SELECT[position]
    );

    digitalWrite(_latchPin, HIGH);

    delay(2);
}
