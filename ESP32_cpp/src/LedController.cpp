#include <LedController.h>
#include <cstring>
#include <string>

#define NUM_LEDS 256
#define DATA_PIN 2

// 0  -  1  -  2
// |     |     |
// 3  -  4  -  5
// |     |     |
// 6  -  7  -  8
// |     |     |
// 9  -  10 -  11
// |     |     |
// 12 -  13 -  14
std::map<char, std::string> MATRIX_FONT = {
    {'A',"1,3,5,6,7,8,9,11,12,14"},
    {'B',"0,1,3,4,5,6,7,8,9,10,11,12,13"},
    {'C',"1,2,3,6,9,13,14"},
    {'D',"0,1,2,3,5,6,8,9,11,12,13,14"},
    {'E',"0,1,2,3,6,7,8,9,12,13,14"},
    {'F',"0,1,2,3,6,7,8,9,12"},
    {'G',"0,1,3,6,7,8,9,10,11,12,13,14"},
    {'H',"0,2,3,5,6,7,8,9,11,12,14"},
    {'I',"0,1,2,4,7,10,12,13,14"},
    {'J',"2,5,8,9,11,12,13,14"},
    {'K',"0,2,3,4,6,9,10,12,14"},
    {'L',"0,3,6,9,12,13,14"},
    {'M',"0,2,3,4,5,6,8,9,11,12,14"},
    {'N',"0,1,2,3,5,6,8,9,10,11,12,13,14"},
    {'O',"0,1,2,3,5,6,8,9,11,12,13,14"},
    {'P',"0,1,2,3,5,6,7,8,9,12"},
    {'Q',"0,1,2,3,5,6,8,9,10,11,12,13,14"},
    {'R',"0,1,2,3,5,6,7,8,9,10,12,14"},
    {'S',"1,2,3,7,11,12,13"},
    {'T',"0,1,2,4,7,10,13"},
    {'U',"0,2,3,5,6,8,9,11,12,13,14"},
    {'V',"0,2,3,5,6,8,9,11,13"},
    {'W',"0,2,3,5,6,8,9,10,11,12,14"},
    {'X',"0,2,3,5,7,9,11,12,14"},
    {'Y',"0,2,3,5,7,10,13"},
    {'Z',"0,1,2,5,7,8,9,12,13,14"},
    {'1',"2,5,8,11,14"},
    {'2',"0,1,2,5,6,7,8,9,12,13,14"},
    {'3',"0,1,2,5,6,7,8,11,12,13,14"},
    {'4',"0,3,5,6,7,8,11,14"},
    {'5',"0,1,2,3,6,7,8,11,12,13,14"},
    {'6',"0,1,2,3,6,7,8,9,11,12,13,14"},
    {'7',"0,1,2,3,5,8,11,14"},
    {'8',"0,1,2,3,5,6,7,8,9,11,12,13,14"},
    {'9',"0,1,2,3,5,6,7,8,11,12,13,14"},
    {'0',"0,1,2,3,5,6,8,9,11,12,13,14"},
    //{'°',"1,3,5,7"},
    {'.',"13"},
    {'%',"0,5,7,9,14"}
};

LedController Controller;

CRGB led_buf[NUM_LEDS];
CRGB tmp_buf[NUM_LEDS];

int buf_index = 0;

void LedController::init() {
    FastLED.addLeds<NEOPIXEL, DATA_PIN>(led_buf, NUM_LEDS);
    FastLED.setBrightness(10);
}

void LedController::clearBuf() {
    for (int i = 0; i < NUM_LEDS; i++) {
        led_buf[i] = CRGB::Black;
        tmp_buf[i] = CRGB::Black;
    }
}

void LedController::overrideLedBuffer() {
    for (int i = 0; i < NUM_LEDS; i++) {
        led_buf[i] = tmp_buf[i];
    }
}

void LedController::runningDot() {
    clearBuf();
    if (buf_index < NUM_LEDS) {
        buf_index++;
    } else {
        buf_index = 0;
    }

    led_buf[buf_index] = CRGB::DarkBlue;
    FastLED.show();
}

void LedController::writeStringToMatrix(std::string text) {
    clearBuf();
    
    for (int i = 0; i < text.length(); i++) {
        char letter = text[i];
        boolean seperator = true;

        if (letter == '.') {
            //seperator = false;
        }

        writeCharToMatrix(letter, i, seperator);
    }

    blockAnimation = true;
    overrideLedBuffer();
    blockAnimation = false;

    FastLED.show();
}

void LedController::writeCharToMatrix(char letter, int position, boolean seperator) {
    int startIndex = position * CHAR_WIDTH;
    int row_pos;

    if (seperator) {
        startIndex += position;
    }

    if (ROTATION == 1) {
        startIndex = 224 + startIndex;
        row_pos = MATRIX_WIDTH - (NUM_LEDS - startIndex);
    }

    std::string font_index = MATRIX_FONT.find(letter)->second;

    size_t pos = 0;
    std::string token;
    do {
        pos = font_index.find(",");

        if (pos != std::string::npos) {
            token = font_index.substr(0, pos);
            font_index.erase(0, pos + 1);
        } else {
            token = font_index;
        }
        
        int letter_coord = std::atoi(token.c_str());
        if (ROTATION == 0) {

        } else if (ROTATION == 1) {

            if (letter_coord < 3) {
                tmp_buf[startIndex + letter_coord] = currColor;
            } else if (letter_coord < 6) {
                tmp_buf[startIndex - (row_pos * 2 - 1) - (letter_coord - 3) - 2] = currColor;
            } else if (letter_coord < 9) {
                tmp_buf[startIndex - MATRIX_WIDTH * 2 + (letter_coord - 6)] = currColor;
            } else if (letter_coord < 12) {
                tmp_buf[startIndex - (row_pos + MATRIX_WIDTH) * 2 - 1 - (letter_coord - 9)] = currColor;
            } else {
                tmp_buf[startIndex - MATRIX_WIDTH * 4 + (letter_coord - 12)] = currColor;
            }
        }
    } while (pos != std::string::npos);

}

void LedController::animateColorBar() {

}
