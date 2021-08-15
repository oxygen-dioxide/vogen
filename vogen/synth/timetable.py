"""vogen.synth基础类库"""
import datetime
from vogen.synth import utils
from typing import List,Optional


def timeToFrame(timeSpan:datetime.timedelta)->float:
    return timeSpan/utils.Params.hopSize
def frameToTime(frames:float)->datetime.timedelta:
    return frames*utils.Params.hopSize

import json

class TPhoneme():
    def __init__(self,ph:str,on:int,off:int):
        self.ph=ph
        self.on=on
        self.off=off

class TNote():
    """
    pitch:音高
    on:开始时间，单位为0.25s，取整
    off:结束时间，单位为0.25s，取整
    """
    def __init__(self,pitch:int,on:int,off:int):
        self.pitch=pitch
        self.on=on
        self.off=off

class TChar():
    """
    ch:汉字，对于空白为None
    rom:拼音，对于空白为None
    notes:音高列表
    ipa:（待处理）音素列表
    """
    def __init__(self,
                ch:Optional[str]=None,
                rom:Optional[str]=None,
                notes:Optional[List[TNote]]=None,
                ipa:Optional[List[TPhoneme]]=None):
        self.ch=ch
        self.rom=rom
        self.notes=notes
        self.ipa=ipa 
       
class TUtt():
    def __init__(self,uttStartSec:float,uttDur:int,romScheme:str,chars:List[TChar]):
        self.uttStartSec=uttStartSec
        self.uttDur=uttDur
        self.romScheme=romScheme
        self.chars=chars