#include <Arduino.h>
#include <LedController.h>
#include <LedSocket.h>
#include <time.h>
#include <DHT.h>
#include <sstream>
#include <string.h>
#include <Persistence.h>
#include <millisDelay.h>

#define DHT_PIN 26
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

time_t now_;
tm t_;


millisDelay run;

uint8_t lastCompareMinute = 255;
float lastCompareValues[2] = {255.0f, 255.0f};

void setup() {
    // put your setup code here, to run once:
    Serial.begin(115200);
    Controller.init();
    Socket.connectToNetwork();
    dht.begin();

    run.start(1000);
}

void loop() {

  if (run.justFinished()) {
    long int t1 = millis(); 
    Socket.listen();
    std::ostringstream ss;


    float tmp = dht.readTemperature();
    float hum = dht.readHumidity();

    time(&now_);
    localtime_r(&now_, &t_);

    if (!isnan(tmp) && !isnan(hum)) {
          ss << tmp;
          std::string tmp_txt(ss.str());
          ss.clear();
          
          ss << hum;
          std::string hum_txt(ss.str());

    } else {
      Serial.println("Failed to read from DHT22-Sensor");
      tmp = 0.0f;
      hum = 0.0f;
    }
   
    if (lastCompareValues[0] == 255.0f) {
      lastCompareValues[0] = tmp;
      lastCompareValues[1] = hum;
    }


    //Decide color for matrix
    if ((t_.tm_min % 5 == 0 && t_.tm_min != lastCompareMinute) || lastCompareMinute == 255) {
      tm target_timestamp = t_;

      if (t_.tm_min % 5 == 0) {
        time_t ts = now_ - (5*60);
        localtime_r(&ts, &target_timestamp);
      } else {
        target_timestamp.tm_min = t_.tm_min - t_.tm_min % 5;
      }
      
      Storage.getPersistedDataByTimestamp(target_timestamp, lastCompareValues);

      lastCompareMinute = t_.tm_min;
    }

    if (Socket.currMode ==  TMP) {
        float diff = lastCompareValues[0] - tmp;

        if (diff > 0) {
          Controller.currColor = CRGB::Blue;
        } else if (diff == 0) {
          Controller.currColor = CRGB::Amethyst;
        } else {
          Controller.currColor = CRGB::IndianRed;
        }
      } else if (Socket.currMode == HUM) {
        float diff = lastCompareValues[1] - hum;
        //Todo: Hum colors
      }

    if (Socket.currMode == TMP) {
      Controller.writeStringToMatrix(Storage.floatToString(tmp));
    } else if (Socket.currMode == HUM) {
      Controller.writeStringToMatrix(Storage.intToString((uint16_t) std::floor(hum)));
    }

    if (t_.tm_min % 5 == 0 && t_.tm_min != Storage.last_persisted_minute && !isnan(tmp)) {
      Storage.persistValue(tmp, hum, t_);
    }

    run.repeat();

    long int t2 = millis();
    Serial.print("Time taken by the task: "); Serial.print(t2-t1); Serial.println(" milliseconds");
  }
  
  //Animation
  Controller.animateColorBar();
  delay(100);
}