__version__='0.0.1'

import json
import zipfile
from typing import List,Tuple,Dict,Union

class Vognote():
    def __init__(self,
                 pitch:int=60,
                 lyric:str="",
                 rom:str="a",
                 on:int=0,
                 dur:int=480):
        self.pitch=pitch
        self.lyric=lyric
        self.rom=rom
        self.on=on
        self.dur=dur
    
    def dump(self)->dict:
        return self.__dict__

def parsenote(content:dict)->Vognote:
    """
    将音符字典解析为Vognote对象
    """
    vn=Vognote()
    vn.__dict__.update(content)
    return vn

class Vogutt():
    def __init__(self,
                 name:str="",
                 singerId:str="gloria",
                 romScheme:str="man",
                 notes:List[Vognote]=[]):
        self.name=name
        self.singerId=singerId
        self.romScheme=romScheme
        self.notes=notes
    
    def dump(self)->dict:
        d=self.__dict__.copy()
        d["notes"]=[i.dump() for i in self.notes]
        return d

    def autosplit(self,r:int=0)->list:
        """
        自动拆分乐句，两个音符间隙大于r则拆分，返回拆分后的乐句列表
        """
        if(len(self.notes)<2):
            return [self]
        else:
            result=[]
            def newutt():
                result.append(Vogutt(name=self.name,singerId=self.singerId,romScheme=self.romScheme,notes=[]))
            newutt()
            time=self.notes[0].on
            for n in self.notes:
                if(n.on-time>r):
                    newutt()
                result[-1].notes.append(n)
                time=n.on+n.dur
            return result
        
def parseutt(content:dict):
    """
    将乐句字典解析为Vogutt对象
    """
    vu=Vogutt()
    vu.__dict__.update(content)
    vu.notes=[parsenote(i) for i in vu.notes]
    return vu

class Vogfile():
    def __init__(self,
                 timeSig0:str="4/4",
                 bpm0:float=120.0,
                 accomOffset:int=0,
                 utts:List[Vogutt]=[]):
        self.timeSig0=timeSig0
        self.bpm0=bpm0
        self.accomOffset=accomOffset
        self.utts=utts

    def dump(self)->dict:
        d=self.__dict__.copy()
        d["utts"]=[i.dump() for i in self.utts]
        return d

    def save(self,filename:str):
        with zipfile.ZipFile(filename,"w") as z:
            z.writestr("chart.json",json.dumps(self.dump()))

    def autosplit(self,r:int=0):
        """
        自动拆分乐句，两个音符间隙大于r则拆分
        """
        self.utts=sum((i.autosplit() for i in self.utts),[])
        return self

def parsefile(content:dict)->Vogfile:
    """
    将工程字典解析为Vogfile对象
    """
    vf=Vogfile()
    vf.__dict__.update(content)
    vf.utts=[parseutt(i) for i in vf.utts]
    return vf

def openvog(filename:str)->Vogfile:
    """
    打开vog文件，返回Vogfile对象
    """
    with zipfile.ZipFile(filename, "r") as z:
        return parsefile(json.loads(z.read("chart.json")))
