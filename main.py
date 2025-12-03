import os
import logging
from fanuc.AdvanceDriver import AdvanceDriver
from pyfocas.Collector import Collector
from pyfocas.Machine import Machine
from FanucImplementation.DriverImplementations import Fanuc30iDriver
from pyfocas import Exceptions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    lib_path = "./lib/libfwlib32-linux-armv7.so.1.0.5"
    advancDriver = AdvanceDriver(lib_path)
    advancDriver.connecte()
    try:
        while True:
            pass
    except (Exception, KeyboardInterrupt) as e:
        logging.info('stop main funaction')
        advancDriver.disconnect()

if __name__ == "__main__":
    main()

# import logging
# import ctypes

# def main():
#     lib_path = "./lib/libfwlib32-linux-armv7.so.1.0.5"
#     try:
#         # Use CDLL for Linux
#         focas_lib = ctypes.CDLL(lib_path)
#         logging.info("Library loaded successfully")
#     except Exception as e:
#         logging.error(f"Failed to load library: {e}")
#         exit(1)
#     # focas_lib.cnc_allclibhndl3.argtypes = [ctypes.c_char_p, ctypes.c_ushort, ctypes.c_long, ctypes.POINTER(ctypes.c_ushort)]
#     # focas_lib.cnc_allclibhndl3.restype = ctypes.c_short

#     # Example connection parameters
#     ip = b"192.168.1.1"  # Replace with your CNC IP
#     port = 8193
#     timeout = 10
#     handle = ctypes.c_ushort()

#     # Call the function
#     result = focas_lib.cnc_allclibhndl3(ip, port, timeout, ctypes.byref(handle))

#     if result == 0:
#         logging.info(f"Connected! Handle: {handle.value}")
#     else:
#         logging.error(f"Connection failed. Error code: {result}")

# if __name__ == "__main__":
#     main()