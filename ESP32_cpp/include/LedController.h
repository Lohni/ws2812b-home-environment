#include <map>

#define MATRIX_WIDTH 32
#define CHAR_WIDTH 3
#define ROTATION 1

class LedController {
    private:
        boolean blockAnimation = false;
        void animateColorBar();
        void clearBuf();
        void overrideLedBuffer();

    public:
        void init();
        void runningDot();
        void writeStringToMatrix(std::string text);
        void writeCharToMatrix(char letter, int position, boolean seperator);
};

extern LedController Controller;