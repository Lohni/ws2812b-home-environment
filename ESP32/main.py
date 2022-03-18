import MatrixSocket
import LedMain
import time

# load wlan config
matrixSocket = MatrixSocket.MatrixSocket()
main = LedMain.LedMain(matrixSocket)

while True:
    main.run()
    time.sleep_ms(1000)