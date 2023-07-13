import numpy as np

class Header:
    def __init__(self, file):
        self.file=file
        self.header={}
        self.columns={}
        self.hor=False
        with open(file, encoding="Latin-1") as f:
            for header_lines, line in enumerate(f):
                line=line.strip()
                if line == '#CPlot file [V, dIdV, I]':
                    CFILE = True
                    HOR = False
                    break
                if line == '#CPlot file [x, dIdV, I]':
                    CFILE = True
                    HOR = True
                    break
                else:
                    CFILE = False
                    HOR = False
                    key, *value =line.split('\t', 1)
                    self.header[key]= value
                    if key == '[DATA]':
                        lines=f.readlines()
                        cols=lines[0].strip()
                        self.channels=cols.split('\t')
                        break
        if CFILE:
            self.header['1'] = 0
            self.X = 0
            self.Y = 0
            self.columns['V']=0
            self.columns['I']=2
            self.columns['dIdV']=1
        elif HOR:
            self.hor = True
        else:
            self.X=float(self.header['X (m)'][0])
            self.Y=float(self.header['Y (m)'][0])
            for ele in self.channels:
                if '[filt]' not in ele:
                    if 'LI Demod 1 X (A)' in ele:
                        key = 'dIdV'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'Current (A)' in ele:
                        key = 'I'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'LI Demod 2 X (A)' in ele:
                        key = 'd2IdV2'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'Bias (V)' in ele:
                        key = 'V'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'LI Demod 1 R (A)' in ele:
                        key = 'dIdV'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'LI Demod 2 R (A)' in ele:
                        key = 'd2IdV2'
                        value= (self.channels.index(ele))
                        self.columns[key]=value

                    #Backward data

                    if 'LI Demod 1 X [bwd] (A)' in ele:
                        key = 'dIdV[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'Current [bwd] (A)' in ele:
                        key = 'I[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'LI Demod 2 X [bwd] (A)' in ele:
                        key = 'd2IdV2[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'Bias [bwd] (V)' in ele:
                        key = 'V[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'LI Demod 1 R [bwd] (A)' in ele:
                        key = 'dIdV[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'LI Demod 2 R [bwd] (A)' in ele:
                        key = 'd2IdV2[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key]=value
                    if 'Z [bwd] (m)' in ele:
                        key = 'Z[bwd]'
                        value= (self.channels.index(ele))
                        self.columns[key] = value

                
class Grid:
    def __init__(self, file):
        self.file=file
        self.header={}
        self.columns={}
        with open(file, encoding="Latin-1") as f:
            for header_lines, line in enumerate(f):
                line=line.strip()
                key, *value =line.split('=', 1)
                self.header[key]= value
                if key == ':HEADER_END:':
                    break
        Griddim=(self.header['Grid dim'][0]).split('x')
        self.GridX=int(Griddim[0].replace('"',''))
        self.GridY=int(Griddim[1].replace('"',''))
        self.points=int(self.header['Points'][0])
        self.channels=(self.header['Channels'][0]).split(';')
        self.para=int(self.header['# Parameters (4 byte)'][0])
        self.exp=(self.header['Experiment parameters'][0]).split(';')
        sett=(self.header['Grid settings'][0]).split(';')
        self.X=1e9*float(sett[2])
        self.Y=1e9*float(sett[3])
        col=(self.header['Channels'][0]).split(';')
        for ele in col:

            # Forward data

            if 'LI Demod 1 X (A)' in ele:
                key = 'dIdV'
                value= col.index(ele)
                self.columns[key]=value
            if 'Current (A)' in ele:
                key = 'I'
                value= col.index(ele)
                self.columns[key]=value
            if 'LI Demod 2 X (A)' in ele:
                key = 'd2IdV2'
                value=col.index(ele)
                self.columns[key]=value
            if 'Bias (V)' in ele:
                key = 'V'
                value=col.index(ele)
                self.columns[key]=value
            if 'LI Demod 1 R (A)' in ele:
                key = 'dIdV'
                value= (self.channels.index(ele))
                self.columns[key]=value
            if 'LI Demod 2 R (A)' in ele:
                key = 'd2IdV2'
                value= (self.channels.index(ele))
                self.columns[key]=value
            if 'Z (m)' in ele:
                key = 'Z'
                value = (self.channels.index(ele))
                self.columns[key] = value

            #Backward data

            if 'LI Demod 1 X [bwd] (A)' in ele:
                key = 'dIdV[bwd]'
                value= col.index(ele)
                self.columns[key]=value
            if 'Current [bwd] (A)' in ele:
                key = 'I[bwd]'
                value= col.index(ele)
                self.columns[key]=value
            if 'LI Demod 2 X [bwd] (A)' in ele:
                key = 'd2IdV2[bwd]'
                value=col.index(ele)
                self.columns[key]=value
            if 'Bias [bwd] (V)' in ele:
                key = 'V[bwd]'
                value=col.index(ele)
                self.columns[key]=value
            if 'LI Demod 1 R [bwd] (A)' in ele:
                key = 'dIdV[bwd]'
                value= (self.channels.index(ele))
                self.columns[key]=value
            if 'LI Demod 2 R [bwd] (A)' in ele:
                key = 'd2IdV2[bwd]'
                value= (self.channels.index(ele))
                self.columns[key]=value
            if 'Z [bwd] (m)' in ele:
                key = 'Z[bwd]'
                value = (self.channels.index(ele))
                self.columns[key] = value

        if 'Z (m)' in self.exp:
            self.Z = (self.exp.index('Z (m)')) + self.para - len(self.exp)


class MP:
    def __init__(self, file):
        self.file=file
        self.MPC={}
        self.DI={}
        self.columns={}
        self.V=[]
        key=''
        count=0
        with open(file, encoding="Latin-1") as f:
            for header_lines, line in enumerate(f):
                count+=1
                line=line.strip()
                if line == ':SCAN_PIXELS:':
                    nextline=f.readline()
                    values = nextline.split()
                    self.GridX=int(values[0].replace('"',''))
                    self.GridY=int(values[1].replace('"',''))
                    count+=1
                if line == ':SCAN_RANGE:':
                    nextline=f.readline()
                    values = nextline.split()
                    self.X=1e9*float(values[0].replace('"',''))
                    self.Y=1e9*float(values[1].replace('"',''))
                    count+=1
                if line == ':BIAS:':
                    nextline=f.readline()
                    values = nextline.split()
                    self.V.append(float(values[0].replace('"','')))
                    count+=1
                if line == ':Multipass-Config:':
                    self.V=[]
                    n=0
                    while nextline[0] != ':':
                        nextline=f.readline()
                        values = nextline.split()
                        self.MPC[n]=values
                        n+=1
                        count+=1
                if line == ':DATA_INFO:':
                    n=0
                    while True:
                        nextline=f.readline()
                        values = nextline.split()
                        self.DI[n]=values
                        n+=1
                        count+=1
                        if nextline == '\n':
                            break
                if line == ':SCANIT_END:':
                    count+=2
                    break
                
            self.header=count
            
            self.channels={}
            self.back = False
            
            if self.MPC:
                for i in range (1,len(self.MPC)-1):
                    self.V.append(float(self.MPC[i][5])+0.00001*i)

            if self.DI[1][3] == 'both':
                self.back = True
            if self.back:
                self.total = (len(self.DI)-2)*2
            elif not self.back:
                self.total = (len(self.DI)-2)

            if self.MPC:
                self.points=len(self.MPC)-2
            else:
                if self.back:
                    self.points=2
                    self.V.append(self.V[0])
                else:
                    self.points=1


            self.channelnum=int(self.total/self.points)
            col= []
            for j in range (1, self.channelnum+1):
                col.append(self.DI[j][1])

            for ele in col:
                if 'LI_Demod_1_X' in ele:
                    key = 'dIdV'
                    value= col.index(ele)
                    self.columns[key]=value
                if 'Current' in ele:
                    key = 'I'
                    value= col.index(ele)
                    self.columns[key]=value
                if 'LI_Demod_2_X' in ele:
                    key = 'd2IdV2'
                    value=col.index(ele)
                    self.columns[key]=value
                if 'Bias' in ele:
                    key = 'V'
                    value=col.index(ele)
                    self.columns[key]=value
                if 'Z' in ele:
                    key = 'Z'
                    value=col.index(ele)
                    self.columns[key]=value
                if 'LI_Demod_1_R' in ele:
                    key = 'dIdV'
                    value= (self.channels.index(ele))
                    self.columns[key]=value
                if 'LI_Demod_2_R' in ele:
                    key = 'd2IdV2'
                    value= (self.channels.index(ele))
                    self.columns[key]=value

               


        

