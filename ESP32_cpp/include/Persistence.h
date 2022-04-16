#include <SPIFFS.h>
#include <time.h>

#define STORAGE_FILENAME "sensorData.dat"

class Persistence {
    private:
        int last_persisted_minute = -1;
        uint16_t sensorDataToBytes(float tmp, float hum);
        float* persistedBytesToValue(uint8_t firstByte, uint8_t secondByte);
        void validateFileStructure(File sensorData, uint16_t curr_identifier_value, const char* id);

        std::string intToString(uint16_t value);
        std::string floatToString(float value);
    public:
        void persistValue(float tmp, float hum, tm t);
        float* getPersistedDataByTimestamp(tm t);
        std::string decodeWholeFile();
        void overrideFile(std::string);
};

extern Persistence Storage;

static const char YEAR_ID[3] = {'y', 'y', ':'};
static const char MONTH_ID[3] = {'m', 'm', ':'};
static const char HOUR_ID[3] = {'d', 'd', ':'};
static const char DAY_ID[3] = {'h', 'h', ':'};