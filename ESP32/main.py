import MatrixSocket
import LedMain
import uasyncio
import _thread
import time

from LEDUtils import LEDUtils

sLock = _thread.allocate_lock()

# load wlan config
matrixSocket = MatrixSocket.MatrixSocket()
main = LedMain.LedMain(matrixSocket)

def animateMatrixThread():
    while True:
        main.ledUtil.animateTxt()
        time.sleep_ms(50)

_thread.start_new_thread(animateMatrixThread, ())

while True:
    sLock.acquire()
    main.run()
    sLock.release()
    time.sleep(1)

