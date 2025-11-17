from ctypes import *
import ctypes

from pyfocas.Driver import FocasDriverBase
from pyfocas.Exceptions import FocasExceptionRaiser
from .Fwlib32_h import *
from time import time_ns
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

AUTO_LABELS = ["MDI", "AUTO", "AUTO", "EDIT", "AUTO", "MANUAL", "MANUAL"]
RUN_LABELS = ["STOPPED", "READY (WAITING)", "FEED HOLD", "ACTIVE", "ACTIVE"]

gBlockString = ""


class Fanuc30iDriver(FocasDriverBase):
    ip = ""
    port = 0
    timeout = 0

    def connect(self, ip, port, timeout=10):
        try:
            self.dll.cnc_startupprocess.restype = c_short
            self.dll.cnc_startupprocess.argtypes = [c_short, c_char_p]
            log_file = b"focas.log"
            init_ret = self.dll.cnc_startupprocess(3, log_file)
            logging.info(f"FOCAS initialization result: {init_ret}")  # 0 = success
            if init_ret != 0:
                logging.error(f"FOCAS init failed with code: {init_ret}")
            func = self.dll.cnc_allclibhndl3

            func.argtypes = [
                c_char_p,           # IP address (string)
                c_ushort,           # Port number
                c_long,             # Timeout
                ctypes.POINTER(c_ushort)  # Handle pointer
            ]
            func.restype = c_short
            
            ip_bytes = ip.encode('utf-8')
            handle = c_ushort(0)
            
            # logging.info(f"Connecting to {ip}:{port} with timeout {timeout}")
            
            result = func(ip_bytes, port, timeout, byref(handle))
            logging.info(f"Connection result: {result}, Handle: {handle.value}")
            
            FocasExceptionRaiser(result, context=self)
            
            self.ip = ip
            self.port = port
            self.timeout = timeout
            return handle.value
            
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise

    def disconnect(self, handle):
        self.dll.cnc_freelibhndl(handle)

    def registerPollMethods(self):
        # there has GOT to be a way to do this with a decorator
        self.addPollMethod(self.getProgramName)
        self.addPollMethod(self.getBlockNumber)
        self.addPollMethod(self.getActiveTool)
        self.addPollMethod(self.getControlStatus)
        self.addPollMethod(self.getPMCValues)
        self.addPollMethod(self.getServoAndAxisLoads)
        self.addPollMethod(self.getAlarmStatus)
        self.addPollMethod(self.getCurrentBlock)
        # self.addPollMethod(self.getToolLifeData)

    def getProgramName(self, handle):
        data = {"time":time_ns() // 1_000_000}
        func = self.dll.cnc_exeprgname
        func.restype = c_short
        executingProgram = ExecutingProgram()
        result = func(handle, byref(executingProgram))
        FocasExceptionRaiser(result, context=self)
        data["programName"] = executingProgram.name
        data["oNumber"] = executingProgram.oNumber
        return data

    def getBlockNumber(self, handle):
        data = {"time":time_ns() // 1_000_000}
        dynamic = DynamicResult()
        func = self.dll.cnc_rddynamic2
        func.restype = c_short
        result = func(handle,
                      -1,
                      sizeof(DynamicResult),
                      byref(dynamic))
        FocasExceptionRaiser(result, context=self)
        data["blockNumber"] = dynamic.sequenceNumber
        return data

    def getActiveTool(self, handle):
        data = {"time":time_ns() // 1_000_000}
        func = self.dll.cnc_modal
        func.restype = c_short
        modalData = ModalData()
        result = func(handle, 108, 1, byref(modalData))
        FocasExceptionRaiser(result, context=self)
        data["activeTool"] = modalData.modal.aux.aux_data
        return data

    def getControlStatus(self, handle):
        data = {"time":time_ns() // 1_000_000}
        func = self.dll.cnc_statinfo
        func.restype = c_short
        statInfo = StatInfo()
        result = func(handle, byref(statInfo))
        FocasExceptionRaiser(result, context=self)
        try:
            data["autoMode"] = AUTO_LABELS[statInfo.auto]
        except IndexError:
            data["autoMode"] = statInfo.auto

        try:
            data["runStatus"] = RUN_LABELS[statInfo.run]
        except IndexError:
            data["runStatus"] = statInfo.run

        data["isEditing"] = bool(statInfo.edit)
        return data

    def getPMCValues(self, handle):
        """
        Checks the PMC addresses and returns
        their values from the control.
        """
        """ getPMCfunc is the ctypes function imported
            from the dll.                          """
        data = {"time":time_ns() // 1_000_000}
        getPMCfunc = self.dll.pmc_rdpmcrng
        getPMCfunc.restype = c_short
        """ length = 9 is a hardcoded value from the
            vendor's documentation.                """
        length = 9
        pmcAddresses = {"Fovr": 12,
                        "Sovr": 30}
        for pmcName in pmcAddresses:
            pmcAddress = pmcAddresses[pmcName]
            pmcdata = PMC()
            result = getPMCfunc(handle,
                                0,
                                0,
                                pmcAddress,
                                pmcAddress,
                                length,
                                byref(pmcdata))
            FocasExceptionRaiser(result, context=self)
            data[pmcName] = pmcdata.data.pmcValue
        return data

    def getServoAndAxisLoads(self, handle):
        data = {"time":time_ns() // 1_000_000}
        getServoLoadFunc = self.dll.cnc_rdspmeter
        getServoLoadFunc.restype = c_short
        num = c_short(MAX_AXIS)
        loads = (SpindleLoad * MAX_AXIS)()
        result = getServoLoadFunc(handle, 0, byref(num), loads)
        FocasExceptionRaiser(result, context=self)
        # lambda to calculate the actual spindle load value
        spload = lambda s: s.load.data / pow( 10.0, s.load.decimal)
        loads = {s.load.name : spload(s) for s in loads if s.load.name != "\x00" }
        # TODO: add in axis loads
        getAxisLoadFunc = self.dll.cnc_rdsvmeter
        getAxisLoadFunc.restype = c_short
        axloads = (ServoLoad * MAX_AXIS)()
        num = c_short(MAX_AXIS)
        result = getAxisLoadFunc(handle, byref(num), axloads)
        FocasExceptionRaiser(result, context=self)
        axloads = {s.load.name : spload(s) for s in axloads if s.load.name != "\x00"}
        loads.update(axloads)
        data['loads']= loads 
        return data

    def getAlarmStatus(self, handle):
        data = {"time": time_ns() // 1_000_000}
        getAlarmStatusFunc = self.dll.cnc_alarm
        getAlarmStatusFunc.restype = c_short
        alarm_data = AlarmStatus()
        result = getAlarmStatusFunc(handle, byref(alarm_data))
        FocasExceptionRaiser(result, context=self)
        alarm_data = alarm_data.data
        logging.info(f'this is alarm code : {alarm_data}')
        data["alarm"] = alarmStringBuilder(alarm_data=alarm_data)
        return data

    def getCurrentBlock(self, handle):
        data = {"time":time_ns() // 1_000_000}
        global gBlockString
        getCurrentBlockFunc = self.dll.cnc_rdexecprog
        getCurrentBlockFunc.restype = c_short
        blockstring = (c_char * 255)()
        blocklength = c_ushort(255)
        blocknumber = c_short(0)
        result = getCurrentBlockFunc(handle, byref(blocklength),
                                     byref(blocknumber), blockstring)
        FocasExceptionRaiser(result, context=self)
        if blockstring.value is not gBlockString:
            data["currentBlock"] = blockstring.value
            gBlockString = blockstring.value

        return data
    
    def getToolLifeData(self, handle):
        """
        Reads tool life data for the currently active tool.
        Returns tool number, group, used life, max life, and remaining.
        """
        data = {"time": time_ns() // 1_000_000}
        odb = ODBTG()
        length = ctypes.sizeof(ODBTG)
        
        result = self.dll.cnc_rdtoolgrp( handle,0,length,byref(odb))
        FocasExceptionRaiser(result, context=self)
        # if odb.grp_num == 13:
        logging.info(f"Group: {odb.grp_num}")
        data["state"]['data']["group"] = odb.grp_num
        data["state"]['data']["max_life"] = odb.life
        data["state"]['data']["tool_life_count"] = odb.count
        data["state"]['data']["tool_in_group"] = odb.ntool

        # logging.info(f"Max Life: {odb.life}, Used: {odb.count}")
        # logging.info(f"Tools in group: {odb.ntool}")
        # if odb.life == odb.count :
        #     logging.info("ToolLife is Over")
            # logging.info(f'{self.getAlarmStatus()}')
        
        for i in range(odb.ntool):
            t = odb.data[i]
            data["state"]['data']["tool"] = t.tool_num
            # logging.info(f"  [{t.tuse_num}] T{t.tool_num} | L:{t.length_num} R:{t.radius_num} Info:{t.tinfo}")
        return data

def alarmStringBuilder(alarm_data):
    alarms = []
    if alarm_data & DATAIO_ALARM_MASK:
        alarms.append("DATAIO")
    if alarm_data & SERVO_ALARM_MASK:
        alarms.append("SERVO")
    if alarm_data & MACRO_ALARM_MASK:
        alarms.append("MACRO")
    if alarm_data & OVERHEAT_ALARM_MASK:
        alarms.append("OVERHEAT")
    if alarm_data & OVERTRAVEL_ALARM_MASK:
        alarms.append("OVERTRAVEL")
    if alarm_data & SPINDLE_ALARM_MASK:
        alarms.append("SPINDLE")

    return alarms
