#ifndef MULTI_FUNCTION_DISPLAY_H
#define MULTI_FUNCTION_DISPLAY_H

#include <Arduino.h>

class MultiFunctionDisplay {

public:
    MultiFunctionDisplay(byte latchPin, byte clockPin, byte dataPin);

    void begin();
    void show(int number);
    void showClock(byte hours, byte minutes);
    void setClockMode(bool enabled);
    void update();

private:
    byte _latchPin;
    byte _clockPin;
    byte _dataPin;
    bool _clockMode;

    byte _digits[4];

    void showDigit(byte position, byte number);
};

#endif
