import os
import numpy
import onnxruntime
from typing import List
from vogen.synth import timetable

modelpath=os.path.join(os.path.split(os.path.realpath(__file__))[0],"models")
models={"man":onnxruntime.InferenceSession(os.path.join(modelpath,"f0.man.onnx")),
"yue":onnxruntime.InferenceSession(os.path.join(modelpath,"f0.yue.onnx")),
"yue-wz":onnxruntime.InferenceSession(os.path.join(modelpath,"f0.yue.onnx"))}

def run(romScheme:str,chars:List[timetable.TChar]):
    
    pass#TODO