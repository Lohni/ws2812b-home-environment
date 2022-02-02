import time
import machine
import neopixel
import dht
import uos as os
import network
import ntptime

#
# 0  -  1  -  2
# |     |     |
# 3  -  4  -  5
# |     |     |
# 6  -  7  -  8
# |     |     |
# 9  -  10 -  11
# |     |     |
# 12 -  13 -  14
#

font = {
    "A": [1, 3, 5, 6, 7, 8, 9, 11, 12, 14],
    "B": [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    "C": [1, 2, 3, 6, 9, 13, 14],
    "D": [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "E": [0, 1, 2, 3, 6, 7, 8, 9, 12, 13, 14],
    "F": [0, 1, 2, 3, 6, 7, 8, 9, 12],
    "G": [0, 1, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    "H": [0, 2, 3, 5, 6, 7, 8, 9, 11, 12, 14],
    "I": [0, 1, 2, 4, 7, 10, 12, 13, 14],
    "J": [2, 5, 8, 9, 11, 12, 13, 14],
    "K": [0, 2, 3, 4, 6, 9, 10, 12, 14],
    "L": [0, 3, 6, 9, 12, 13, 14],
    "M": [0, 2, 3, 4, 5, 6, 8, 9, 11, 12, 14],
    "N": [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14],
    "O": [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "P": [0, 1, 2, 3, 5, 6, 7, 8, 9, 12],
    "Q": [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14],
    "R": [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 14],
    "S": [1, 2, 3, 7, 11, 12, 13],
    "T": [0, 1, 2, 4, 7, 10, 13],
    "U": [0, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "V": [0, 2, 3, 5, 6, 8, 9, 11, 13],
    "W": [0, 2, 3, 5, 6, 8, 9, 10, 11, 12, 14],
    "X": [0, 2, 3, 5, 7, 9, 11, 12, 14],
    "Y": [0, 2, 3, 5, 7, 10, 13],
    "Z": [0, 1, 2, 5, 7, 8, 9, 12, 13, 14],
    "1": [2, 5, 8, 11, 14],
    "2": [0, 1, 2, 5, 6, 7, 8, 9, 12, 13, 14],
    "3": [0, 1, 2, 5, 6, 7, 8, 11, 12, 13, 14],
    "4": [0, 3, 5, 6, 7, 8, 11, 14],
    "5": [0, 1, 2, 3, 6, 7, 8, 11, 12, 13, 14],
    "6": [0, 1, 2, 3, 6, 7, 8, 9, 11, 12, 13, 14],
    "7": [0, 1, 2, 5, 8, 11, 14],
    "8": [0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14],
    "9": [0, 1, 2, 3, 5, 6, 7, 8, 11, 12, 13, 14],
    "0": [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],
    "°": [1, 3, 5, 7],
    ".": [13],
    "%": [0, 5, 7, 9, 14]
}


class LEDUtils:
    def __init__(self, np: neopixel.NeoPixel, fontDir: {}):
        self.np = np
        self.fontDir = fontDir

    def writeStringToMatrix(self, s: str):
        self.np.fill((0, 0, 0))
        for pos, char in enumerate(s):
            seperator = True
            if s == '.':
                seperator = False

            position = self.fontDir.get(char)
            self.writeCharToMatrix(position, pos, seperator)

    def writeCharToMatrix(self, char: [], char_position, seperator: bool):
        # width of matrix : 32, char width : 3 + 1 padding
        # -> max. 8 fonts on matrix
        matrixWidth = 32
        startIndex = char_position * 3

        if seperator:
            # 1 led padding between letters
            startIndex += char_position

        for pos in char:
            if pos < 3:
                self.np[startIndex + pos] = (10, 5, 6)
            elif pos < 6:
                self.np[-startIndex + (matrixWidth * 2 - 1) + (3 - pos)] = (10, 5, 6)
            elif pos < 9:
                self.np[startIndex + (matrixWidth * 2) + (6 - pos) * -1] = (10, 5, 6)
            elif pos < 12:
                self.np[-startIndex + (matrixWidth * 4 - 1) + (9 - pos)] = (10, 5, 6)
            else:
                self.np[startIndex + (matrixWidth * 4) + (12 - pos) * -1] = (10, 5, 6)

    def runningText(self, s, padding):
        self.np.fill((0, 0, 0))
        matrixWidth = 32
        for char_position, letter in enumerate(s):
            char = self.fontDir.get(letter)

            startIndex = char_position * 3 + char_position + padding
            for pos in char:
                if pos < 3:
                    index = startIndex + pos
                    if index >= matrixWidth:
                        index = index - matrixWidth

                elif pos < 6:
                    index = -startIndex + (matrixWidth * 2 - 1) + (3 - pos)
                    if index < matrixWidth:
                        index = (matrixWidth * 2 - 1) - (matrixWidth - 1 - index)

                elif pos < 9:
                    index = startIndex + (matrixWidth * 2) + (6 - pos) * -1
                    if index >= matrixWidth * 3:
                        index = matrixWidth * 2 + (index - matrixWidth * 3)

                elif pos < 12:
                    index = -startIndex + (matrixWidth * 4 - 1) + (9 - pos)
                    if index < matrixWidth * 3:
                        index = (matrixWidth * 4 - 1) - (matrixWidth * 3 - 1 - index)

                else:
                    index = startIndex + (matrixWidth * 4) + (12 - pos) * -1
                    if index >= matrixWidth * 5:
                        index = matrixWidth * 4 + (index - matrixWidth * 5)

                self.np[index] = (10, 10, 10)


class Persistence:
    def sensorDataToBytes(self, temp: float, humidity: float) -> str:
        # Byte-Composition for Sensor-Data:
        # AAAABBBB | BCCCCCCC
        # A -> 4Bit for Temp. comma -> 0-9 / 16
        # B -> 5Bit for Temp. dezimal -> 0-32
        # C -> 7Bit for Humidity -> 0-100 / 128

        tDec = int(str(temp).split('.')[0])
        tComma = int(str(temp).split('.')[1][:1])
        humByte = int(humidity)

        decLSB = tDec & 1
        decRest = (tDec >> 1) & 0b00001111
        humCut = humByte & 0b01111111

        firstByte = (tComma << 4) | decRest
        secondByte = (decLSB << 7) | humCut

        return str(firstByte) + str(secondByte)

    def persistedBytesToValues(self, persistedBytes: str) -> [float, int]:
        firstByte = int(persistedBytes[0])
        secondByte = int(persistedBytes[1])

        tempComma = (firstByte >> 4) / 10
        tempDec = (secondByte >> 7) | ((firstByte & 0b00001111) << 1)
        humidity = secondByte & 0b01111111

        return [tempDec + tempComma, humidity]

    def persistValue(self, temperature: float, humidity: float):
        currDateMEZ = time.localtime(self.getCurrentMEZ())
        print(currDateMEZ)

        dataFile = open('sensorData.txt', 'ab+')

        entryYear = 0
        while entryYear != currDateMEZ[0]:
            yearLine = str(dataFile.readline().decode())
            if yearLine.startswith('year'):
                entryYear = int(yearLine.split(":")[1])
            elif yearLine == '':
                dataFile.write(('year:' + str(currDateMEZ[0]) + '\n').encode())
                entryYear = currDateMEZ[0]
                print('Created Year entry')

        entryMonth = 0
        while entryMonth != currDateMEZ[1]:
            monthLine = str(dataFile.readline().decode())
            if monthLine.startswith('month'):
                entryMonth = int(monthLine.split(":")[1])
            elif monthLine == '':
                dataFile.write(('month:' + str(currDateMEZ[1]) + '\n').encode())
                entryMonth = currDateMEZ[1]
                print('Created Month entry')

        entryDay = 0
        while entryDay != currDateMEZ[2]:
            dayLine = str(dataFile.readline().decode())
            if dayLine.startswith('day'):
                entryDay = int(dayLine.split(":")[1])
            elif dayLine == '':
                dataFile.write(('day:' + str(currDateMEZ[2]) + '\n').encode())
                entryDay = currDateMEZ[2]
                print('Created Day entry')

        entryHour = 0
        while entryHour != currDateMEZ[3]:
            hourLine = str(dataFile.readline().decode())
            if hourLine.startswith('hour'):
                entryHour = int(hourLine.split(":")[1])
            elif hourLine == '':
                dataFile.write(('hour:' + str(currDateMEZ[3]) + '\n').encode())
                entryHour = currDateMEZ[3]
                print('Created Hour entry')

        # Now we know that the Data-Structure exists -> save Data

        data = self.sensorDataToBytes(temperature, humidity)
        dataFile.write((data + '\n').encode())
        dataFile.close()

    def readPersistedValue(self):
        pass

    def getCurrentMEZ(self):
        # Austria-MESZ between:
        # Last March-Sunday at 02:00 MEZ
        # Last Oktober-Sunday at 03:00 MESZ
        mez = (time.time() + 3600)
        t = time.localtime(mez)
        month = t[1]
        day = t[2]

        if 3 <= month <= 10:
            if month == 3:
                lastSunday = self.getLastSundayOfMonth(mez)
                if day > lastSunday or (day == lastSunday and t[3] >= 2):
                    mez = mez + 3600
            elif month == 10:
                mest = mez + 3600
                tmest = time.localtime(mest)
                lastSunday = self.getLastSundayOfMonth(mest)
                if tmest[2] < lastSunday or (tmest[2] == lastSunday and tmest[3] < 3):
                    mez = mez + 3600
            else:
                mez = mez + 3600

        return mez

    def getLastSundayOfMonth(self, mez) -> int:
        t = time.localtime(mez)
        currDay = t[2]
        diff = 0

        if t[1] == 3 or t[1] == 10:
            diff = 31 - currDay

        eomTime = mez + (3600 * 24 * diff)
        eom = time.localtime(eomTime)
        weekDay = eom[6]
        diffToPrevSunday = 7 - (6 - weekDay)

        lastSunday = eom[2]
        if diffToPrevSunday < 7:
            lastSunday = time.localtime(eomTime - (3600 * 24 * diffToPrevSunday))[2]

        return lastSunday


# Get time from Timeserver to handle persistence
wlan = network.WLAN(network.STA_IF)
wlan.active(True)  # activate the interface
wlan.connect('PBS-3ADBF1', 'BbK1dBhg2wwgKb3dmh7S4')  # connect to an AP

for i in range(10):
    if wlan.isconnected():
        print("System time set")
        ntptime.settime()
        wlan.disconnect()
        wlan.active(False)
        break
    time.sleep(1)

# LED Inits
n = 256
np = neopixel.NeoPixel(machine.Pin(2), n)
dhtSensor = dht.DHT22(machine.Pin(26))
ledUtil = LEDUtils(np, font)

dataFileName = "sensorData.txt"

if dataFileName not in os.listdir():
    x = open(dataFileName, 'x')
    x.close()

persistence = Persistence()

padding = 0

avgTmpBuff = [0, 0, 0, 0, 0]
avgHumBuff = [0, 0, 0, 0, 0]

count = 0
secCount = 0
while True:
    dhtSensor.measure()
    tmp = str(dhtSensor.temperature()) + '°C'
    hum = str(int(dhtSensor.humidity())) + '%'

    if padding >= 32:
        padding = 0

    # ledUtil.runningText(s.upper(), padding)
    ledUtil.writeStringToMatrix(tmp)

    np.write()
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
