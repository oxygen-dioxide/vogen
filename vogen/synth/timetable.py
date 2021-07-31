import datetime
from vogen.synth import utils
from typing import List,Optional

#TODO
def timeToFrame(timeSpan:datetime.timedelta)->float:
    return timeSpan/utils.Params.hopSize
def frameToTime(frames:float)->datetime.timedelta:
    return frames*utils.Params.hopSize

#let timeToFrame(timeSpan : TimeSpan) = timeSpan / hopSize
#let frameToTime(frames : float) = frames * hopSize

import json

class TPhoneme():
    def __init__(self,ph:str,on:int,off:int):
        self.ph=ph
        self.on=on
        self.off=off

class TNote():
    def __init__(self,pitch:int,on:int,off:int):
        self.pitch=pitch
        self.on=on
        self.off=off

class TChar():
    def __init__(self,
                ch:Optional[str],
                rom:Optional[str],
                notes:Optional[List[TNote]],
                ipa:Optional[List[TPhoneme]]):
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