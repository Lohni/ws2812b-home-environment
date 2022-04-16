#include <Arduino.h>
#include <LedController.h>
#include <LedSocket.h>
#include <time.h>
#include <DHT.h>
#include <sstream>
#include <string.h>

#define DHT_PIN 26
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    // put your setup code here, to run once:
    Serial.begin(115200);
    Controller.init();
    Socket.connectToNetwork();
    dht.begin();
}

void loop() {
    //long int t1 = millis();

    std::ostringstream ss;

    float tmp = dht.readTemperature();
    float hum = dht.readHumidity();

    if (!isnan(tmp) && !isnan(hum)) {
          ss << tmp;
          std::string tmp_txt(ss.str());
          ss.clear();
          
          ss << hum;
          std::string hum_txt(ss.str());
    } else {
      Serial.println("Failed to read from DHT22-Sensor");
    }

    Controller.writeStringToMatrix("TEST");
    Socket.listen();

    delay(1000);

    //long int t2 = millis();
    //Serial.print("Time taken by the task: "); Serial.print(t2-t1); Serial.println(" milliseconds");
}