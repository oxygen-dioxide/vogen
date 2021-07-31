import datetime

class Params():
    fs=44100
    channels=1
    worlsFftSize=2048
    
    hopSize=datetime.timedelta(milliseconds=10)
    headSil=datetime.timedelta(seconds=0.5)
    tailsil=datetime.timedelta(seconds=0.5)
    
    #let appDir=

