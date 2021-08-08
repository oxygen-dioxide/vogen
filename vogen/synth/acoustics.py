import os
import numpy
import onnxruntime
from typing import List,Optional
from vogen.synth import timetable,utils

pkgroot=os.path.join(os.path.split(os.path.realpath(__file__))[0],"libs")
modelmanager=utils.ModelManager(os.path.join(pkgroot,"{}","model.onnx"))

def run(romScheme:str,voiceLibId:str,f0:numpy.ndarray,chars:List[timetable.TChar])->List[numpy.ndarray]:
    voiceLibId=voiceLibId.lower()
    phs:List[timetable.TPhoneme]=sum([ch.ipa for ch in chars],[])
    phDurs=[ph.off-ph.on for ph in phs]
    phSyms=[]
    for ph in phs:
        if(ph.ph==None):
            phSyms.append("")
        elif(":" in ph.ph):
            phSyms.append(ph.ph)
        else:
            phSyms.append(romScheme+":"+ph.ph)
    breAmp=numpy.array([numpy.zeros(len(f0),dtype=numpy.float32)])
    xs={"phDurs":numpy.array([phDurs],dtype=numpy.int64),
        "phs":numpy.array([phSyms]),
        "f0":numpy.array([f0],dtype=numpy.float32),
        "breAmp":breAmp}

    pkgpath=os.path.join(pkgroot,voiceLibId)
    model=modelmanager.get(voiceLibId)
    return model.run([model.get_outputs()[0].name,model.get_outputs()[1].name],xs)
    #mgc,bap