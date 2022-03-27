import time
import machine
import dht
from Persistence import Persistence
from LEDUtils import LEDUtils
import MatrixSocket


class LedMain:
    def __init__(self, mSocket: MatrixSocket):
        self.socket = mSocket
        self.dhtSensor = dht.DHT22(machine.Pin(26))
        self.ledUtil = LEDUtils(256)
        self.persistence = Persistence()
        self.matrix_mode = 'tmp'
        self.compare_interval_min = 5
        self.last_compare_value = [0, 0, 0]  # [tmp, hum, min]

    def run(self):
        try:
            self.socket.listen(self.persistence)

            try:
                self.dhtSensor.measure()
                print(self.dhtSensor.temperature())
            except OSError as err:
                print("DHT-Measure error")

            local_time = time.localtime(self.persistence.getCurrentMEZ())

            tmp = str(self.dhtSensor.temperature()) + '°C'
            hum = str(int(self.dhtSensor.humidity())) + '%'

            if self.socket.req_mode == 'tmp' and self.matrix_mode != 'tmp':
                self.matrix_mode = 'tmp'
                print('Selected TMP-Mode')
            elif self.socket.req_mode == 'hum' and self.matrix_mode != 'hum':
                self.matrix_mode = 'hum'
                print('Selected HUM-Mode')

            # Set Color
            if self.matrix_mode == 'tmp':
                comparison_timestamp = local_time
                tmp_color = (10, 5, 6)

                last_comp_val = self.last_compare_value[2] + 5
                if last_comp_val == 60:
                    last_comp_val = 0

                if comparison_timestamp[4] % 5 == 0 and last_comp_val < comparison_timestamp[4] \
                        or self.last_compare_value[0] == 0 or 0 == comparison_timestamp[4] and self.last_compare_value[2] == 50:
                    instant = time.mktime(comparison_timestamp) - (comparison_timestamp[4] % 5) * 60

                    if self.last_compare_value[0] != 0:
                        instant = instant - 5 * 60

                    comparison_data = self.persistence.getDataByTimestamp(time.localtime(instant))

                    if len(comparison_data) > 0:
                        self.last_compare_value[0] = comparison_data[0]
                        self.last_compare_value[1] = comparison_data[1]
                        self.last_compare_value[2] = time.localtime(instant)[4]
                    else:
                        self.last_compare_value[0] = self.dhtSensor.temperature()
                        self.last_compare_value[2] = time.localtime(instant)[4]

                print('LastCompareVal:' + str(self.last_compare_value))
                diff = self.last_compare_value[0] - self.dhtSensor.temperature()
                if diff > 0:
                    tmp_color = (2, 2, 10)
                elif diff < 0:
                    tmp_color = (10, 2, 2)
                # Todo: calc color hues https://www.colorspire.com/rgb-color-wheel/

                print(tmp_color)
                self.ledUtil.color = tmp_color
                self.ledUtil.writeStringToMatrix(tmp)

            current_min = local_time[4]
            print(str(current_min) + ' ... ' + str(self.persistence.last_persisted_minute))
            if current_min % 5 == 0 and current_min != self.persistence.last_persisted_minute:
                tmp = self.dhtSensor.temperature()
                hum = self.dhtSensor.humidity()
                self.persistence.persistValue(tmp, hum, local_time)

                print("Temperature: " + str(tmp))
                print("Humidity: " + str(hum))
                print("Persisted Data!")  # Todo Timestamp?

        except Exception as err:
            print(err)
            pass
    # Todo: Error notification to Matrix, save error to file/ var?, error interface via http to see whats happening
