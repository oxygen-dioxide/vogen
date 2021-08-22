import os
import json
import wget
import shutil
import zipfile
import tempfile
from typing import Dict,List

pkgroot=os.path.join(os.path.split(os.path.realpath(__file__))[0],"synth","libs")

#由于windows文件夹不区分大小写，而Linux区分大小写
#为保证跨平台一致性，所有包名均转为小写

def install_local(name:str,force:bool=False)->int:
    """
    安装本地音源
    name:文件路径与名称
    """
    name=os.path.realpath(name)
    with zipfile.ZipFile(name, "r") as z:
        contents=z.namelist()
        #如果没有meta.json或model.onnx，则包不完整,返回1
        if(not("meta.json" in contents and "model.onnx" in contents)):
            return 1
        pid=json.loads(z.read("meta.json"))["id"].lower()
        pkgpath=os.path.join(pkgroot,pid)
        #如果目录已存在，则询问是否删除
        if(os.path.exists(pkgpath)):
            if(force):
                shutil.rmtree(pkgpath)    
            else:
                print(pid+"已存在，是否删除？\ny:删除并继续安装  n:保留并放弃安装")
                instr=input()
                while(len(instr)==0 or not(instr[0] in ("y","n","Y","N"))):
                    print("y:删除并继续安装  n:保留并放弃安装")
                    instr=input()
                if(instr[0] in ("y","Y")):
                    shutil.rmtree(pkgpath)
                else:
                    return -1
            
        #创建目录
        os.makedirs(pkgpath)
        #解压文件
        orgcwd=os.getcwd()#先备份原工作路径，以便返回
        os.chdir(pkgpath)
        z.extractall()
        os.chdir(orgcwd)
    print("已安装",pid)
    return 0

def install_online(url:str,force:bool=False):
    path=os.path.join(tempfile.mkdtemp(),"temp.vogeon")
    wget.download(url,path)
    install_local(path,force)
    
def install(name:str,force:bool=False):
    """
    安装音源
    name:文件路径与名称
    """
    if(os.path.isfile(name)):
        install_local(name,force)
    else:
        install_online(name,force)

def uninstall(pid:str):
    pkgpath=os.path.join(pkgroot,pid)
    shutil.rmtree(pkgpath)

def list()->List[str]:
    """
    列出已安装的音源
    """
    names=[]
    for name in os.listdir(pkgroot):
        pkgpath=os.path.join(pkgroot,name)
        if(os.path.isfile(os.path.join(pkgpath,"meta.json")) and os.path.isfile(os.path.join(pkgpath,"model.onnx"))):
            names.append(name)
    return names
    
def show(pid:str)->Dict[str,str]:
    """
    音源详细信息
    """
    return json.load(open(os.path.join(pkgroot,pid,"meta.json"),encoding="utf8"))

def main():
    list()

if(__name__=="__main__"):
    main()