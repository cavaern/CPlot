import numpy as np
import matplotlib.pyplot as plt

class Line:
    def __init__(self, file_list, H):
        fig,ax=plt.subplots()
        
        Header=(H.header_lines +2)

        linescan=[]                                                                 #Making the lists for the dIdV, V and I data from the files
        linescanV=[]
        linescanI=[]

        if H.back:
            foot = (H.points/2) + H.points*(H.backnum-1)
        else:
            foot = 0

        for file in file_list:
                linescan.append(np.genfromtxt(file, skip_header=Header, skip_footer=int(foot), usecols=(H.didv+3)))   #Going through all files in the folder with the chosen name and extracting the dIdV values. They are put in a list as 1D arrays.
        for file in file_list:
                linescanI.append(np.genfromtxt(file, skip_header=Header, skip_footer=int(foot), usecols=(H.i+3)))  #Make an list of 1D arrays with the current data
        for file in file_list:
                linescanV.append(np.genfromtxt(file, skip_header=Header, skip_footer=int(foot), usecols=(1)))  #Same for V
                
        try:
            self.data=np.vstack(linescan).T
            dataV=np.vstack(linescanV).T
            dataI=np.vstack(linescanI).T
            self.avr=self.data.mean(axis=1)
            datanormI=np.divide(self.data,abs(dataI))
            self.datanorm=np.multiply(datanormI,abs(dataV))
            self.avrnorm=self.datanorm.mean(axis=1)
        except ValueError:
            pass
                             
        #Make a 2D array of the list of arrays 'linescan' and transpose to make sure the voltage is on the Y axis
        self.V = np.genfromtxt(file, skip_header=Header, skip_footer=int(foot), usecols=(1))                        #Make an array of the bias data                                                           #Take end bias
                     
    
