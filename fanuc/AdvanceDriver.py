from pyfocas.Collector import Collector
from ctypes import *
from pyfocas.Machine import Machine
from FanucImplementation.DriverImplementations import Fanuc30iDriver
from pyfocas import Exceptions
import time
import logging

logging.basicConfig(level=logging.INFO)

class AdvanceDriver:
    def __init__(self,lib_path):
        self.lib_path = lib_path
        self.machine1= None
        # try:
        #     self.fwlib = cdll.LoadLibrary(self.lib_path)
        #     logging.info("Library loaded successfully")
        # except Exception as e:
        #     logging.error(f"Failed to load library: {e}")
        # if not os.path.exists(self.lib_path):
        #     logging.error(f"Library not found at {self.lib_path}")
        # else:
        #     logging.info(f"Loading library from {self.lib_path}")
        
    def connecte(self,):
         logging.info("Creating Fanuc30iDriver instance")
        #  self.fwlib.cnc_startupprocess.restype = c_short
        #  self.fwlib.cnc_startupprocess.argtypes = [c_short, c_char_p]
        #  log_file = b"focas.log"
        #  init_ret = self.fwlib.cnc_startupprocess(3, log_file)
        #  logging.info(f"FOCAS initialization result: {init_ret}")  # 0 = success
        #  if init_ret != 0:
        #    logging.error(f"FOCAS init failed with code: {init_ret}")

        #  self.fwlib.cnc_allclibhndl3.restype = c_short
        #  logging.info("Setting argument types for cnc_allclibhndl3")
        #  self.fwlib.cnc_allclibhndl3.argtypes = [
        #         c_char_p,     # IP address
        #         c_ushort,     # Port
        #         c_short,      # Timeout
        #         POINTER(c_ushort)  # Output handle
        #     ]
        #  logging.info("Preparing connection parameters")
        #  cnc_ip = b"192.168.1.100"
        #  port = 8193
        #  timeout = 10
        #  libh = c_ushort(0)
        #  logging.info(f"Connecting to {cnc_ip.decode()}:{port} with timeout {timeout}")
        #  ret = self.fwlib.cnc_allclibhndl3(cnc_ip, port, timeout, byref(libh))
        #  logging.info(f"Connection result: {ret}, Handle: {libh.value}")
      
         driver30i = Fanuc30iDriver(self.lib_path,extradlls=["./lib/fwlibe64.dll"])
         
         logging.info("Creating Machine instance")
         try:
            self.machine1 = Machine(driver=driver30i, ip="192.168.0.3", name="316")
            for i in range(10):
                data = self.machine1.createDatum()
                logging.info(f"Machine connected successfully: {data}")
                time.sleep(0.5)
         except Exceptions.FocasConnectionException as e:
            logging.error(f"Failed to create Machine: {e}")
    
    def disconnect(self):
        if self.machine1 is not None:
            self.machine1.disconnect()