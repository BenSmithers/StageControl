from enum import Enum

class Status(Enum):
    OK = 0
    CommsTimeOut =1
    MechanicalTimeout = 2
    UnknownCommand = 3
    ValueOutOfRange=4
    ModuleIsolated=5
    ModuleOutOfIsolation=6
    InitializingError = 7
    ThermalErr=8
    Busy=9
    SensorError=10
    MotorError=11
    MechanicalOutofRange=12
    OverCurrent=13 


class ELLxBoardNotFound(Exception):
    pass 
class LEDNotFound(Exception):
    pass 
