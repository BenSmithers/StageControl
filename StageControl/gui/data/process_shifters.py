import os 
from datetime import datetime 
import calendar
_out = os.path.join(os.path.dirname(__file__),"shifter_data.csv")
_in = os.path.join(os.path.dirname(__file__),"shifter_data_raw.csv")

infile = open(_in, 'rt')
lines = infile.readlines()
infile.close()

_obj = open(_out, 'wt')
for i, line in enumerate(lines):
    if i==0:
        continue

    data = line.split(",")
    time_base_raw = data[0].split("-")
    time_shift1 = datetime(2024, 10 if time_base_raw[1]=="Oct" else 11, day=int(time_base_raw[0]),hour=5)
    time_shift2 = datetime(2024, 10 if time_base_raw[1]=="Oct" else 11, day=int(time_base_raw[0]),hour=13)
    time_shift3 = datetime(2024, 10 if time_base_raw[1]=="Oct" else 11, day=int(time_base_raw[0]),hour=21)

    _obj.write("{}, {}, {}\n".format(
        calendar.timegm(time_shift1.timetuple()), "" if "#N/A" in data[1] else data[1], "" if "#N/A" in data[2] else data[2] 
    ))
    _obj.write("{}, {}, {}\n".format(
        calendar.timegm(time_shift2.timetuple()), "" if "#N/A" in data[3] else data[3], "" if "#N/A" in data[4] else data[4] 
    ))
    _obj.write("{}, {}, {}".format(
        calendar.timegm(time_shift3.timetuple()), "" if "#N/A" in data[5] else data[5],"\n" if "#N/A" in data[6] else  data[6] 
    ))
_obj.close()