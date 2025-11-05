from pyfocas.Exceptions import FocasConnectionException
import logging
logging.basicConfig(level=logging.INFO)
import time

class Machine(object):
    def __init__(self, driver, ip, port=8193, name=None):
        self.name = name if name is not None else ip
        self.ip = ip
        self.port = port
        self.driver = driver
        self.handle = None
        self.connecte()
        # try:
        #     self.handle = self.driver.connect(ip, port)
        # except Exception as e:
        #     logging.error(f"Failed to connect to machine {self.name} at {self.ip}:{self.port} - {e}")
        #     raise
    def connecte(self):
        try:
            self.handle = self.driver.connect(self.ip, self.port)
        except FocasConnectionException as e:
            logging.info('try to connecte again')
            time.sleep(2)
            self.connecte()
    def createDatum(self):
        data = self.driver.poll(self.handle)
        data["machineName"] = self.name
        return data

    def reconnect(self):
        while True:
            try:
                self.handle = self.driver.reconnect(handle=self.handle,
                                                    ip=self.ip,
                                                    port=self.port)
                break
            except FocasConnectionException:
                logging.info("Reconnecting to machine: %s at %s"
                             % (self.name, self.ip))
    def disconnect(self):
        if self.handle is not None:
            self.driver.disconnect(self.handle)
            self.handle = None