import time
import json
import machine
import dht
from Persistence import Persistence
from LEDUtils import LEDUtils
import network
import ntptime
import usocket
import uasyncio

# load wlan config
with open('wlan_config.json') as w_conf:
    wlan_data = json.loads(w_conf.read())

    # Get time from Timeserver to handle persistence
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)  # activate the interface
    wlan.connect(wlan_data['name'], wlan_data['password'])  # connect to an AP

    for i in range(10):
        if wlan.isconnected():
            print("System time set")
            ntptime.settime()
            print(wlan.ifconfig())
            #wlan.disconnect()
            #wlan.active(False)
            break
        time.sleep(1)

# create socket for control
addr = usocket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = usocket.socket()
s.bind(addr)
s.listen(1)
s.settimeout(1)

# LED Inits
n = 256
dhtSensor = dht.DHT22(machine.Pin(26))

ledUtil = LEDUtils(n)
persistence = Persistence()

padding = 0

avgTmpBuff = [0, 0, 0, 0, 0]
avgHumBuff = [0, 0, 0, 0, 0]

count = 0
secCount = 0


matrix_mode = ''
req_mode = 'tmp'

while True:
    try:
        cl, addr = s.accept()
        req_path = str(cl.makefile('rwb', 0).readline()).split(' ')
        if len(req_path) > 1:
            print(req_path[1])
            req_path = req_path[1]
        cl.send('200')
        cl.close()

        if req_path.startswith('/matrix'):
            if req_path.endswith('/tmp'):
                req_mode = 'tmp'
            if req_path.endswith('/hum'):
                req_mode = 'hum'
    except OSError:
        pass

    try:
        dhtSensor.measure()
    except OSError as err:
        print(err)

    tmp = str(dhtSensor.temperature()) + '°C'
    hum = str(int(dhtSensor.humidity())) + '%'

    if padding >= 32:
        padding = 0

    # ledUtil.runningText(s.upper(), padding)

    if req_mode == 'tmp' and matrix_mode != 'tmp':
        matrix_mode = 'tmp'
        uasyncio.run(ledUtil.writeStringToMatrix(tmp))
        print('Selected TMP-Mode')
    elif req_mode == 'hum' and matrix_mode != 'hum':
        matrix_mode = 'hum'
        uasyncio.run(ledUtil.writeStringToMatrix(hum))
        print('Selected HUM-Mode')

    padding += 1

    if secCount == 120:
        avgTmpBuff[count] = dhtSensor.temperature()
        avgHumBuff[count] = dhtSensor.humidity()

        if count == 4:
            avgTmp = sum(avgTmpBuff) / 5
            avgHum = sum(avgHumBuff) / 5

            persistence.persistValue(avgTmp, avgHum)

            print("Temperature Buffer: " + ', '.join(map(str, avgTmpBuff)))
            print("Humidity Buffer: " + ', '.join(map(str, avgHumBuff)))
            print("Persisted Data!")  # Todo Timestamp?

            avgTmpBuff = [0] * 5
            avgHumBuff = [0] * 5
            count = 0
        else:
            count += 1
        secCount = 1

    else:
        secCount += 1

    time.sleep_ms(500)
