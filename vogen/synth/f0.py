"""基频模型相关"""
import os
import numpy
import onnxruntime
import more_itertools
from typing import List,Optional
from vogen.synth import timetable

modelpath=os.path.join(os.path.split(os.path.realpath(__file__))[0],"models")
models={"man":onnxruntime.InferenceSession(os.path.join(modelpath,"f0.man.onnx")),
"yue":onnxruntime.InferenceSession(os.path.join(modelpath,"f0.yue.onnx")),
"yue-wz":onnxruntime.InferenceSession(os.path.join(modelpath,"f0.yue.onnx"))}

def run(romScheme:str,chars:List[timetable.TChar])->numpy.ndarray:
    phs=sum([ch.ipa for ch in chars],[])
    uttDur=chars[-1].ipa[-1].off
    noteOps:List[Optional[timetable.TNote]]=sum([([None] if ch.notes==None else ch.notes) for ch in chars],[])
    #print([None if n==None else n.__dict__ for n in noteOps])
    noteBounds=[0]
    for (prevNote,note) in more_itertools.pairwise(noteOps):
        if(note!=None):
            noteBounds.append(note.on)
        elif(prevNote!=None):
            noteBounds.append(prevNote.off)
        else:
            pass#raise ArgumentException("Consecutive sil chars in %A")
    noteBounds.append(uttDur)
    phSyms=[]
    for ph in phs:
        if(ph.ph==None):
            phSyms.append("")
        elif(":" in ph.ph):
            phSyms.append(ph.ph)
        else:
            phSyms.append(romScheme+":"+ph.ph)
    notePitches=[0.0 if note==None else note.pitch for note in noteOps]
    noteDurs=[(t1-t0) for (t0,t1) in more_itertools.pairwise(noteBounds)]
    noteToCharIndex=list(range(len(noteOps)))
    phDurs=[ph.off-ph.on for ph in phs]
    xs={"phs":numpy.array(phSyms),
        "notePitches":numpy.array(notePitches,dtype=numpy.float32),
        "noteDurs":numpy.array(noteDurs,dtype=numpy.int64),
        "noteToCharIndex":numpy.array(noteToCharIndex,dtype=numpy.int64),
        "phDurs":numpy.array(phDurs,dtype=numpy.int64)}
    #运行模型
    model=models[romScheme]
    f0=model.run([model.get_outputs()[0].name],xs)[0]
    return f0

def main():
    import timetable as t
    chars=[t.TChar(ch=None,rom=None,notes=None,ipa=[t.TPhoneme(ph=None,on=0,off=39)]),
        t.TChar(ch="du",rom="du",notes=[t.TNote(pitch=60,on=50,off=75)],ipa=[t.TPhoneme("d",39,50),t.TPhoneme("u",50,66)]),
        t.TChar(ch="guang",rom="guang",notes=[t.TNote(pitch=62,on=75,off=100),t.TNote(60,100,125)],ipa=[t.TPhoneme("g",66,74),t.TPhoneme("w",74,85),t.TPhoneme("ag",85,103),t.TPhoneme("ngq",103,125)]),
        t.TChar(ch=None,rom=None,notes=None,ipa=[t.TPhoneme(None,125,175)]),
    ]
    f0=run("man",chars)
    from myplot import plot
    plot(f0)

if(__name__=="__main__"):
    main()