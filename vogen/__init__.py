"""PyVogen：开源开源歌声合成引擎Vogen的python实现"""

__version__='0.0.6'

import copy
import json
import math
import zipfile
import jyutping
import pypinyin
import more_itertools
from vogen import config
from typing import List,Tuple,Dict,Union,Optional,Any
from collections.abc import Callable,Iterator

#导入numpy（可选）
try:
    import numpy
    hasnumpy=True
except ModuleNotFoundError:
    hasnumpy=False
"""
#导入vogen.synth（可选）
try:
    from vogen.synth import timetable
    hassynth=True
except ModuleNotFoundError:
    hassynth=False
"""
class VogNote():
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
        return "  VogNote {} {}[{}] {} {}\n".format(self.pitch,self.lyric,self.rom,self.on,self.dur)

    __repr__=__str__

    def dump(self)->dict:
        return self.__dict__

def parsenote(content:dict)->VogNote:
    """
    将音符字典解析为VogNote对象
    """
    vn=VogNote()
    vn.__dict__.update(content)
    return vn

class VogUtt():
    """
    Vogen乐句对象
    singerId：歌手
    romScheme：语种（man：中文普通话，yue：粤语，yue-wz：粤语梧州话）
    notes：音符列表
    f0：音高线（不支持写入文件）
    """
    def __init__(self,
                 singerId:str=config.config["DefaultSinger"],
                 romScheme:str=config.config["DefaultRomScheme"],
                 notes:List[VogNote]=[],
                 f0:Optional[numpy.ndarray]=None):
        self.singerId=singerId
        self.romScheme=romScheme
        self.notes=notes
        self.f0=f0
    
    def __add__(self,other):
        #两个乐句相加可合并乐句
        #self为上一乐句，other为下一乐句
        return VogUtt(singerId=self.singerId,romScheme=self.romScheme,notes=self.notes.copy()+other.notes.copy())

    def __radd__(self,other):
        #为适配sum，规定：其他类型+VogUtt返回原VogUtt的副本
        return copy.deepcopy(self)

    def __str__(self)->str:
        return " VogUtt {} {} \n".format(self.singerId,self.romScheme)+"".join(str(n) for n in self.notes)

    __repr__=__str__

    def __len__(self)->int:
        """
        获取乐句中的音符数量
        """
        return len(self.notes)
    
    def __getitem__(self,key)->VogNote:
        if(type(key)==slice):#如果是切片类型，则返回切片后的VogUtt对象
            return VogUtt(singerId=self.singerId,romScheme=self.romScheme,notes=self.notes[key])
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
        """
        将乐句对象转为vog文件中的字典形式
        """
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

    def synth(self,tempo:float):
        """
        合成乐句，以numpy数组形式返回音频
        tempo:曲速
        """
        import vogen.synth
        return vogen.synth.synthutt(self,tempo)

    def toVogUtt(self):
        return copy.deepcopy(self)

    def autojoinnote(self):
        """
        从musicxml或其他五线谱等价格式导入时，跨小节音符会被拆分为连音符，本函数将被拆分的音符恢复
        具体机制：连在一起的同音高连音符会被合并
        """
        length=len(self)
        for (i,(nextnote,note)) in enumerate(more_itertools.pairwise(reversed(self.notes))):
            if (nextnote.rom=="-" and note.pitch==nextnote.pitch and note.on+note.dur>=nextnote.on):
                note.dur=nextnote.on+nextnote.dur-note.on
                del self.notes[length-i-1]
        return self

    def getlyric(self)->List[str]:
        """
        获取乐句中所有音符的歌词（字符串列表）
        """
        return [note.lyric for note in self.notes]

    def getrom(self)->List[str]:
        """
        获取乐句中所有音符的拼音（字符串列表）
        """
        return [note.rom for note in self.notes]

    def setlyric(self,lyrics:Iterator[str]):
        """
        批量灌入歌词，并自动转换为拼音
        lyrics：要输入的歌词，可以是字符串，也可以是字符串列表
        """
        for (note,lyric) in zip(self.notes,lyrics):
            note.lyric=lyric
        return self.lyrictorom()

def music21StreamToVogUtt(st)->VogUtt:
    """
    将music21 stream对象转为vogen utt对象
    """
    import music21
    vognote=[]
    for note in st.flat.getElementsByClass(music21.note.Note):
        if(note.lyric in (None,"")):#连音符在music21中没有歌词
            lyric="-"
        else:
            lyric=note.lyric
        vognote.append(VogNote(on=int(note.offset*480),
                             dur=int(note.duration.quarterLength*480),
                             pitch=note.pitch.midi,
                             lyric=lyric,
                             rom=lyric))
    return VogUtt(notes=vognote).lyrictorom()

def utaupyUstToVogUtt(u)->VogUtt:
    """
    将utaupy ust对象转为vogen utt对象
    """
    vognotes=[]
    time=0
    for un in u.notes:
        notelen=int(un["Length"])
        if(not(un.lyric in ("","R","r"))):
            vognotes.append(VogNote(pitch=un["NoteNum"],lyric=un["Lyric"],rom=un["Lyric"],on=time,dur=notelen))
        time+=notelen
    return VogUtt(notes=vognotes)

def midoMidiTrackToVogUtt(mt)->VogUtt:
    """
    将mido miditrack对象转为vogen utt对象
    """
    tick=0
    lyric=""
    note:Dict[int,Tuple[str,int]]={}#音符注册表 {音高:(歌词,开始时间)}
    vognotes=[]
    for signal in mt:
        tick+=signal.time
        if(signal.type=="note_on"):
            #将新音符注册到键位-音符字典中
            note[signal.note]=(lyric,tick)
        elif(signal.type=="note_off"):
            #从键位-音符字典中找到音符，并弹出
            if(signal.note in note):
                n=note.pop(signal.note)
                vognotes.append(VogNote(on=n[1],
                            dur=tick-n[1],
                            pitch=signal.note,
                            lyric=n[0],
                            rom=n[0]))
        elif(signal.type=="lyrics"):
            lyric=signal.text
    return VogUtt(notes=vognotes).lyrictorom()

def toVogUtt(a)->VogUtt:
    """
    将其他类型的音轨工程对象转为vogen utt对象
    """
    type_name=type(a).__name__
    #从对象类型到所调用函数的字典
    type_function_dict={
        "VogUtt":copy.deepcopy,
        "Stream":music21StreamToVogUtt,#Music21普通序列对象
        "Measure":music21StreamToVogUtt,#Music21小节对象
        "Part":music21StreamToVogUtt,#Music21多轨中的单轨对象
        "Ust":utaupyUstToVogUtt,#utaupy ust对象
    }
    #如果在这个字典中没有找到函数，则默认调用a.toVogUtt()
    return type_function_dict.get(type_name,lambda x:x.toVogFile())(a)

def parseutt(content:dict):
    """
    将乐句字典解析为VogUtt对象
    """
    vu=VogUtt()
    vu.__dict__.update(content)
    vu.notes=[parsenote(i) for i in vu.notes]
    return vu

class VogFile():
    """
    vogen工程对象
    timeSig0：节拍
    bpm0：曲速
    accomOffset：伴奏起点
    utts：乐句列表
    """
    def __init__(self,
                 timeSig0:str="4/4",
                 bpm0:float=120.0,
                 accomOffset:int=0,
                 utts:List[VogUtt]=[]):
        self.timeSig0=timeSig0
        self.bpm0=bpm0
        self.accomOffset=accomOffset
        self.utts=utts

    def __add__(self,other):
        result=copy.deepcopy(self)
        result.utts+=other.utts
        return result

    def __radd__(self,other):
        #为适配sum，规定：其他类型+VogUtt返回原VogUtt的副本
        return copy.deepcopy(self)

    def __str__(self):
        return "VogFile {} {}\n".format(self.timeSig0,self.bpm0)+"".join(str(utt) for utt in self.utts)

    __repr__=__str__

    def __len__(self)->int:
        """
        获取工程中的乐句数量
        """
        return len(self.utts)
    
    def __getitem__(self,key)->VogNote:
        if(type(key)==slice):#如果是切片类型，则返回切片后的VogUtt对象
            return VogFile(timeSig0=self.timeSig0,bpm0=self.bpm0,accomOffset=self.accomOffset,utts=self.utts[key])
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

    def append(self,utt:VogUtt):
        self.utts.append(utt)
        return self

    def dump(self)->dict:
        """
        将乐句对象转为vog文件中的字典形式
        """
        d=self.__dict__.copy()
        d["utts"]=[i.dump() for i in self.utts]
        for (i,utt) in enumerate(d["utts"]):
            utt["name"]="utt-{}".format(i)
        return d

    def save(self,filename:str):
        """
        保存文件
        """
        with zipfile.ZipFile(filename,"w") as z:
            z.writestr("chart.json",json.dumps(self.dump()))

    def autosplit(self,r:int=80):
        """
        自动拆分乐句，两个音符间隙大于r则拆分
        """
        self.utts=sum((i.autosplit() for i in self.utts),[])
        return self

    def sortnote(self):
        """
        对工程中的每个乐句，分别对其中的音符排序
        """
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

    def setSinger(self,singerId:str):
        """
        为工程中的所有乐句统一设置歌手
        """
        for utt in self.utts:
            utt.singerId=singerId
        return self

    def setRomScheme(self,romScheme:str):
        """
        为工程中的所有乐句统一设置语种
        """
        for utt in self.utts:
            utt.romScheme=romScheme
        return self

    def lyrictorom(self):
        """
        从歌词生成拼音
        """
        for utt in self.utts:
            utt.lyrictorom()
        return self

    def synth(self):
        """
        合成工程，以numpy数组形式返回音频
        """
        import vogen.synth
        return vogen.synth.synth(self)

    def play(self):
        """
        合成工程并播放
        """
        import vogen.synth
        return vogen.synth.play(self)

    def separate_by_singer(self)->Dict[str,Any]:
        """
        根据歌手拆分工程，返回{音源名:对应的部分工程}字典
        """
        emptyfile=copy.copy(self)
        emptyfile.utts=[]
        result=dict()
        for i in self:
            result[i.singerId]=result.get(i.singerId,copy.copy(emptyfile)).append(i)
        return result

    def autojoinnote(self):
        for utt in self:
            utt.autojoinnote()
        return self

    def toVogFile(self):
        return copy.deepcopy(self)

    def notes(self):
        """
        工程对象中的音符迭代器
        注意：不是按音符的时间顺序，而是按乐句在工程中的顺序和音符在乐句中的顺序
        只有在乐句、音符按时间顺序排列（可用VogFile.sort函数排序），且没有乐句重叠时，该迭代器才按时间顺序
        """
        for utt in self:
            yield from utt
    
    def getlyric(self)->List[str]:
        """
        获取工程中所有音符的歌词（字符串列表）
        """
        return [note.lyric for note in self.notes()]
    
    def getrom(self)->List[str]:
        """
        获取工程中所有音符的拼音（字符串列表）
        """
        return [note.rom for note in self.notes()]
    
    def setlyric(self,lyrics:Iterator[str]):
        """
        批量灌入歌词，并自动转换为拼音
        lyrics：要输入的歌词，可以是字符串，也可以是字符串列表
        """
        for (note,lyric) in zip(self.notes(),lyrics):
            note.lyric=lyric
        return self.lyrictorom()   

def music21StreamToVogFile(st)->VogFile:
    """
    将music21 stream对象转为vogen工程对象
    注意：输入的music21 Stream对象不能有音符重叠
    """
    import music21
    vf=VogFile(utts=[music21StreamToVogUtt(st)]).autosplit()
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

def music21ScoreToVogFile(sc)->VogFile:
    """
    将music21 score对象转为vogen工程对象
    注意：输入的music21 score对象中，音轨内不能有音符重叠
    """
    return sum([music21StreamToVogFile(part) for part in sc.parts]).sort()
    
def utaupyUstToVogFile(u)->VogFile:
    """
    将utaupy ust对象转为vogen工程对象
    """
    return VogFile(utts=[utaupyUstToVogUtt(u)],bpm0=float(u.tempo)).autosplit()

def midoMidiTrackToVogFile(mt)->VogFile:
    vu=midoMidiTrackToVogUtt(mt)
    if(len(vu)>0):
        utts=[vu]
    else:
        utts=[]
    return VogFile(utts=utts).autosplit()
    #TODO:tempo

def midoMidiFileToVogFile(mf)->VogFile:
    return sum([midoMidiTrackToVogFile(tr) for tr in mf.tracks]).sort()
    #TODO:tempo

def toVogFile(a)->VogFile:
    """
    将其他类型的音轨工程对象a转为vogen工程对象
    """
    type_name=type(a).__name__
    #从对象类型到所调用函数的字典
    type_function_dict={
        "VogFile":copy.deepcopy,
        "Stream":music21StreamToVogFile,#Music21普通序列对象
        "Measure":music21StreamToVogFile,#Music21小节对象
        "Part":music21StreamToVogFile,#Music21多轨中的单轨对象
        "Score":music21ScoreToVogFile,#Music21多轨工程对象
        "Ust":utaupyUstToVogFile,#utaupy ust对象
    }
    #如果在这个字典中没有找到函数，则默认调用a.toVogFile()
    return type_function_dict.get(type_name,lambda x:x.toVogFile())(a)

def parsefile(content:dict)->VogFile:
    """
    将工程字典解析为VogFile对象
    """
    vf=VogFile()
    vf.__dict__.update(content)
    vf.utts=[parseutt(i) for i in vf.utts]
    return vf

def parsef0(fp)->numpy.ndarray:
    """
    解析工程文件中的f0文件
    """
    rawarray=numpy.frombuffer(fp,dtype=numpy.int)
    octave=rawarray//8388608-130
    #b=math.log2((rawarray%8388608)+8388608)*12-276.3763155
    key=numpy.log2((rawarray%8388608)+8388608)*12-276.3763155
    return (octave*12+key)*(rawarray!=0)

def openvog(filename:str,loadf0:bool=True)->VogFile:
    """
    打开vog文件，返回VogFile对象
    loadf0:是否加载音高线，默认为True（仅当loadf0=True且存在numpy库时加载）
    """
    with zipfile.ZipFile(filename, "r") as z:
        znamelist=z.namelist()
        vf=parsefile(json.loads(z.read("chart.json")))
        #uttdict={u.name:u for u in vf.utts}
        #加载音高线
        if(hasnumpy and loadf0):
            for i in range(len(vf.utts)):
                if("utt-{}.f0".format(i) in znamelist):
                    vf.utts[i].f0=parsef0(z.open("utt-{}.f0".format(i)).read())
    return vf
    
def loadfile_ust(filename:str)->VogFile:
    """
    读入ust文件，并转为VogFile对象
    """
    import utaupy
    return toVogFile(utaupy.ust.load(filename))

def loadfile_music21(filename:str)->VogFile:
    """
    读入music21支持的文件，并转为VogFile对象
    """
    import music21
    return music21ScoreToVogFile(music21.converter.parse(filename))
    
def loadfile_musicxml(filename:str)->VogFile:
    """
    读入musicxml文件，并转为VogFile对象
    """
    return loadfile_music21(filename).autojoinnote()

def loadfile_mid(filename:str)->VogFile:
    import mido
    return midoMidiFileToVogFile(mido.MidiFile(filename))

def loadfile(filename:str)->VogFile:
    """
    读入文件，并转为VogFile对象
    支持的文件类型：vog,ust,musicxml,mid
    """
    filetype=filename.split(".")[-1].lower()
    fileparsers:Dict[str,Callable[[str],VogFile]]={
            "vog":openvog,
            "ust":loadfile_ust,
            "musicxml":loadfile_musicxml,
            "mxl":loadfile_musicxml,
            "mid":loadfile_mid,
            }
    return fileparsers[filetype](filename)

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