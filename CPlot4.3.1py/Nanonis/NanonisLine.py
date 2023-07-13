import numpy as np
import matplotlib.pyplot as plt
import math
import PySimpleGUI as sg
from scipy.signal import savgol_filter

class Line:
    def __init__(self, file_list, H, channel, fil, der, bck, norm):
        filsetwin, filsetpoly = fil[1], fil[2]
        if bck == 'no':
            back = False
        else:
            try:
                a = H.columns['dIdV[bwd]']
                back = True
            except KeyError:
                back = False
                sg.popup('No backward channel recorded.')

        Header=(len(H.header)+1)

        test=False
        self.V = np.genfromtxt(file_list[0], skip_header=Header, usecols=(H.columns['V']))
        is_NaN = math.isnan(self.V[0])
        while is_NaN:
            Header += 1
            self.V = np.genfromtxt(file_list[0], skip_header=Header, usecols=(H.columns['V']))
            is_NaN = math.isnan(self.V[0])

        linescan = []   #Making the lists for the dIdV, V and I data from the files
        linescanV = []
        linescanI = []

        linescanback=[]
        linescanIback=[]

        for file in file_list:
            dIdV = np.genfromtxt(file, skip_header=Header, usecols=(H.columns[channel]))
            I = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['I']))
            V = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['V']))
            if back:
                dIdVbwd = np.genfromtxt(file, skip_header=Header, usecols=(H.columns[f'{channel}[bwd]']))
                Ibwd = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['I[bwd]']))
                for c, v in enumerate(dIdV):
                    dIdV[c] += dIdVbwd[c]
                    dIdV[c] /= 2
                    I[c] += Ibwd[c]
                    I[c] /= 2
            if fil[0] == 'Savinsky-Golay':
                dIdV = savgol_filter(dIdV, filsetwin, filsetpoly)
            if der == 'dy/dx':
                dIdV = -np.gradient(dIdV)
            if der == 'abs(dy/dx)':
                dIdV = abs(np.gradient(dIdV))
            linescan.append(dIdV)
            linescanI.append(I)
            linescanV.append(V)

        try:
            self.data = np.vstack(linescan).T
            self.hdata = np.stack(linescan, axis=0).T

            dataV = np.vstack(linescanV).T
            hdataV = np.stack(linescanV, axis=0).T
            dataI = np.vstack(linescanI).T
            hdataI = np.stack(linescanI, axis=0).T

           
            dataI = abs(dataI)
            dataI = dataI + 1e-12

            hdataI = abs(hdataI)
            self.hdataI = hdataI
            hdataI = hdataI + 1e-12
            
            if norm == 'dIdV/(I/V)':
                datanormI=np.divide(self.data,dataI)
                self.data=np.multiply(datanormI,abs(dataV))

                hdatanormI = np.divide(self.hdata,hdataI)
                self.hdata=np.multiply(hdatanormI,abs(hdataV))
            
            self.avr=self.data.mean(axis=1)
            self.avrI=dataI.mean(axis=1)

            self.havr = self.hdata.mean(axis=0)
            self.havrI = hdataI.mean(axis=0)
        except ValueError:
            pass
                             
        #Make a 2D array of the list of arrays 'linescan' and transpose to make sure the voltage is on the Y axis
        #self.V = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['V']))                        #Make an array of the bias data                                                           #Take end bias
                    
