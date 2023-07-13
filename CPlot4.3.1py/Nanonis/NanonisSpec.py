import numpy as np
import matplotlib.pyplot as plt
import math

class Spectrum:
    def __init__(self, file, H):
        Header=(len(H.header)+1)

        test=False
        self.V = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['V']))
        is_NaN = math.isnan(self.V[0])
        while is_NaN:
            Header += 1
            self.V = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['V']))
            is_NaN = math.isnan(self.V[0])

        self.dIdV = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['dIdV']))                                                            #Making the lists for the dIdV, V and I data from the files
        self.I = np.genfromtxt(file, skip_header=Header, usecols=(H.columns['I']))
