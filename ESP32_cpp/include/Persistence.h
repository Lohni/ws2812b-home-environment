#include <SPIFFS.h>
#include <time.h>

#define STORAGE_FILENAME "/sensorData.dat"

class Persistence {
    private:
        uint16_t sensorDataToBytes(float tmp, float hum);
        void persistedBytesToValue(uint8_t firstByte, uint8_t secondByte, float* ret);
        void validateFileStructure(File sensorData, uint16_t curr_identifier_value, const char* id);


    public:
        int last_persisted_minute = -1;
        void persistValue(float tmp, float hum, tm t);
        float* getPersistedDataByTimestamp(tm t, float* ret);
        std::string decodeWholeFile();
        void overrideFile(std::string body);
        std::string intToString(uint16_t value);
        std::string floatToString(float value);
};

extern Persistence Storage;

static const char YEAR_ID[3] = {'y', 'y', ':'};
static const char MONTH_ID[3] = {'m', 'm', ':'};
static const char HOUR_ID[3] = {'h', 'h', ':'};
static const char DAY_ID[3] = {'d', 'd', ':'};