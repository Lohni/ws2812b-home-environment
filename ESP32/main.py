import MatrixSocket
import LedMain

# load wlan config
matrixSocket = MatrixSocket.MatrixSocket()
main = LedMain.LedMain(matrixSocket)

while True:
    main.run()