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


async def persistenceCounter(dht: dht.DHT22):
    await uasyncio.sleep(10)
    tmp = dht.temperature()
    hum = dht.humidity()
    # persistence.persistValue(dhtSensor.temperature(), dhtSensor.humidity())

    print("Temperature: " + tmp)
    print("Humidity: " + hum)
    print("Persisted Data!")  # Todo Timestamp?


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
            # wlan.disconnect()
            # wlan.active(False)
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

matrix_mode = ''
req_mode = 'tmp'

while True:
    try:
        cl, addr = s.accept()
        tmp = cl.makefile('rwb', 0)
        req_path = bytes(tmp.readline()).decode('UTF-8').split(' ')

        content_length = 0
        while True:
            line = bytes(tmp.readline()).decode('UTF-8')
            if line.startswith('Content-Length'):
                content_length = int(line.split(':')[1].strip(' '))
            if line == '\r\n':
                break

        body = bytes(tmp.read(content_length)).decode('UTF-8')

        print(req_path)
        if req_path[1].startswith('/matrix'):
            if req_path[1].endswith('/tmp'):
                req_mode = 'tmp'
            if req_path[1].endswith('/hum'):
                req_mode = 'hum'

        if req_path[1].startswith('/storage'):
            print(req_path[0])
            if req_path[0] == 'GET':
                msg = persistence.decodeWholeFile()
                cl.sendall('HTTP/1.1 200 OK\r\n' +
                           'Content-Type:text/html; encoding=utf8\r\n' +
                           'Content-Length:' + str(len(msg)) + '\r\n' +
                           'Connection:close\r\n\r\n' +
                           msg)

            if req_path[0] == 'POST':
                persistence.overrideFile(body)

                cl.sendall('HTTP/1.1 200 OK\r\n' +
                           'Content-Type:text/html; encoding=utf8\r\n' +
                           'Connection:close\r\n\r\n')

        cl.close()
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

    time.sleep_ms(1000)

# Todo: Error notification to Matrix, save error to file?, error interface via http to see whats happening
