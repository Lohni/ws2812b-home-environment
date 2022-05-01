#include <map>
#include <FastLED.h>

#define MATRIX_WIDTH 32
#define CHAR_WIDTH 3
#define ROTATION 1

class LedController {
    private:
        boolean blockAnimation = false;
        void clearBuf();
        void overrideLedBuffer();

    public:
        CRGB currColor = CRGB::Amethyst;
        void init();
        void runningDot();
        void writeStringToMatrix(std::string text);
        void writeCharToMatrix(char letter, int position, boolean seperator);
        void animateColorBar();
};

extern LedController Controller;