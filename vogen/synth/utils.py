"""常量及通用功能代码"""
import datetime
import onnxruntime
from typing import Dict

class Params():
    fs=44100
    channels=1
    worldFftSize=2048
    
    hopSize=datetime.timedelta(milliseconds=10)
    headSil=datetime.timedelta(seconds=0.5)
    tailsil=datetime.timedelta(seconds=0.5)
    
    #let appDir=

#模型导入与缓存
class ModelManager():
    def __init__(self,pathtemplate:str):
        self.models={}
        self.pathtemplate=pathtemplate
        
    def get(self,id:str):
        if(not id in self.models):
            self.models[id]=onnxruntime.InferenceSession(self.pathtemplate.format(id))    
        return self.models[id]
    