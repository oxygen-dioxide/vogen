#基于Vogen 7月28日代码

import vogen
import numpy
import pyworld
from typing import List,Optional
from vogen.synth import f0
from vogen.synth import utils
from vogen.synth import prosody
from vogen.synth import acoustics
from vogen.synth import timetable

params=utils.Params()

def synthutt(utt:vogen.Vogutt,tempo:float):
    def ticktotime(tick:int)->int:
        #将480为一拍的tick转为0.01s为单位的时间
        return int(100*tick/(8*tempo))
    #print(utt.__dict__)
    tchars:List[timetable.TChar]=[timetable.TChar()]
    uttstart=utt.notes[0].on
    uttstarttime=ticktotime(uttstart)
    tick=uttstart
    
    for note in utt.notes:
        #如果音符前有空隙，则补充一个None
        if(note.on>tick):
            tchars.append(timetable.TChar())
        tnote=timetable.TNote(pitch=note.pitch,on=ticktotime(note.on)-uttstarttime+50,off=ticktotime(note.on+note.dur)-uttstarttime+50)
        if(note.rom=="-"):
            tchars[-1].notes.append(tnote)
        else:
            tchars.append(timetable.TChar(ch=note.lyric,rom=note.rom,notes=[tnote]))
        tick=note.on+note.dur
    tchars.append(timetable.TChar())
    
    tchars=prosody.run(utt.romScheme,tchars[-2].notes[-1].off+50,tchars)
    
    f0array=f0.run(utt.romScheme,tchars)
    
    mgc,bap=acoustics.run(utt.romScheme,utt.singerId,f0array,tchars)
    #print(mgc.shape,bap.shape)
    #TODO:将mgc、bap转为音频
    sp=pyworld.decode_spectral_envelope(mgc[0].astype(numpy.float64),params.fs,params.worldFftSize)
    #print(sp.shape)
    ap=pyworld.decode_aperiodicity(bap[0].astype(numpy.float64),params.fs,params.worldFftSize)
    #print(ap.shape)
    return pyworld.synthesize(f0array.astype(numpy.float64),sp,ap,params.fs,params.hopSize.microseconds//1000)

def synth(file:vogen.Vogfile):
    tempo=file.bpm0
    #以utt为单位合成
    nutt=len(file.utts)#utt的数量
    tracklen=max([utt.notes[-1].on+utt.notes[-1].dur for utt in file.utts])#以tick为单位的音轨总长度
    trackwave=numpy.zeros(int(params.fs*(tracklen/(8*tempo)+0.5)))#
    print(len(trackwave))
    for i,utt in enumerate(file.utts):
        #显示进度
        print("\r正在合成乐句{}/{}".format(i+1,nutt)+"#"*int(20*i/nutt)+"-"*(20-int(20*i/nutt)))
        #合成
        uttwave=synthutt(utt,tempo)
        #将合成出的音频加到音轨上
        uttoffset=int(params.fs*(utt.notes[0].on/(8*tempo)-0.5))
        trackwave[uttoffset:uttoffset+len(uttwave)]+=uttwave
    
    return (trackwave*(2**15 - 1)).astype(numpy.int16)

def is_jupyter_notebook()->bool:
    #检测是否为jupyter notebook
    try:
        get_ipython().__class__.__name__
        #jupyter notebook
        return True
    except NameError:
        #普通命令行
        return False

def play(file:vogen.Vogfile):
    a=synth(file)
    if(is_jupyter_notebook()):
        from IPython.display import Audio
        return Audio(data=a, rate=params.fs)
    else:
        import simpleaudio as sa
        sa.play_buffer(a,1,2,params.fs)
        

#测试
def main():
    global a
    a=synth(vogen.openvog(r"C:\users\lin\desktop\3.vog"))
    #print(a)
    #from myplot import plot
    #plot(a)
    
    #播放音频
    #import numpy as np
    #audio =(a*(2**15 - 1)/np.max(np.abs(a))).astype(np.int16)
    #plot(audio)
    #import simpleaudio as sa
    #sa.play_buffer(audio,1,2,44100)
    
    #导出音频
    import wavio
    import numpy as np
    wavio.write(r"C:\users\lin\desktop\3.wav",a,44100)

if(__name__=="__main__"):
    main()