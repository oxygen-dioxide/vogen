__version__='0.0.4'

import copy
import json
import math
import zipfile
import jyutping
import pypinyin
import more_itertools
from vogen import config
from typing import List,Tuple,Dict,Union,Optional

try:
    import numpy
    hasnumpy=True
except:
    hasnumpy=False

class Vognote():
    """
    Vogen音符对象
    pitch：音高，C4=60
    lyric：歌词汉字
    rom：歌词拼音
    on：开始时间，1拍=480
    dur：时长，1拍=480
    """
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

    def __str__(self):
        return "  Vognote {} {}[{}] {} {}\n".format(self.pitch,self.lyric,self.rom,self.on,self.dur)

    __repr__=__str__

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
    """
    Vogen乐句对象
    name：名称
    singerId：歌手
    romScheme：语种（man：中文普通话，yue：粤语）
    notes：音符列表
    f0：音高线（不支持写入文件）
    """
    def __init__(self,
                 name:str="",
                 singerId:str=config.config["DefaultSinger"],
                 romScheme:str="man",
                 notes:List[Vognote]=[],
                 f0:Optional[numpy.ndarray]=None):
        self.name=name
        self.singerId=singerId
        self.romScheme=romScheme
        self.notes=notes
        self.f0=f0
    
    def __add__(self,other):
        #两个乐句相加可合并乐句
        #self为上一乐句，other为下一乐句
        return Vogutt(name=self.name,singerId=self.singerId,romScheme=self.romScheme,notes=self.notes.copy()+other.notes.copy())

    def __radd__(self,other):
        #为适配sum，规定：其他类型+Vogutt返回原Vogutt的副本
        return copy.deepcopy(self)

    def __str__(self)->str:
        return " Vogutt {} {} {}\n".format(self.name,self.singerId,self.romScheme)+"".join(str(n) for n in self.notes)

    __repr__=__str__

    def __len__(self)->int:
        """
        获取乐句中的音符数量
        """
        return len(self.notes)
    
    def __getitem__(self,key)->Vognote:
        if(type(key)==slice):#如果是切片类型，则返回切片后的Vogutt对象
            return Vogutt(name=self.name,singerId=self.singerId,romScheme=self.romScheme,notes=self.notes[key])
        else:#如果key是整数，则返回音符
            return self.notes[key]

    def __setitem__(self,key,value):
        self.notes[key]=value
    
    def __delitem__(self,key):
        self.notes.__delitem__(key)
    
    def __iter__(self):
        return iter(self.notes)

    def __reversed__(self):
        return reversed(self.notes)

    def dump(self)->dict:
        d=self.__dict__.copy()
        d.pop("f0")
        d["notes"]=[i.dump() for i in self.notes]
        return d

    def autosplit(self,r:int=80)->list:
        """
        自动拆分乐句，两个音符间隙大于r则拆分，返回拆分后的乐句列表
        """
        indexs=[None]+[i+1 for (i,(note,nextnote)) in enumerate(more_itertools.pairwise(self)) if (note.on+note.dur+r<nextnote.on)]+[None]
        return [self[i:nexti] for (i,nexti) in more_itertools.pairwise(indexs)]

    def offset(self,offset:int=0):
        """将utt中的音符全部左右移动offset个单位"""
        for note in self.notes:
            note.on+=offset
        return self

    def sort(self):
        """
        对乐句中的音符排序
        """
        self.notes.sort(key=lambda x:x.on)
        return self
    
    def lyrictorom(self):
        """
        从歌词汉字生成拼音
        """
        hanzis=""
        hanzinotes=[]
        for note in self.notes:
            if(len(note.lyric)==1 and '\u4e00'<=note.lyric<='\u9fff'):
                hanzis+=note.lyric
                hanzinotes.append(note)
            else:
                note.rom=note.lyric
        if(self.romScheme=="man"):#普通话
            pinyins=pypinyin.lazy_pinyin(hanzis)
        elif(self.romScheme.startswith("yue")):#粤语
            pinyins=(i[:,-1] for i in jyutping.get(note))
        for (note,pinyin) in zip(hanzinotes,pinyins):
            note.rom=pinyin
        return self

def music21_stream_to_vog_utt(st)->Vogutt:
    import music21
    vognote=[]
    for note in st.flat.getElementsByClass(music21.note.Note):
        if(note.lyric in (None,"")):#连音符在music21中没有歌词
            lyric="-"
        else:
            lyric=note.lyric
        vognote.append(Vognote(on=int(note.offset*480),
                             dur=int(note.duration.quarterLength*480),
                             pitch=note.pitch.midi,
                             lyric=lyric,
                             rom=lyric))
                             #TODO:汉字转拼音
    return Vogutt(notes=vognote)

def to_vog_utt(a)->Vogutt:
    """
    将其他类型的音轨工程对象a转为vogen utt对象
    """
    type_name=type(a).__name__
    #从对象类型到所调用函数的字典
    type_function_dict={
        "Vogutt":copy.deepcopy,
        "Stream":music21_stream_to_vog_utt,#Music21普通序列对象
        "Measure":music21_stream_to_vog_utt,#Music21小节对象
        "Part":music21_stream_to_vog_utt,#Music21多轨中的单轨对象
    }
    #如果在这个字典中没有找到函数，则默认调用a.to_vog_utt()
    return type_function_dict.get(type_name,lambda x:x.to_vog_file())(a)

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

    def __add__(self,other):
        result=copy.deepcopy(self)
        result.utts+=other.utts
        return result

    def __radd__(self,other):
        #为适配sum，规定：其他类型+Vogutt返回原Vogutt的副本
        return copy.deepcopy(self)

    def __str__(self):
        return "Vogfile {} {}\n".format(self.timeSig0,self.bpm0)+"".join(str(utt) for utt in self.utts)

    __repr__=__str__

    def __len__(self)->int:
        """
        获取工程中的乐句数量
        """
        return len(self.utts)
    
    def __getitem__(self,key)->Vognote:
        if(type(key)==slice):#如果是切片类型，则返回切片后的Vogutt对象
            return Vogfile(timeSig0=self.timeSig0,bpm0=self.bpm0,accomOffset=self.accomOffset,utts=self.utts[key])
        else:#如果key是整数，则返回乐句
            return self.utts[key]

    def __setitem__(self,key,value):
        self.utts[key]=value
    
    def __delitem__(self,key):
        self.utts.__delitem__(key)
    
    def __iter__(self):
        return iter(self.utts)

    def __reversed__(self):
        return reversed(self.utts)

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

    def sortnote(self):
        for utt in self.utts:
            utt.sort()
        return self

    def sort(self):
        """
        对工程文件中的乐句排序
        """
        self.sortnote()
        self.utts.sort(key=lambda x:x.notes[0].on)
        return self

    def setSingerId(self,singerId:str):
        """
        为工程中的所有乐句设置歌手
        """
        for utt in self.utts:
            utt.singerId=singerId
        return self

    def setRomScheme(self,romScheme:str):
        """
        为工程中的所有乐句设置语种
        """
        for utt in self.utts:
            utt.romScheme=romScheme
        return self

    def lyrictorom(self):
        for utt in self.utts:
            utt.lyrictorom()
        return self

def music21_stream_to_vog_file(st):
    import music21
    vf=Vogfile(utts=[music21_stream_to_vog_utt(st)]).autosplit()
    #节拍
    b=list(st.getElementsByClass(music21.meter.TimeSignature))
    if(len(b)>0):
        b=b[0]
        vf.timeSig0=("{}/{}".format(b.numerator,b.denominator))
    #曲速
    t=list(st.getElementsByClass(music21.tempo.MetronomeMark))
    if(len(t))>0:
        vf.bpm0=t[0].number
    return vf

def to_vog_file(a)->Vogfile:
    """
    将其他类型的音轨工程对象a转为vogen工程对象
    """
    type_name=type(a).__name__
    #从对象类型到所调用函数的字典
    type_function_dict={
        "Vogfile":copy.deepcopy,
        "Stream":music21_stream_to_vog_file,#Music21普通序列对象
        "Measure":music21_stream_to_vog_file,#Music21小节对象
        "Part":music21_stream_to_vog_file,#Music21多轨中的单轨对象
    }
    #如果在这个字典中没有找到函数，则默认调用a.to_vog_file()
    return type_function_dict.get(type_name,lambda x:x.to_vog_file())(a)

def parsefile(content:dict)->Vogfile:
    """
    将工程字典解析为Vogfile对象
    """
    vf=Vogfile()
    vf.__dict__.update(content)
    vf.utts=[parseutt(i) for i in vf.utts]
    return vf

def parsef0(fp)->numpy.ndarray:
    rawarray=numpy.frombuffer(fp,dtype=numpy.int)
    octave=rawarray//8388608-130
    #b=math.log2((rawarray%8388608)+8388608)*12-276.3763155
    key=numpy.log2((rawarray%8388608)+8388608)*12-276.3763155
    return (octave*12+key)*(rawarray!=0)

def openvog(filename:str,loadf0:bool=True)->Vogfile:
    """
    打开vog文件，返回Vogfile对象
    loadf0:是否加载音高线，默认为True（仅当loadf0=True且存在numpy库时加载）
    """
    with zipfile.ZipFile(filename, "r") as z:
        znamelist=z.namelist()
        vf=parsefile(json.loads(z.read("chart.json")))
        uttdict={u.name:u for u in vf.utts}
        if(hasnumpy and loadf0):
            for i in uttdict:
                if(i+".f0" in znamelist):
                    uttdict[i].f0=parsef0(z.open(i+".f0").read())
    return vf
    
#关于f0格式
#np.fromfile("utt-0.f0",dtype=np.int)
#以八度为单位，八度之间等差，差2**23
#八度之内为等比，(x+1)%2**23的公比为2**(1/12)（十二平均律常数）
#TODO:f0的时间单位

#调试
def main():
    openvog(r"C:\users\lin\desktop\shl.vog")

if(__name__=="__main__"):
    main()