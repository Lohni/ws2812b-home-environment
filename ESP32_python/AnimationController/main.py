import neopixel
import machine
import time
import _thread

np = neopixel.NeoPixel(machine.Pin(2), 1000)
buf = [(0, 0, 0)] * 1000


#@micropython.native
def loop():
    f = np.__setitem__
    g = buf.__getitem__
    r = range(256)
    for i in r:
        it = g(i)
        f(i, it)

def loop1():
    r = range(256)
    f = loop
    for i in r:
        f()


def time_it(f):
    t1 = time.ticks_us()
    loop1()
    t2 = time.ticks_us()
    df = time.ticks_diff(t2, t1)
    fmt = '{:8.2f} k/sec'
    print(fmt.format(1000 / df * 1e3))


time_it()
