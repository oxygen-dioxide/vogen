"""
PyVogen设置
"""
from typing import Any,Dict
import os
import json

#设置项说明
#DefaultSinger：默认的SingerId
#UseWinml：使用winml运行onnx模型（仅限windows，需安装winrt库，重启生效）

#出厂默认设置
defaultConfig={"DefaultSinger":"",
               "UseWinml":False}

#各设置项的变量类型
configtype={"DefaultSinger":str,
            "UseWinml":bool}

configPath=os.path.join(os.path.split(os.path.realpath(__file__))[0],"config.json")#设置文件路径

def write(config:Dict[str,Any]):
    """
    将设置写入设置文件
    """
    global configPath
    json.dump(config,open(configPath,"w",encoding="utf8"))

initConfig=defaultConfig#initConfig为vogen库本次刚刚导入时的设置，即设置文件
try:    
    initConfig.update(json.load(open(configPath)))
except json.decoder.JSONDecodeError:
    write(initConfig)
except FileNotFoundError:
    write(initConfig)

config=initConfig

def set(key:str,value:Any):
    """
    修改单个设置项并写入设置文件
    """
    if(type(value)==str!=configtype[key]):
        if(configtype[key]==bool):
            value={"true":True,"t":True,"false":False,"f":False}[value.lower()]
        else:
            value=configtype[key](value)
    assert(type(value)==configtype[key])
    config[key]=value
    initConfig[key]=value
    write(initConfig)