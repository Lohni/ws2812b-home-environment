#include <Persistence.h>
#include <cmath>
#include <sstream>
#include <iostream>

Persistence Storage;

uint16_t Persistence::sensorDataToBytes(float tmp, float hum) {
        // Byte-Composition for Sensor-Data:
        // AAAABBBB | BCCCCCCC
        // A -> 4Bit for Temp. comma -> 0-9 / 16
        // B -> 5Bit for Temp. dezimal -> 0-32
        // C -> 7Bit for Humidity -> 0-100 / 128
        uint8_t tmp_dec = std::floor(tmp);
        uint8_t tmp_comma = (tmp - tmp_dec) * 10;
        uint8_t hum_dec = std::floor(hum);

        uint8_t decLSB = tmp_dec & 1;
        uint8_t decRest = (tmp_dec >> 1) & 0b00001111;
        uint8_t hum_byte = hum_dec & 0b01111111;
        
        uint8_t firstByte = (tmp_comma << 4) | decRest;
        uint8_t secondByte = (decLSB << 7) | hum_byte;

        uint16_t bytes_to_persist = firstByte << 8 | secondByte;
        return bytes_to_persist;
}

void Persistence::persistedBytesToValue(uint8_t firstByte, uint8_t secondByte, float* ret) {
        float tmp_comma = (firstByte >> 4) / 10;
        uint8_t tmp_dec = (secondByte >> 7) | ((firstByte & 0b00001111) << 1);
        uint8_t humidity = secondByte & 0b01111111;

        Serial.println(tmp_comma);
        Serial.println(tmp_dec);

        ret[0] = tmp_comma + tmp_dec; 
        ret[1] = (float) humidity;
}

void Persistence::persistValue(float tmp, float hum, tm t) {
        if(!SPIFFS.begin(true)){
                Serial.println("An Error has occurred while mounting SPIFFS");
                return;
        }

        uint16_t year = t.tm_year + 1900;
        uint16_t month = t.tm_mon + 1;
        uint16_t day = t.tm_mday;
        uint16_t hour = t.tm_hour;
        uint16_t min = t.tm_min;

        uint16_t data_bytes = sensorDataToBytes(tmp, hum);

        File sensorData = SPIFFS.open(STORAGE_FILENAME, FILE_WRITE);

        if (!sensorData) {
                Serial.println("Failed to open Sensor-Datafile");
                return;
        }
        
        validateFileStructure(sensorData, year, YEAR_ID);
        validateFileStructure(sensorData, month, MONTH_ID);
        validateFileStructure(sensorData, hour, HOUR_ID);
        validateFileStructure(sensorData, day, DAY_ID);

        while (true) {
                char line[5];
                int bytesRead = sensorData.readBytes(line, 5);
                 if (bytesRead == 5) {
                        uint16_t persistedTime = line[0] << 8 | line[1];
                        if (persistedTime == min) {
                                //Entry for curr minute already exists
                                break;
                        }
                } else if (bytesRead == 0) {
                        sensorData.write(min);
                        sensorData.write(':');
                        sensorData.write(data_bytes);
                        last_persisted_minute = min;
                        break;
                } else {
                        Serial.println('Wrong number of bytes read: ' + bytesRead);
                        break;
                }
        }

        sensorData.close();
}

void Persistence::validateFileStructure(File sensorData, uint16_t curr_identifier_value, const char* id) {
        while (true) {
                char line[5]; 
                int bytesRead = sensorData.readBytes(line, 5);
                if (bytesRead == 5) {
                        if (line[0] == id[0] && line[1] == id[1]) {
                                uint16_t a = line[3] << 8 | line[4];
                                if (a == curr_identifier_value) {
                                    break;    
                                }
                        }
                } else if (bytesRead == 0) {
                        for (int i = 0; i < 3; i++) {
                                sensorData.write(id[i]);
                        }

                        sensorData.write(curr_identifier_value);

                        Serial.println('Created Entry: ' + id);
                        break;
                } else {
                        Serial.println('Wrong number of bytes read: ' + bytesRead);
                        break;
                }
        }
}

float* Persistence::getPersistedDataByTimestamp(tm t) {
        if(!SPIFFS.begin(true)){
                Serial.println("An Error has occurred while mounting SPIFFS");
                return NULL;
        }

        File sensorData = SPIFFS.open(STORAGE_FILENAME, FILE_READ);

        if (!sensorData) {
                Serial.println("Failed to open Sensor-Datafile");
                return NULL;
        }

        uint16_t year = t.tm_year + 1900;
        uint16_t month = t.tm_mon + 1;
        uint16_t day = t.tm_mday;
        uint16_t hour = t.tm_hour;

        uint16_t dataTime = t.tm_min;

        uint8_t mtc[4][5] = {{YEAR_ID[0], YEAR_ID[1], YEAR_ID[2], year >> 8, year & 0b0000000011111111},
                             {MONTH_ID[0], MONTH_ID[1], MONTH_ID[2], month >> 8, month & 0b0000000011111111},
                             {DAY_ID[0], DAY_ID[1], DAY_ID[2], day >> 8, day & 0b0000000011111111},
                             {HOUR_ID[0], HOUR_ID[1], HOUR_ID[2], hour >> 8, hour & 0b0000000011111111}};
        
        uint8_t line[5] = {255, 255, 255, 255, 255};
        int currMtcIndex = 0;
        int bytesRead = sensorData.read(line, 5);
        while (bytesRead >= 0 || line[0] == 255) {
                if (currMtcIndex < 4) {
                        if (line[0] == mtc[currMtcIndex][0] && line[1] == mtc[currMtcIndex][1] && line[2] == mtc[currMtcIndex][2] 
                                && line[3] == mtc[currMtcIndex][3] && line[4] == mtc[currMtcIndex][4]) {
                                currMtcIndex++;
                        }
                } else {
                        uint16_t persistedMin = line[0] << 8 || line[1];
                        if (persistedMin == dataTime) {
                                break;
                        }
                }
        }

        sensorData.close();
        if (bytesRead > 0) {
                float ret[2];
                persistedBytesToValue(line[3], line[4], ret);
                return ret;
        }

        float empty[2] = {0 , 0};
        return empty;
}

std::string Persistence::decodeWholeFile() {
        if(!SPIFFS.begin(true)){
                Serial.println("An Error has occurred while mounting SPIFFS");
                return "An Error has occurred while mounting SPIFFS";
        }

        File sensorData = SPIFFS.open(STORAGE_FILENAME, FILE_READ);

        if (!sensorData) {
                Serial.println("Failed to open Sensor-Datafile");
                return "Failed to open Sensor-Datafile";
        }

        std::string body = "";

        uint8_t line[5]; 
        while (true) {
                int bytesRead = sensorData.read(line, 5);

                if (bytesRead == 5) {
                        if (line[0] == (uint8_t) 'y' || line[0] == (uint8_t) 'm' || line[0] == (uint8_t) 'd' || line[0] == (uint8_t) 'h') {
                                uint16_t val = line[3] << 8 | line[4];
                                body = body + (char) line[0] + (char) line[1] + (char) line[2] + intToString(val) + "\n";
                        } else {
                                uint16_t persistedMin = line[0] << 8 | line[1];
                                Serial.println(persistedMin);
                                float values[2];
                                persistedBytesToValue(line[3], line[4], values);

                                body = body + intToString(persistedMin) + (char) line[2] + floatToString(values[0]) + "," + floatToString(values[1]) + "\n";
                        }
                } else {
                        break;
                }
        }

        sensorData.close();

        Serial.println(body.c_str());
        return body;
}

void Persistence::overrideFile(std::string body) {
        if(!SPIFFS.begin(true)){
                Serial.println("An Error has occurred while mounting SPIFFS");
                return;
        }

        File sensorData = SPIFFS.open(STORAGE_FILENAME, FILE_WRITE);

        if (!sensorData) {
                Serial.println("Failed to open Sensor-Datafile");
                return;
        }

        size_t pos = 0;
        std::string line;
        while (pos != std::string::npos) {
                pos = body.find('\n');

                if (pos != std::string::npos) {
                        line = body.substr(0, pos - 1);
                        body.erase(0, pos+1);
                } else {
                        line = body;
                }

                int dp = line.find(':');
                std::string line_start = line.substr(0, dp);
                std::string line_end = line.substr(dp+1, line.size() -1);

                if (line_start == "yy" || line_start == "mm" || line_start == "dd" || line_start == "hh") {
                        uint16_t val;
                        std::istringstream iss(line_end); // Values 0 is not sucessfull
                        
                        iss >> val;

                        const char* pre = line_start.c_str();

                        sensorData.write((uint8_t) pre[0]);
                        sensorData.write((uint8_t) pre[1]);
                        sensorData.write((uint8_t) ':');
                        sensorData.write((uint8_t) (val >> 8));
                        sensorData.write((uint8_t) val & 0b0000000011111111);
                } else {
                        int tmp_sep = line_end.find(',');
                        std::string tmp_string = line_end.substr(0, tmp_sep);
                        int comma_pos = tmp_string.find('.');

                        std::string sdec = tmp_string.substr(0, comma_pos);
                        std::string scomma = tmp_string.substr(comma_pos + 1, 1);
                        std::string shum = line_end.substr(tmp_sep + 1, 2);

                        uint16_t tmp_dec;
                        uint16_t tmp_comma;
                        uint16_t hum_dec;
                        std::istringstream tdec(sdec);
                        std::istringstream tcomma(scomma);
                        std::istringstream thum(shum);

                        tdec >> tmp_dec;
                        tcomma >> tmp_comma;
                        thum >> hum_dec;

                        float tmp = tmp_dec + (tmp_comma / 10);
                        float hum = (float) hum_dec;

                        uint16_t ls;
                        std::istringstream iss(line_start);
                        iss >> ls;

                        uint16_t dataBytes = sensorDataToBytes(tmp, hum);
                        
                        Serial.println(dataBytes);

                        sensorData.write((uint8_t) (ls >> 8));
                        sensorData.write((uint8_t) (ls & 0b0000000011111111));
                        sensorData.write((uint8_t) ':');
                        sensorData.write((uint8_t) (dataBytes >> 8));
                        sensorData.write((uint8_t) (dataBytes & 0b0000000011111111));
                }       


        }

        sensorData.close();
        Serial.println("Overwritten sensorData.dat");
}

std::string Persistence::intToString(uint16_t value) {
        std::string res;
        while (value > 10) {
                uint8_t number = value % 10;
                res = res + (char) (number + 48);
                value = value / 10;
        }

        res = res + (char) (value + 48);
        std::reverse(res.begin(), res.end());
        return res;
}

std::string Persistence::floatToString(float value) {
        std::string res_dec = intToString(floorf(value));

        float comma = value - floorf(value);
        uint8_t firstComma = floorf(comma * 10);

        return res_dec + "." + (char) (firstComma + 48);
}