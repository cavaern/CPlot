import struct as struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widg
import PySimpleGUI as sg
from itertools import islice

class MP:
    def __init__(self, file,H):
        mp = []
        pixels=H.GridX*H.GridY
        
        if H.back:
            b = 2
        elif not H.back:
            b =1
        with open (file, 'rb') as f:
            for line in islice(f, (H.header-1), None):
                contents = f.read()
            
        decode = struct.iter_unpack(">f",contents[2:])
        
        for elem in decode:
            mp.append(elem)

        datamp = np.empty(shape=(H.GridY,H.GridX))
        self.mpdic={}
        count=0
        
        for k in range (0,H.total):
            for n in range (0, H.GridY):
                for m in range (0, H.GridX):
                    datamp[n,m]=mp[count][0]
                    count+=1
                    m+=1
                n+=1
            self.mpdic['{}'.format(k)]= datamp
            datamp = np.empty(shape=(H.GridY,H.GridX))
            k+=1

        self.V=sorted(H.V) 
        self.zdic={}
        self.idic={}
        self.vdic={}
        self.didvdic={}
        self.d2idv2dic={}
        
        for ele in H.columns:
            if 'Z' in ele:
                for i in range (0,H.points//b):
                    self.zdic['{}'.format(H.V[b*i])]=self.mpdic['{}'.format(H.columns['Z']*b+H.channelnum*i*b)]
                    if b == 2:
                        self.zdic['{}'.format(H.V[b*i+1])]=np.flip(self.mpdic['{}'.format(1+H.columns['Z']*b+H.channelnum*i*b)],1)
            if 'I' in ele:
                for i in range (0,H.points//b):
                    self.idic['{}'.format(H.V[b*i])]=self.mpdic['{}'.format(H.columns['I']*b+H.channelnum*i*b)]
                    if b == 2:
                        self.idic['{}'.format(H.V[b*i+1])]=np.flip(self.mpdic['{}'.format(1+H.columns['I']*b+H.channelnum*i*b)],1)
            if 'dIdV' in ele:
                for i in range (0,H.points//b):
                    self.didvdic['{}'.format(H.V[b*i])]=self.mpdic['{}'.format(H.columns['dIdV']*b+H.channelnum*i*b)]
                    if b == 2:
                        self.didvdic['{}'.format(H.V[b*i+1])]=np.flip(self.mpdic['{}'.format(1+H.columns['dIdV']*b+H.channelnum*i*b)],1)
            if 'd2IdV2' in ele:
                for i in range (0,H.points//b):
                    self.d2idv2dic['{}'.format(H.V[b*i])]=self.mpdic['{}'.format(H.columns['d2IdV2']*b+H.channelnum*i*b)]
                    if b == 2:
                        self.d2idv2dic['{}'.format(H.V[b*i+1])]=np.flip(self.mpdic['{}'.format(1+H.columns['d2IdV2']*b+H.channelnum*i*b)],1)
            if ele == 'V':
                for i in range (0,H.points//b):
                    self.vdic['{}'.format(H.V[b*i])]=self.mpdic['{}'.format(H.columns['V']*b+H.channelnum*i*b)]
                    if b == 2:
                        self.vdic['{}'.format(H.V[b*i+1])]=np.flip(self.mpdic['{}'.format(1+H.columns['V']*b+H.channelnum*i*b)])
        averx=[0,0]
        avery=[0,0]
        self.zdiclin={}
        if self.zdic:
            for l in range (0,H.points):
                self.zdiclin['{}'.format(H.V[l])]=np.copy(self.zdic['{}'.format(H.V[l])])
            for l in range (0,H.points):
                yy=self.zdic['{}'.format(self.V[l])][:,H.GridX//2]
                xy=np.arange(0,H.GridY)
                zy=np.polyfit(xy,yy,1)
                avery += zy

                yx=self.zdic['{}'.format(self.V[l])][H.GridY//2,:]
                xx=np.arange(0,H.GridX)
                zx=np.polyfit(xx,yx,1)
                averx += zx

                print(averx, avery)
                
                for m in range (0,H.GridX):
                    self.zdiclin['{}'.format(H.V[l])][:,m]-=np.arange(0,H.GridY)*avery[0]
                for n in range (0,H.GridY):
                    self.zdiclin['{}'.format(H.V[l])][n,:]-=np.arange(0,H.GridX)*averx[0]
                averx=[0,0]
                avery=[0,0]


            
            
##        
##        start=points*H.columns['dIdV']*b
##        skip=points*len(H.channels)*b
##        end=points*(H.columns['dIdV']*b+1)
##        
##
#file=r'C:\Users\User\Desktop\CPlot\original data\VS2-Gr_2021_06_28_0020.sxm'
##file=r'C:\Users\User\Desktop\CPlot\original data\VS2-Gr - 1_2nm.sxm'
##H=NH.MP(file)
####
##a=MP(file,H)
