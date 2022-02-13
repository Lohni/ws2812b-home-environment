import time
import uos as os
import io


class Persistence:
    def __init__(self):
        dataFileName = "sensorData.txt"
        if dataFileName not in os.listdir():
            x = open(dataFileName, 'x')
            x.close()
        print("Initialized Persistence.__init__()")

    def sensorDataToBytes(self, temp: float, humidity: float) -> bytes:
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

        return int(firstByte).to_bytes(1, 'big') + int(secondByte).to_bytes(1, 'big')

    def persistedBytesToValues(self, persistedBytes: bytes) -> [float, int]:
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

        # Todo: year/month/hour/day entry ints with to_bytes ---> TEST

        entryYear = 0
        while entryYear != currDateMEZ[0]:
            yearLine = dataFile.readline()
            if yearLine.startswith('year'.encode()):
                entryYear = int(yearLine.split(":".encode())[1])
            elif yearLine == ''.encode():
                dataFile.write('year:'.encode() + int(currDateMEZ[0]).to_bytes(2, 'big') + '\n'.encode())
                entryYear = currDateMEZ[0]
                print('Created Year entry')

        entryMonth = 0
        while entryMonth != currDateMEZ[1]:
            monthLine = dataFile.readline()
            if monthLine.startswith('month'.encode()):
                entryMonth = int(monthLine.split(":".encode())[1])
            elif monthLine == ''.encode():
                dataFile.write('month:'.encode() + int(currDateMEZ[1]).to_bytes(1, 'big') + '\n'.encode())
                entryMonth = currDateMEZ[1]
                print('Created Month entry')

        entryDay = 0
        while entryDay != currDateMEZ[2]:
            dayLine = dataFile.readline()
            if dayLine.startswith('day'.encode()):
                entryDay = int(dayLine.split(":".encode())[1])
            elif dayLine == ''.encode():
                dataFile.write('day:'.encode() + int(currDateMEZ[2]).to_bytes(1, 'big') + '\n'.encode())
                entryDay = currDateMEZ[2]
                print('Created Day entry')

        entryHour = 0
        while entryHour != currDateMEZ[3]:
            hourLine = dataFile.readline()
            if hourLine.startswith('hour'.encode()):
                entryHour = int(hourLine.split(":".encode())[1])
            elif hourLine == ''.encode():
                dataFile.write('hour:'.encode() + int(currDateMEZ[3]).to_bytes(1, 'big') + '\n'.encode())
                entryHour = currDateMEZ[3]
                print('Created Hour entry')

        # Now we know that the Data-Structure exists -> save Data
        minute_mark = int(currDateMEZ[4] / 5) * 5
        data = self.sensorDataToBytes(temperature, humidity)
        dataFile.write(minute_mark.to_bytes(1, 'big'))
        dataFile.write(':'.encode() + data + '\n'.encode())
        dataFile.close()

    def getDataByTimestamp(self, timestamp: []):
        dataFile = open('sensorData.txt', 'rb')

        matchOrder = ['year:'.encode() + int(timestamp[0]).to_bytes(2, 'big'),
                      'month:'.encode() + int(timestamp[1]).to_bytes(1, 'big'),
                      'day:'.encode() + int(timestamp[2]).to_bytes(1, 'big'),
                      'hour:'.encode() + int(timestamp[3]).to_bytes(1, 'big')]

        dataTime = int(timestamp[4] / 5) * 5
        data = ''

        currentMtcIndex = 0

        line = dataFile.readline()
        while data == '' and line != '':
            if line.__contains__(matchOrder[currentMtcIndex]) and currentMtcIndex <= 3:
                currentMtcIndex += 1

            if currentMtcIndex == 4:
                if int(line[0]) == dataTime:
                    data = line

            line = dataFile.readline()

        dataFile.close()
        if data != '':
            return self.persistedBytesToValues(data.split(':'.encode(), 1)[1])

        return [0, 0]

    def decodeWholeFile(self):
        dataFile = open('sensorData.txt', 'rb')

        body = ''
        while True:
            line = dataFile.readline()
            print(line)
            dec_line = line.decode()

            if dec_line == '':
                break

            if dec_line.startswith('year') or dec_line.startswith('month') \
                    or dec_line.startswith('day') or dec_line.startswith('hour'):
                line = line.split(':'.encode())
                body = body + line[0].decode() + str(int(line[1]))
            else:
                if len(dec_line) >= 4:
                    body = body + str(int(line[0])) + ':' + str(
                        self.persistedBytesToValues(line.split(':'.encode(), 1)[1])) + '\n'
                else:
                    body = body + str(self.persistedBytesToValues(line)) + '\n'

        dataFile.close()
        return body

    def overrideFile(self, data):
        dataFile = open('sensorData.txt', 'wb')

        buf = io.StringIO(data)
        while True:
            line = buf.readline()

            if line == '':
                break

            if line.startswith('year') or line.startswith('month') \
                    or line.startswith('day') or line.startswith('hour'):
                dataFile.write(line.encode())
            else:
                line = line.split(':')
                sensorData = line[1].replace('[', '').replace(']', '').replace(' ', '').split(',')
                dataFile.write((int(line[0]).to_bytes(1, 'big') + ':'.encode() + self.sensorDataToBytes(
                    float(sensorData[0]), int(sensorData[1]))))

        dataFile.close()
        print('Overwritten sensorData.txt')

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
