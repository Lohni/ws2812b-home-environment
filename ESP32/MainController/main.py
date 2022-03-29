import MatrixSocket
import mainController
import time

# load wlan config
matrixSocket = MatrixSocket.MatrixSocket()
main = mainController.MainController(matrixSocket)

while True:
    main.run()
    time.sleep(1)

