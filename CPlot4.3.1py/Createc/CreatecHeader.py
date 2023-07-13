class Header:
    def __init__(self, file):
        self.header={}

        with open(file, 'rt') as f:
            for self.header_lines, line in enumerate(f):
                line=line.strip()
                if not line: break
                key, *value =line.split('=', 1)
                self.header[key]= value
                if key == 'DATA':
                    lines=f.readlines()
                    cols=lines[0].strip()
                    points=cols.split()
                    break
        self.points=int(points[0])
        usedchannels=[]
        channels=[4096,2048,1024,512,256,128,64,32,16,8,4,2,1]
        channelsum=int(self.header['Vertchannelselectval'][0])
        for elem in channels:
            if channelsum >= elem:
                channelsum -= elem
                usedchannels.append(elem)
        self.columns=len(usedchannels)
        usedchannels.reverse
        self.i=usedchannels.index(8)
        self.didv=usedchannels.index(32)
        back=int(self.header['VertSpecBack'][0])
        if back == 0:
            self.back = False
        else:
            self.back = True
            self.backnum = back
 
        
class Grid:
    def __init__(self, file):

        filehead=r'{}.dat'.format(file)
        self.header={}

        with open(filehead, 'rt') as f:
            for header_lines, line in enumerate(f):
                line=line.strip()
                if not line: break
                key, *value =line.split('=', 1)
                self.header[key]= value
                if key == 'PSTMAFM.EXE_Date':
                    break
        GridX=int(self.header['Num.X / Num.X'][0])/int(self.header['SpecXGrid'][0])
        GridY=int(self.header['Num.Y / Num.Y'][0])/int(self.header['SpecYGrid'][0])
        self.GridX=int(GridX)
        self.GridY=int(GridY)
        self.X=float(self.header['Length x[A]'][0])/10
        self.Y=float(self.header['Length y[A]'][0])/10
        self.spectra=self.GridX*self.GridY
        self.skip=256

        self.pointlist=[]

        for i in range(0,8):
            self.pointlist.append(int(self.header['Vpoint{}.t'.format(i)][0]))
        
        self.points=max(self.pointlist)    
        usedchannels=[]
        channels=[4096,2048,1024,512,256,128,64,32,16,8,4,2,1]
        channelsum=int(self.header['Vertchannelselectval'][0])
        for elem in channels:
            if channelsum >= elem:
                channelsum -= elem
                usedchannels.append(elem)
        self.columns=len(usedchannels)
        usedchannels.reverse
        self.didv=usedchannels.index(32)
        

