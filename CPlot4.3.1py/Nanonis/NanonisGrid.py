import struct as struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widg
import PySimpleGUI as sg
from itertools import islice
from scipy.signal import savgol_filter
from scipy.misc import derivative

class Grid:
    def __init__(self, file,H, demod, fil, der, back, size):
        if size[1] > size[0]:
            X1, X2 = size[0], size[1]
        else:
            X2, X1 = size[0], size[1]
        if size[3] > size[2]:
            Y1, Y2 = size[2], size[3]
        else:
            Y2, Y1 = size[2], size[3]

        filsetwin, filsetpoly = fil[1],fil[2]
        grid = []
        dIdVgrid=[]
        Igrid=[]
        Zgrid=[]
        spectra=H.GridX*H.GridY
        
        with open (file, 'rb') as f:
            for line in islice(f, (len(H.header)-1), None):
                contents = f.read()
            
        decode = struct.iter_unpack(">f",contents)
        
        for elem in decode:
            grid.append(elem)

        self.V=[]
        for n in range(0,H.points):
            self.V.append(grid[H.points*H.columns['V']+H.para+n])
        
        skip=H.points*len(H.channels)+H.para
        
        start=H.points*H.columns[demod]+H.para
        end=H.points*(H.columns[demod]+1)+H.para

        if 'dIdV[bwd]' in H.columns:
            startbwd = H.points * H.columns['{}[bwd]'.format(demod)] + H.para
            endbwd = H.points * (H.columns['{}[bwd]'.format(demod)] + 1) + H.para
        else:
            startbwd = start
            endbwd = end
        a = 0
        for n in range(0,spectra):
            try:
                if fil[0] == 'Savinsky-Golay':
                    dIdV=savgol_filter(np.ravel(grid[(start+n*skip):(end+n*skip)]), filsetwin, filsetpoly)
                    dIdVbwd=savgol_filter(np.ravel(grid[(startbwd+n*skip):(endbwd+n*skip)]), filsetwin, filsetpoly)
                else:
                    dIdV = np.ravel(np.array(grid[(start + n * skip):(end + n * skip)]))
                    dIdVbwd = np.ravel(np.array(grid[(startbwd + n * skip):(endbwd + n * skip)]))
                if back == 'yes':
                    for c, v in enumerate(dIdV):
                        dIdV[c] += dIdVbwd[c]
                        dIdV[c] /= 2
                if der == 'dy/dx':
                    dIdV=abs(np.gradient(dIdV))
                if len(dIdV) == H.points:
                    dIdVgrid.append(dIdV)
                    n+=1
            except IndexError:
                break
           
            
        for n in range(0, spectra):
            try:
                Z = grid[H.Z + n*skip]
            except IndexError:
                break
            Zgrid.append(Z)
            
        data=np.array(dIdVgrid)

        dataZ = np.array(Zgrid)
        datagridZ = np.empty(shape=(H.GridY,H.GridX))
        count = 0
        for n in range(0, H.GridY):
            for m in range(0, H.GridX):
                try:
                    datagridZ[n, m] = dataZ[count]
                except IndexError:
                    break
                count += 1
                m += 1
            n += 1

        averx=[0,0]
        avery=[0,0]
        datagridZlin = np.copy(datagridZ)

        try:
            for j in range (0,H.GridX):
                y=datagridZ[j,:]
                x=np.arange(0,H.GridX) 
                z=np.polyfit(x,y,1)
                averx += z/H.GridX
            for k in range (0,H.GridY):
                y=datagridZ[:,k]
                x=np.arange(0,H.GridY)
                z=np.polyfit(x,y,1)
                avery += z/H.GridY
            for m in range (0,H.GridX):
                datagridZlin[m,:]-=np.arange(0,H.GridX)*averx[0]+averx[1]
            for n in range (0,H.GridY):
                datagridZlin[:,n]-=np.arange(0,H.GridY)*avery[0]
        except IndexError:
            pass

        startI=H.points*H.columns['I']+H.para
        endI=H.points*(H.columns['I']+1)+H.para

        if 'dIdV[bwd]' in H.columns:
            startIbwd= H.points * H.columns['I[bwd]'] + H.para
            endIbwd = H.points * (H.columns['I[bwd]'] + 1) + H.para
        else:
            startIbwd = startI
            endIbwd = endI

        for n in range(0,spectra):
            try:
                if fil[0] == 'Savinsky-Golay':
                    I = savgol_filter(np.ravel(grid[(startI + n * skip):(endI + n * skip)]), filsetwin, filsetpoly)
                    Ibwd = savgol_filter(np.ravel(grid[(startIbwd + n * skip):(endIbwd + n * skip)]), filsetwin, filsetpoly)
                else:
                    I = np.ravel(np.array(grid[(startI+n*skip):(endI+n*skip)]))
                    Ibwd = np.ravel(np.array(grid[(startIbwd + n * skip):(endIbwd + n * skip)]))
                if back == 'yes':
                    for c, v in enumerate(dIdV):
                        I[c] += Ibwd[c]
                        I[c] /= 2
                if len(I) == H.points:
                    Igrid.append(I)
                    n+=1
            except IndexError:
                break



        dataI = np.array(Igrid)

        dataI = np.abs(dataI)

        dataI = dataI + 1e-12

        
        datanorm=np.divide(data,dataI)
        
        datagrid = np.empty(shape=(H.GridY,H.GridX))
        self.griddic={}
        count=0
        
        for k in range (0,H.points):
            for n in range(0,H.GridY):
                for m in range(0,H.GridX):
                    try:
                        datagrid[n,m]=data[count,k]
                    except IndexError:
                        break
                    count+=1
                    m+=1
                n+=1
            self.griddic['{}'.format(k)]= datagrid[Y1:Y2, X1:X2]
            datagrid = np.empty(shape=(H.GridY,H.GridX))
            count=0
            k+=1

        datagridI = np.empty(shape=(H.GridY,H.GridX))
        self.griddicI={}
        count=0
        
        for k in range (0,H.points):
            for n in range(0,H.GridY):
                for m in range(0,H.GridX):
                    try:
                        datagridI[n,m]=dataI[count,k]
                    except IndexError:
                        break
                    count+=1
                    m+=1
                n+=1
            self.griddicI['{}'.format(k)]= datagridI[Y1:Y2, X1:X2]
            datagridI = np.empty(shape=(H.GridY,H.GridX))
            count=0
            k+=1

        
        datagridnorm = np.empty(shape=(H.GridY,H.GridX))
        self.griddicnorm={}
        count=0

        
        for k in range (0,H.points):
            for n in range(0,H.GridY):
                for m in range(0,H.GridX):
                    try:
                        datagridnorm[n,m]=datanorm[count,k]
                    except IndexError:
                        break
                    count+=1
                    m+=1
                n+=1
            self.griddicnorm['{}'.format(k)]= datagridnorm[Y1:Y2, X1:X2]*(abs(self.V[k][0]*1000))
            datagridnorm = np.empty(shape=(H.GridY,H.GridX))
            count=0
            k+=1
    
        self.griddic['Z'] = datagridZlin
        self.griddicnorm['Z'] = datagridZlin

        self.gridavr = []
        for k in range (0, H.points):
            self.gridavr.append(np.average(self.griddic['{}'.format(k)]))
            
        self.gridavrI = []
        for k in range (0, H.points):
            self.gridavrI.append(np.average(self.griddicI['{}'.format(k)]))

        self.gridavrnorm = []
        for k in range (0, H.points):
            self.gridavrnorm.append(np.average(self.griddicnorm['{}'.format(k)]))
