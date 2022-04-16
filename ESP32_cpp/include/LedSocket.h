#include <map>

#define NTP_SERVER "at.pool.ntp.org"
#define TIMEZONE "CET-1CEST,M3.5.0,M10.5.0/3" //Europe-Vienna

class LedSocket {
    public:
        std::string conf_file = "/wlan_conf.json";
        void connectToNetwork();
        void initServer();
        void listen();
};

extern LedSocket Socket;