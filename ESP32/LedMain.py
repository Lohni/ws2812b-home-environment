import time
import machine
import dht
from Persistence import Persistence
from LEDUtils import LEDUtils
import uasyncio
import MatrixSocket


class LedMain:
    def __init__(self, mSocket: MatrixSocket):
        self.socket = mSocket
        self.dhtSensor = dht.DHT22(machine.Pin(26))
        self.ledUtil = LEDUtils(256)
        self.persistence = Persistence()
        self.matrix_mode = ''

    def run(self):
        try:
            self.socket.listen(self.persistence)

            try:
                self.dhtSensor.measure()
            except OSError as err:
                print("DHT-Measure error")

            tmp = str(self.dhtSensor.temperature()) + '°C'
            hum = str(int(self.dhtSensor.humidity())) + '%'

            if self.socket.req_mode == 'tmp' and self.matrix_mode != 'tmp':
                self.matrix_mode = 'tmp'
                uasyncio.run(self.ledUtil.writeStringToMatrix(tmp))
                print('Selected TMP-Mode')
            elif self.socket.req_mode == 'hum' and self.matrix_mode != 'hum':
                self.matrix_mode = 'hum'
                uasyncio.run(self.ledUtil.writeStringToMatrix(hum))
                print('Selected HUM-Mode')

            local_time = time.localtime(self.persistence.getCurrentMEZ())
            current_min = local_time[4]
            if current_min % 5 == 0 and current_min != self.persistence.last_persisted_minute:
                tmp = dht.temperature()
                hum = dht.humidity()
                self.persistence.persistValue(self.dhtSensor.temperature(), self.dhtSensor.humidity(), local_time)

                print("Temperature: " + tmp)
                print("Humidity: " + hum)
                print("Persisted Data!")  # Todo Timestamp?

            time.sleep_ms(1000)
        except Exception as err:
            pass
    # Todo: Error notification to Matrix, save error to file/ var?, error interface via http to see whats happening
