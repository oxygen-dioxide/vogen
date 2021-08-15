"""确定音素时长"""
import os
import copy
import numpy
import datetime
import onnxruntime
import more_itertools
from typing import List
from vogen.synth import g2p
from vogen.synth import timetable

modelpath=os.path.join(os.path.split(os.path.realpath(__file__))[0],"models")
models={"man":onnxruntime.InferenceSession(os.path.join(modelpath,"po.man.onnx")),
"yue":onnxruntime.InferenceSession(os.path.join(modelpath,"po.yue.onnx")),
"yue-wz":onnxruntime.InferenceSession(os.path.join(modelpath,"po.yue.onnx"))}

def run(romScheme:str,uttDur:int,chars:List[timetable.TChar]):
    roms=[i.rom for i in chars]
    chPhs=g2p.run(romScheme,roms)
    chPhs=[([None] if i==None else i)  for i in chPhs]
    phs=[]
    for i in chPhs:
        for ph in i:
            if(ph==None):
                phs.append("")
            elif(":" in ph):
                phs.append(ph)
            else:
                phs.append(romScheme+":"+ph)
    #print(phs)
    chPhCounts=[len(i) for i in chPhs]
    noteBounds=[0]
    for (ch0,ch1) in more_itertools.pairwise(chars):
        if ch1.notes!=None:
            noteBounds.append(ch1.notes[0].on)
        else:
            noteBounds.append(ch0.notes[-1].off)
    noteBounds.append(uttDur)
    noteBoundsSec=[timetable.frameToTime(i).total_seconds() for i in noteBounds]
    noteDursSec=[nt1-nt0 for (nt0,nt1) in more_itertools.pairwise(noteBoundsSec)]
    xs={"phs":numpy.array(phs),"chPhCounts":numpy.array(chPhCounts,dtype=numpy.int64),"noteDursSec":numpy.array(noteDursSec,dtype=numpy.float32)}
    #print(xs)
    #运行模型
    model=models[romScheme]
    ys=model.run([model.get_outputs()[0].name],xs)[0]
    #print(ys)
    phBoundsSec=ys.tolist()
    #TODO
    #跑出来的结果可能会有dur<=0，修复
    #minPhDurSec=timetable.frameToTime(1.01).total_seconds()
    #for (nt0,nt1) in zip(noteBoundsSec[-2::-1],noteBoundsSec[-1:0:-1]):
    #    print(nt0,nt1)
    phBounds=[int(round(timetable.timeToFrame(datetime.timedelta(seconds=i)))) for i in phBoundsSec]
    chPhIndexBounds=[0]
    for i in chPhCounts:
        chPhIndexBounds.append(chPhIndexBounds[-1]+i)
    
    chPhBounds=[phBounds[startIndex:endIndex+1] for (startIndex, endIndex) in more_itertools.pairwise(chPhIndexBounds)]
    #print(chPhBounds)
    outChars=copy.deepcopy(chars)
    for (char,phs,phBounds) in zip(outChars,chPhs,chPhBounds):
        char.ipa=[timetable.TPhoneme(ph=ph,on=on,off=off) for (ph,on,off) in zip(phs,phBounds[0:-1],phBounds[1:])]
    return outChars


def main():
    import timetable as t
    chars=[t.TChar(ch=None,rom=None,notes=None,ipa=None),
        t.TChar(ch="du",rom="du",notes=[t.TNote(pitch=60,on=50,off=75)],ipa=None),
        t.TChar(ch="guang",rom="guang",notes=[t.TNote(pitch=62,on=75,off=100)],ipa=None),
        t.TChar(ch=None,rom=None,notes=None,ipa=None),
    ]
    a=run("man",150,chars)
    #print(a[2].ipa[3])

if(__name__=="__main__"):
    main()