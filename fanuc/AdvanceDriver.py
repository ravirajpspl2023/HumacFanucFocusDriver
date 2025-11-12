from pyfocas.Collector import Collector
from ctypes import *
from pyfocas.Machine import Machine
from FanucImplementation.DriverImplementations import Fanuc30iDriver
from pyfocas import Exceptions
import paho.mqtt.client as mqtt
import json
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdvanceDriver:
    def __init__(self,lib_path):
        self.lib_path = lib_path
        self.machine1= None
        self.connected = False
        self.running = True
        self.broker = "localhost"
        self.port = 1883
        self.telemetry_topic = "pspl-iot/telemetry_cnc"
        self.previous_tool_group = None
        # try:
        #     self.fwlib = cdll.LoadLibrary(self.lib_path)
        #     logging.info("Library loaded successfully")
        # except Exception as e:
        #     logging.error(f"Failed to load library: {e}")
        # if not os.path.exists(self.lib_path):
        #     logging.error(f"Library not found at {self.lib_path}")
        # else:
        #     logging.info(f"Loading library from {self.lib_path}")

    def _client_connect(self):
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="tool_life",
            clean_session=True,
            reconnect_on_failure=True
        )
        self.client.reconnect_delay_set(1,15)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        try:
            self.client.connect(self.broker, self.port, keepalive=15)
        except Exception as e:
            logging.error(f"Connection attempt failed: {e}")
            raise
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.connected = True
            logging.info(f"{self.broker} is connected")
        else:
            logging.error(f"Failed to connect server mqtt return code {reason_code} {self.broker}")

    def on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        logging.warning(f"Disconnected from server MQTT broker {self.broker}")
        self.connected = False
    
    def publish_data(self,data):
        if not self.connected:
            return
        json_data = json.dumps(data)
        result = self.client.publish(self.telemetry_topic,json_data,qos=1)
        result.wait_for_publish()

        
    def connecte(self,):
         logging.info("Creating Fanuc30iDriver instance")      
         driver30i = Fanuc30iDriver(self.lib_path,extradlls=["./lib/fwlibe64.dll"])   
         try:
            self.machine1 = Machine(driver=driver30i, ip="192.168.0.1", name="316")
            self._client_connect()
            self.client.loop_start()
            while self.running:
                # data = self.machine1.get_tool_info()
                data = self.machine1.createDatum()
                logging.info(f"Machine connected successfully: {data}")
                # if data.get("state",{}).get("data",{}).get("group","") != self.previous_tool_group:
                #     self.previous_tool_group = data.get("state",{}).get("data",{}).get("group","")
                #     self.publish_data(data)
                time.sleep(0.5)
         except Exceptions.FocasConnectionException as e:
            logging.error(f"Failed to create Machine: {e}")
         except Exception as e:
             logging.error(e)
             
    
    def disconnect(self):
        if self.machine1 is not None:
            self.machine1.disconnect()
        if self.client is not None :
             if self.client.is_connected() == False:
                 self.client.disconnect()
        self.running = False




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