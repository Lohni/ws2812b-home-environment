import time
import uos as os


class Persistence:
    def __init__(self):
        dataFileName = "sensorData.txt"
        if dataFileName not in os.listdir():
            x = open(dataFileName, 'x')
            x.close()
        print("Initialized Persistence.__init__()")

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
