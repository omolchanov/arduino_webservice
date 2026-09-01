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

MultiFunctionDisplay::MultiFunctionDisplay(
    byte latchPin,
    byte clockPin,
    byte dataPin
) {
    _latchPin = latchPin;
    _clockPin = clockPin;
    _dataPin = dataPin;
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

void MultiFunctionDisplay::update() {
    static byte position = 1;

    showDigit(position, _digits[position]);

    position++;
    if (position >= 4) {
        position = 1;
    }
}

void MultiFunctionDisplay::showDigit(
    byte position,
    byte number
) {
    digitalWrite(_latchPin, LOW);

    shiftOut(
        _dataPin,
        _clockPin,
        MSBFIRST,
        SEGMENT_MAP[number]
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
