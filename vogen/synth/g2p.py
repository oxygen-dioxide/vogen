"""拼音转音素"""
import os
import numpy
import onnxruntime
from typing import List,Optional

xLength=8
yLength=4

modelpath=os.path.join(os.path.split(os.path.realpath(__file__))[0],"models")
models={"man":onnxruntime.InferenceSession(os.path.join(modelpath,"g2p.man.onnx")),
"yue":onnxruntime.InferenceSession(os.path.join(modelpath,"g2p.yue.onnx")),
"yue-wz":onnxruntime.InferenceSession(os.path.join(modelpath,"g2p.yue-wz.onnx"))}

#拼音列表转为n*8的tensor，每个拼音一行，8字节，后面用"\0"补齐
def runForScheme(romScheme:str,roms:List[str])->List[List[str]]:
    xs=numpy.array([list(i.ljust(8,"\0")) for i in roms])
    model=models[romScheme]
    #代入模型运行
    ys=model.run([model.get_outputs()[0].name],{model.get_inputs()[0].name:xs})[0]
    #返回值示例：ys=[['d', 'u','',''], ['g', 'w', 'ag', 'ngq']]
    #过滤空字符串
    return [[j for j in i if j!=""] for i in ys]

def run(romScheme:str,roms:List[Optional[str]]):
    #let schemeToRomIndices =
    #建立"语言->哪些音符是这个语言（列表）"的字典
    schemeToRomIndices=dict()
    for i,rom in enumerate(roms):
        #用冒号临时改变一个音的语言
        if(rom!=None):
            if(":" in rom):
                currRomScheme=rom.split(":")[0]
            else:
                currRomScheme=romScheme
            schemeToRomIndices[currRomScheme]=schemeToRomIndices.get(currRomScheme,[])+[i]
            #TODO
    #let romsNoPrefix =
    #删除语言前缀
    romsNoPrefix=[None if rom==None else rom.split(":")[-1] for rom in roms]

    phs=[None]*len(roms)
    #for KeyValue(currRomScheme, romIndices) in schemeToRomIndices do
    for currRomScheme in schemeToRomIndices:
        romIndices=schemeToRomIndices[currRomScheme]
        schemeRoms=[romsNoPrefix[i] for i in romIndices]
        #print(schemeRoms,romIndices)
        #input()
        schemePhs=runForScheme(currRomScheme,schemeRoms)
        for (romIndex, schemePh) in zip(romIndices,schemePhs):
            if (currRomScheme==romScheme):
                phs[romIndex]=schemePh
            else:
                phs[romIndex]=[ph if (ph in ("",None)) else currRomScheme+":"+ph for ph in schemePh]
    return phs

def main():
    print(run("man",["yue:du","guang"]))

if(__name__=="__main__"):
    main()