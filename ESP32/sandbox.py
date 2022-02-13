i = [21.8, 21.6, 21.9, 21.2, 21.3]
i = 20.5
j = 40

# Byte-Composition for Sensor-Data:
# AAAABBBB | BCCCCCCC
# A -> 4Bit for Temp. comma -> 0-9 / 16
# B -> 5Bit for Temp. dezimal -> 0-32
# C -> 7Bit for Humidity -> 0-100 / 128

iDec = int(str(i).split('.')[0])
iComma = int(str(i).split('.')[1][:1])
jBytes = int(j)

decLSB = iDec & 1
decRest = (iDec >> 1) & 0b00001111
humCut = jBytes & 0b01111111

firstByte = (iComma << 4) | decRest
secondByte = (decLSB << 7) | humCut

print("FirstByte: " + str(firstByte) + " : " + format(firstByte, 'b'))
print("SecondByte: " + str(secondByte) + " : " + format(secondByte, 'b'))

#firstByte = 1066
#secondByte = 168

# Reverse
tempComma = (firstByte >> 4) / 10
tempDec = (secondByte >> 7) | ((firstByte & 0b00001111) << 1)
humidity = secondByte & 0b01111111

print("Temp: " + str(tempDec+tempComma))
print("Humidity: " + str(humidity))