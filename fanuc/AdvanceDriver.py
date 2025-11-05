from pyfocas.Collector import Collector
import os
from pyfocas.Machine import Machine
from FanucImplementation.DriverImplementations import Fanuc30iDriver
from pyfocas import Exceptions
import logging

logging.basicConfig(level=logging.INFO)

class AdvanceDriver:
    def __init__(self,lib_path):
        self.lib_path = lib_path
        if not os.path.exists(self.lib_path):
            logging.error(f"Library not found at {self.lib_path}")
            exit(1)
        else:
            logging.info(f"Loading library from {self.lib_path}")
        
    def connecte(self,):
         logging.info("Creating Fanuc30iDriver instance")
         driver30i = Fanuc30iDriver(self.lib_path,extradlls=["./lib/fwlibe64.dll"])
         
         logging.info("Creating Machine instance")
         machine1 = Machine(driver=driver30i, ip="192.168.0.3", name="316")
         logging.info(f"machine created: {machine1}")