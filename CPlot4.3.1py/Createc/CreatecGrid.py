import struct as struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widg
import PySimpleGUI as sg
#import CreatecHeader as CH

class Grid:
    def __init__(self, file,H):  
        declist = []
        dIdVspec=[]
        dIdV=[]

        
        with open (file, 'rb') as f:
            contents=f.read()
            
        decode = struct.iter_unpack("f",contents)
        
        for elem in decode:
            declist.append(elem)
        
        for n in range(0,H.spectra):
            for i in range(0,H.points):
                try:
                    dIdVspec.append(declist[H.skip+2*H.points+H.didv+i*H.columns+n*H.columns*H.points])
                except IndexError:
                    break
                i += 1
            dIdV.append(dIdVspec)
            dIdVspec=[]
            n+=1
            
        self.griddic={}
        dIdVgrid = np.empty(shape=(H.GridY,H.GridX))
        
        count=0
        for k in range (0,H.points):
            for n in range(0,H.GridY):
                for m in range(0,H.GridX):
                    try:
                        dIdVgrid[n,m]=(dIdV[count][k][0])*19*10E-15
                    except IndexError:
                        break
                    count+=1
                    m+=1
                n+=1
            self.griddic['{}'.format(k)]= dIdVgrid
            dIdVgrid = np.empty(shape=(H.GridY,H.GridX))
            count=0
            k+=1

        self.V=[]
        for n in range(0,H.points):
            self.V.append(declist[H.skip+2*n])


##file=r'E:\Documenten\Python\Natuurkunde\CPlot v3\Createc Grid\TSTM-201114.102533.specgrid'
##H=CH.Grid(file)
##a=Grid(file,H)
