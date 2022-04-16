import network
import usocket
import json
import ntptime
import time
import machine
import Persistence


def wlanConnect():
    # load wlan config
    with open('wlan_config.json') as w_conf:
        wlan_data = json.loads(w_conf.read())

        # Get time from Timeserver to handle persistence
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)  # activate the interface
        wlan.connect(wlan_data['name'], wlan_data['password'])  # connect to an AP

        for i in range(10):
            if wlan.isconnected():
                print(wlan.ifconfig())
                # wlan.disconnect()
                # wlan.active(False)
                break
            time.sleep(1)

        if wlan.isconnected():
            ntptime.settime()
            print("System time set" + str(time.localtime()))

class MatrixSocket:

    def __init__(self):
        wlanConnect()
        addr = usocket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.sock = usocket.socket()
        self.sock.bind(addr)
        self.sock.listen(1)
        self.sock.settimeout(1)
        self.req_mode = ''

    def listen(self, persistence: Persistence):
        try:
            cl, addr = self.sock.accept()
            tmp = cl.makefile('rwb', 0)
            req_path = bytes(tmp.readline()).decode('UTF-8').split(' ')
            req_mode = ""
            content_length = 0

            reset = False

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

            if req_path[1].startswith('/python') and req_path[0] == 'POST':
                ret = self.overrideClass(req_path, body)
                cl.sendall('HTTP/1.1 ' + ret + '\r\n' +
                           'Content-Type:text/html; encoding=utf8\r\n' +
                           'Connection:close\r\n\r\n')

            if req_path[1].startswith('/reset'):
                cl.sendall('HTTP/1.1 ' + '200 OK' + '\r\n' +
                           'Content-Type:text/html; encoding=utf8\r\n' +
                           'Connection:close\r\n\r\n')
                reset = True

            cl.close()
            self.req_mode = req_mode

            if reset:
                machine.reset()
        except OSError:
            pass

    def overrideClass(self, req_path, body):
        targetClass = req_path[1].split('/')[2]

        try:
            file = open(targetClass + '.py', 'w')
            print(file)
            file.write(body)
            file.close()
        except Exception as err:
            print(err)
            return '500 Internal Error'

        return '200 OK'
