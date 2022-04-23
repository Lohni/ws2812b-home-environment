#include <LedSocket.h>
#include <WiFi.h>
#include <cJSON.h>
#include <SPIFFS.h>
#include <sntp.h>
#include <time.h>
#include <Persistence.h>

time_t now;
tm t;        

LedSocket Socket;
WiFiServer server;

void LedSocket::connectToNetwork() {
    std::string ssid;
    std::string pw;

    if(!SPIFFS.begin(true)){
        Serial.println("An Error has occurred while mounting SPIFFS");
    return;
    }

    File confFile = SPIFFS.open(Socket.conf_file.c_str());
    if(!confFile){
        Serial.println("Failed to open WiFi-Config!");
        return;
    }

    std::string content = confFile.readString().c_str();
    Serial.println(content.c_str());

    cJSON *conf;
    conf = cJSON_Parse(content.c_str());
    ssid = cJSON_GetObjectItem(conf, "name")->valuestring;
    pw = cJSON_GetObjectItem(conf, "password")->valuestring;


    configTime(0, 0, NTP_SERVER);
    setenv("TZ", TIMEZONE, 1);
    tzset();

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid.c_str(), pw.c_str());
    while (WiFi.status() != WL_CONNECTED) {
        Serial.println("Establishing connection to WiFi..");Serial.println(WiFi.status());
        delay(1000);
    }

    Serial.println("Connected to network");

    server.begin();

    Serial.print("IP Address: ");Serial.println(WiFi.localIP());

    do {
        delay(1000);
        time(&now);
        localtime_r(&now, &t);
        Serial.println("Waiting for SNTP");
    } while(t.tm_year+1900 == 1970);

    Serial.print("System time set: ");
    Serial.print(t.tm_year+1900);Serial.print(t.tm_mon+1);Serial.print(t.tm_mday);Serial.print(t.tm_hour);Serial.println(t.tm_min);
}

void LedSocket::listen() {
    WiFiClient client = server.available();
    std::string contentLength = "";
    std::string body = "";

    if (client) {
        if (client.available() > 0) {
            Serial.println("New connection");

            std::string req = client.readString().c_str();
            int sep_pos = req.find(' ');

            std::string req_method = req.substr(0, sep_pos);
            req = req.substr(sep_pos + 1, req.size() - 1);

            sep_pos = req.find(' ');
            std::string uri = req.substr(0, sep_pos);

            if (req_method == "POST") {
                if (uri == "/storage") {
                    int body_pos = req.find("\r\n\r\n");
                    std::string data = req.substr(body_pos + 4 , req.length());

                    Serial.println(data.c_str());

                    Storage.overrideFile(data);
                }

            } else if (req_method == "GET") {
                if (uri == "/storage") {
                    body = Storage.decodeWholeFile();
                    contentLength = "Content-Length:" + body.size() + '\r\n';
                }
            }

            std::string response = "HTTP/1.1 200 OK\r\nContent-Type:text/html; encoding=utf8\r\n" 
                        + contentLength + "Connection:close\r\n\r\n" + body;

            client.write(response.c_str());
            client.~WiFiClient();
        }
    }
}