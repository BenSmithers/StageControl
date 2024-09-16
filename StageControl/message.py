# data are in ascii format and in hexadecimal notation 

"""
req status gs
ho home 
get position po  or gp 
move absolute ma
moverelative mr 
set home offset so
get home offset go 


"""
from enum import Enum 


def _all_subclasses(cls:'Response'):
    """
        Returns either a list of the names of all subclasses of `cls`, or a list of the classes themselves
    """

    return list(set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in _all_subclasses(c)]))

def _get_message_map()->'dict[str,Response]':
    all_responses = _all_subclasses(Response)
    return {
        entry.key:entry for entry in all_responses
    }

def response_handler(full_response:bytes):
    """
        First, build a map of the known responses 
        Check this response type against the map
        And call the relevant Response decoder
    """
    print("Received:  ", full_response.decode())
    message_map = _get_message_map()
    this_key = full_response[1:3].decode()

    if this_key not in message_map.keys():
        raise KeyError("Unsure how to handle key {}".format(this_key))
    else:
        return message_map[this_key].decode(full_response)



class DecoderType(Enum):
    Word=0
    SignedLong=1
    UnsignedLong=2 

def _decode_word(reply:bytes)->str:
    return reply.decode()
def _encode_word(reply:str)->bytes:
    return reply.encode()

def _decode_signed_long(reply:bytes)->int:
    """
        Assumes any headers or end of line characters are already removed! 
    """
    decoded = reply.decode()
    # reply will be a signed bit

    flip = decoded[0]!='0'
    package_len = len(decoded)    

    if flip:
        count_from = int("F"*package_len, 16)*-1 -1
    else:
        count_from = 0

    return count_from + int(decoded[:],16)

def _encode_signed_long(value, nbytes)->str:
    if value <0:
        adjusted = value - int("F"*nbytes, 16)*-1 +1
        return hex(adjusted)[2:].upper().encode()
    else:
        raw_hex = hex(value)[2:].upper()
        return ("0"*(nbytes-len(raw_hex)) + raw_hex).upper().encode()



def _encode_unsigned_long(value:int, nbytes:int)->str:
    """
        value should already be in pulses. No conversion takes place here! 
    """

    return hex(value)[2:].zfill(nbytes).upper().encode()

def _decode_unsigned_long(reply:bytes):
    return int(reply.decode(), 16)

def decode(sub_val:bytes, dt:DecoderType):
    if dt.value == DecoderType.Word.value:
        return _decode_word(sub_val)
    elif dt.value == DecoderType.UnsignedLong.value:
        return _decode_unsigned_long(sub_val) 
    elif dt.value == DecoderType.SignedLong.value:
        return _decode_signed_long(sub_val) 
    else:
        raise NotImplementedError("Unknown decoder type: {}".format(dt))

def encode(sub_val, dt:DecoderType, nbytes=-1)->str:
    print(sub_val, dt, nbytes)
    if dt.value == DecoderType.Word.value:
        return _encode_word(sub_val)
    elif dt.value == DecoderType.UnsignedLong.value:
        return _encode_unsigned_long(sub_val, nbytes) 
    elif dt.value == DecoderType.SignedLong.value:
        return _encode_signed_long(sub_val, nbytes) 
    else:
        raise NotImplementedError("Unknown decoder type: {}".format(dt))  

class Message:
    key="XX"
    def __init__(self, *args):
        self._args = args

class Call(Message):
    args = [
    ] 

    @classmethod 
    def encode(cls, *args):
        assert len(cls.args)==len(args)
        bytes_msg= ("0"+cls.key).encode()
        for i, entry in enumerate(args):
            bytes_msg += encode(entry, cls.args[i][1], cls.args[i][0])
        bytes_msg+="\n".encode()
        return bytes_msg

class Response(Message):
    # This should be a series of length-2 lists for [byte number - decoder type]
    reply=[
        [1, DecoderType.Word],
        [2, DecoderType.Word]
    ]
    @classmethod
    def decode(cls, retval:bytes):
        """
            For each expected entry in the return bytes, decode it and add it to a response list
            Then, return the responses
        """
        response = []
        bit_counter = 0
        for entry in cls.reply:
            these = retval[bit_counter:(bit_counter+entry[0])]
            bit_counter += entry[0]
            response.append(decode(these, entry[1])) 
        return response

# ======================== RESPONSES ===================
class GetStatus(Response):
    key = "GS"
    reply = Response.reply + [
        [2, DecoderType.Word]
    ]

class InfoDump(Response):
    key="IN"
    reply = Response.reply + [
        [2, DecoderType.Word], # bi positional slider
        [8, DecoderType.Word], # serial no 
        [4, DecoderType.Word], # year of manufacture
        [2, DecoderType.Word], # firmware ver
        [2, DecoderType.Word], # most significant bit signifies thread type? 
        [4, DecoderType.Word], # 31 mm travel
        [8, DecoderType.Word], # 1 pulse per position?
    ]

class GetPosition(Response):
    key = "AP"
    reply = Response.reply +[
        [8, DecoderType.SignedLong]
    ]
class Position(Response):
    key="PO"
    reply=Response.reply+[ 
        [8, DecoderType.SignedLong]
    ]
class HomeOffset(Response):
    key="HO"
    reply=Response.reply + [
        [8, DecoderType.SignedLong]
    ]


class JogResponse(Response):
    key="GJ"
    reply= Response.reply+[
        [8, DecoderType.SignedLong]
    ]
class VelocityResponse(Response):
    key="GV"
    reply = Response.reply+[ 
        [2, DecoderType.UnsignedLong]
    ]

# ======================== CALLS ===================
class RequestStatus(Call):
    key="gs"
class RequestInfo(Call):
    key="in"
class RequestJog(Call):
    key="gj"
class Isolate(Call):
    key="is"
    args=[
        [2, DecoderType.UnsignedLong]
    ]
class SetHome(Call):
    key="so"
    args=[
        [8, DecoderType.SignedLong]
    ]
class GoHome(Call):
    key = "go"
class RequestPosition(Call):
    key="gp"
class SetJog(Call):
    key="sj"
    args=[
        [8, DecoderType.SignedLong]
    ]
class StepForward(Call):
    key="fw"
class StepBackward(Call):
    key="bw"
class Stop(Call):
    key="st"
class MoveAbsolute(Call):
    key="ma"
    args=[
        [8, DecoderType.SignedLong]
    ]
class MoveRelative(Call):
    key="mr"
    args=[
        [8, DecoderType.SignedLong]
    ]
class GetVeolicty(Call):
    key="gv"
class SetVelocity(Call):
    key="sv"
    args=[
        [2, DecoderType.UnsignedLong]
    ]
class Stop(Call):
    key="st"