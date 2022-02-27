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

    async def persistValue(self, temperature: float, humidity: float, currDateMEZ: time):
        print(currDateMEZ)

        dataFile = open('sensorData.txt', 'ab+')

        matchOrder = ['yy:'.encode() + int(currDateMEZ[0]).to_bytes(2, 'big'),
                      'mm:'.encode() + int(currDateMEZ[1]).to_bytes(2, 'big'),
                      'dd:'.encode() + int(currDateMEZ[2]).to_bytes(2, 'big'),
                      'hh:'.encode() + int(currDateMEZ[3]).to_bytes(2, 'big')]

        while True:
            line = dataFile.read(5)
            if line.startswith(matchOrder[0]):
                break

            if line == ''.encode():
                dataFile.write('yy:'.encode() + int(currDateMEZ[0]).to_bytes(2, 'big'))
                print('Created Year entry')
                break

        while True:
            line = dataFile.read(5)
            if line.startswith(matchOrder[1]):
                break

            if line == ''.encode():
                dataFile.write('mm:'.encode() + int(currDateMEZ[1]).to_bytes(2, 'big'))
                print('Created Month entry')
                break

        while True:
            line = dataFile.read(5)
            if line.startswith(matchOrder[2]):
                break

            if line == ''.encode():
                dataFile.write('dd:'.encode() + int(currDateMEZ[2]).to_bytes(2, 'big'))
                print('Created Day entry')
                break

        while True:
            line = dataFile.read(5)
            if line.startswith(matchOrder[3]):
                break

            if line == ''.encode():
                dataFile.write('hh:'.encode() + int(currDateMEZ[3]).to_bytes(2, 'big'))
                print('Created Hour entry')
                break

        minuteEntryExists = False
        while True:
            line = dataFile.read(5)
            if line.startswith(int(currDateMEZ[4]).to_bytes(2, 'big') + ':'.encode()):
                minuteEntryExists = True
                break

            if line == ''.encode():
                break

        # Now we know that the Data-Structure exists -> save Data
        if not minuteEntryExists:
            data = self.sensorDataToBytes(temperature, humidity)
            dataFile.write(int(currDateMEZ[4]).to_bytes(2, 'big'))
            dataFile.write(':'.encode() + data)

        dataFile.close()

    def getDataByTimestamp(self, timestamp: []):
        dataFile = open('sensorData.txt', 'rb')

        matchOrder = ['yy:'.encode() + int(timestamp[0]).to_bytes(2, 'big'),
                      'mm:'.encode() + int(timestamp[1]).to_bytes(2, 'big'),
                      'dd:'.encode() + int(timestamp[2]).to_bytes(2, 'big'),
                      'hh:'.encode() + int(timestamp[3]).to_bytes(2, 'big')]

        dataTime = int(timestamp[4] / 5) * 5
        data = ''

        currentMtcIndex = 0

        line = dataFile.read(5)
        while data == '' and line[0] != ''.encode():
            if line.__contains__(matchOrder[currentMtcIndex]) and currentMtcIndex <= 3:
                currentMtcIndex += 1

            if currentMtcIndex == 4:
                if line.startswith(dataTime.to_bytes(2, 'big')):
                    data = line

            line = dataFile.read(5)

        dataFile.close()
        if data != '':
            return self.persistedBytesToValues(data.split(':'.encode(), 1)[1])

        return [0, 0]

    def decodeWholeFile(self):
        dataFile = open('sensorData.txt', 'rb')

        body = ''
        while True:
            line = dataFile.read(5).split(':'.encode())
            line_start = line[0].decode()

            if line_start == '':
                break

            if line_start.startswith('yy') or line_start.startswith('mm') \
                    or line_start.startswith('dd') or line_start.startswith('hh'):
                body = body + line_start + ':' + str(int.from_bytes(line[1], 'big')) + '\n'
            else:
                body = body + str(int.from_bytes(line[0], 'big')) + ':' + str(
                    self.persistedBytesToValues(line[1])) + '\n'

        dataFile.close()
        return body

    def overrideFile(self, data):
        dataFile = open('sensorData.txt', 'wb')

        buf = io.StringIO(data)
        while True:
            line = buf.readline().strip()

            if line == '':
                break

            line = line.split(':')
            if line[0].startswith('yy') or line[0].startswith('mm') or line[0].startswith('dd') or line[0].startswith(
                    'hh'):
                dataFile.write(line[0].encode() + ':'.encode() + int(line[1].strip()).to_bytes(2, 'big'))
            else:
                sensorData = line[1].replace('[', '').replace(']', '').replace(' ', '').split(',')
                dataFile.write((int(line[0]).to_bytes(2, 'big') + ':'.encode() + self.sensorDataToBytes(
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
