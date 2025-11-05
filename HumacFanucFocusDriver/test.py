from ctypes import *


fwlib = cdll.LoadLibrary("./lib/libfwlib32-linux-armv7.so.1.0.5")

print(fwlib)
