import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Nanonis.NanonisLine as NL
import Nanonis.NanonisHeader as NH
import Createc.CreatecLine as CL
import Createc.CreatecHeader as CH
import struct as struct
from matplotlib import colors
from matplotlib.colors import SymLogNorm
from scipy.fftpack import fft, fftfreq, rfft
from scipy.signal import savgol_filter
from scipy.misc import derivative
import matplotlib as mpl
from matplotlib.widgets import RangeSlider
from matplotlib.widgets import Slider
from math import pi
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from math import sqrt
from matplotlib.ticker import FormatStrFormatter





def Line():
    #New theme for user interface of PySimpleGui windows
    my_new_theme = {'BACKGROUND': '#B4B9C7',
                    'TEXT': '#023f4a',
                    'INPUT': '#f2f7fb',
                    'TEXT_INPUT': '#000000',
                    'SCROLL': '#3526CB',
                    'BUTTON': ('white', '#3526CB'),
                    'PROGRESS': ('#01826B', '#D0D0D0'),
                    'BORDER': 1,
                    'SLIDER_DEPTH': 0,
                    'PROGRESS_DEPTH': 0}
             
    sg.theme_add_new('CPlot', my_new_theme)


    SYMBOL_UP =    '▲'
    SYMBOL_DOWN =  '▼'
    
    #Dictionary of initial constants

    _VARS = {'window': False,
            'fig_agg': False,
             'pltFig': False,
             'dataSize': 0}


    #Mathplotlib theme
    plt.style.use('classic')
    mpl.rcParams['axes.facecolor'] = '#B4B9C7'
    mpl.rcParams['figure.facecolor'] = '#B4B9C7'
    mpl.rcParams['figure.edgecolor'] = '#B4B9C7'
    #mpl.rcParams['figure.autolayout']=True
    #plt.rcParams['figure.constrained_layout.use'] = True
    mpl.rcParams['font.sans-serif']='Arial'
    mpl.rcParams['font.size']=14
    plt.rcParams['axes.titlepad'] = 20

    interpolations=['none', 'hanning', 'gaussian', 'antialiased']
    cmaps=['gray', 'viridis', 'bwr', 'binary', 'afmhot', 'cividis']
    
    def collapse(layout, key):
        return sg.pin(sg.Column(layout, key=key))
    #Drawing a mathplotlib figure onto a canvas that can be integrated with a PySimpleGui window

    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    #Connecting the figure with the right canvas and window

    def makeData(fig, ax, cbar):
        draw_figure(_VARS['window']['figCanvas'].TKCanvas, fig)
        
    #Same as MakeData but for the FFT
        
    def makeDataFFT(fig, ax, cbar):
        draw_figure(win4['figCanvasFFT'].TKCanvas, fig)

    def makeDataAvr(fig, ax):
        draw_figure(win5['figCanvasAvr'].TKCanvas, fig)

    def makeDataHor(fig, ax):
        draw_figure(win6['figCanvasAvr'].TKCanvas, fig)

    #Update interpolation
      
    def updatePol(pol, fig, img):
        img.set_interpolation(pol)
        fig.canvas.draw_idle()
        
    #Update colormap
        
    def updateCol(col, fig, img):
        img.set_cmap(col)
        fig.canvas.draw_idle()

    
    #Update scale
    def updateLine(spectrum, data, val, files, der, norm):
        if der == 'y':
            derlab = 'dI/dV'
        if der == 'dy/dx':
            derlab = 'd2I/dV2'
        if der == 'abs(dy/dx)':
            derlab = 'abs(d2I/dV2)'
        if norm == 'dIdV/(I/V)':
            norlab = '/(I/V)'
        if norm == 'dIdV':
            norlab = ''
        axAvr.clear()

        if spectrum != 'Average':
            spec=axAvr.plot(G.V, data[:,speclist.index(spectrum)-1])
        else:
            spec=axAvr.plot(G.V,data.mean(axis=1))

        if spectrum != 'Average':
            x = (speclist.index(spectrum)-1)*length/(len(speclist)-2)
            line=ax.axvline(x=x,color='red', ymin=0, ymax=1, linewidth=4)
            fig.canvas.draw_idle()
        else:
            line=ax.axvline(x=0)
            fig.canvas.draw_idle()
        if spectrum != 'Average':
            axAvr.set_title('{}'.format(spectrum))
        else:
            name=files[0].split('/')
            axAvr.set_title('Average of {}'.format(name[-1]))
        axAvr.set(xlabel='Energy (eV)', ylabel = f'{derlab}{norlab} (a.u.)')
        axAvr.set_xlim([float(val['minX']),float(val['maxX'])])
        axAvr.set_ylim([float(val['minY']),float(val['maxY'])])
        axAvr.yaxis.set_major_formatter(FormatStrFormatter('%.1g'))
        figAvr.canvas.draw_idle()
        return line, spec

            
    def updatePlot(val):
        axAvr.set_xlim([float(val['minX']),float(val['maxX'])])
        axAvr.set_ylim([float(val['minY']),float(val['maxY'])])
        figAvr.canvas.draw_idle()

    # Update scale
    def updateHLine(spectrum, data, val, files, der, norm):
        if der == 'y':
            derlab = 'dI/dV'
        if der == 'dy/dx':
            derlab = 'd2I/dV2'
        if der == 'abs(dy/dx)':
            derlab = 'abs(d2I/dV2)'
        if norm == 'dIdV/(I/V)':
            norlab = '/(I/V)'
        if norm == 'dIdV':
            norlab = ''
        axHor.clear()

        if spectrum != 0:
            spec = axHor.plot(np.linspace(0,length,len(files)), data[spectrum-1,:])
        else:
            spec = axHor.plot(np.linspace(0,length,len(files)), G.havr)

        if spectrum != 0:
            y = G.V[spectrum-1]
            line = ax.axhline(y=y, color='red', xmin=0, xmax=1, linewidth=4)
            fig.canvas.draw_idle()
        else:
            line = ax.axhline(y=0)
            fig.canvas.draw_idle()
        if spectrum != 0:
            axHor.set_title('{} eV'.format(round(G.V[spectrum-1], 5)))
        else:
            name = files[0].split('/')
            axHor.set_title('dIdV(x) average of {}'.format(name[-1]))
        axHor.set(xlabel='Distance (nm)', ylabel=f'{derlab}{norlab} (a.u.)')
        axHor.set_xlim([float(val['minX']), float(val['maxX'])])
        axHor.set_ylim([float(val['minY']), float(val['maxY'])])
        axHor.yaxis.set_major_formatter(FormatStrFormatter('%.1g'))
        figHor.canvas.draw_idle()
        return line, spec

    def updateHPlot(val):
        axHor.set_xlim([float(val['minX']), float(val['maxX'])])
        axHor.set_ylim([float(val['minY']), float(val['maxY'])])
        figHor.canvas.draw_idle()
        

    #When the range slider is moved the image and histogram are updated

    def updateScaRan(val):
        if val['sca'] == 'Log':
            img.set_norm(SymLogNorm(1E-15,vmin=val['min'], vmax=val['max']))
        if val['sca'] == 'Linear':
            img.set_norm(None)
            img.norm.vmin = float(val['min'])
            img.norm.vmax = float(val['max'])

        cbar.update_normal(img)
        fig.canvas.draw_idle()

    def updateRanFFT(val):
        if val['sca'] == 'Log':
            imgFFT.set_norm(SymLogNorm(1E-15,vmin=val['min'], vmax=val['max']))
        if val['sca'] == 'Linear':
            imgFFT.set_norm(None)
            imgFFT.norm.vmin = float(val['min'])
            imgFFT.norm.vmax = float(val['max'])
        
        axFFT.set_xlim(float(val['minX']), float(val['maxX']))
        axFFT.set_ylim(float(val['minY']), float(val['maxY']))
        
        cbarFFT.update_normal(imgFFT)
        
        figFFT.canvas.draw_idle()


    def updateRan(val):
        ax.set_xlim(float(val['minX']), float(val['maxX']))
        ax.set_ylim(float(val['minY']), float(val['maxY']))
        
        img.norm.vmin = float(val['min'])
        img.norm.vmax = float(val['max'])
        

        cbar.update_normal(img)
        
        fig.canvas.draw_idle()
                 

    def MakeFig(files, channel, fil, der, back, norm):
        #Layout of the figure
        fig,ax=plt.subplots()
        plt.subplots_adjust(bottom=0.25)

        #Extracting the header info
        if files[0].endswith('.dat'):
            H=NH.Header(files[0])
            HE=NH.Header(files[-1])
            G=NL.Line(files,H, channel, fil, der, back, norm)
            length=pow(pow((H.X-HE.X),2) + pow((H.Y-HE.Y),2),0.5)*1e9
            if length == 0:
                length = len(files)
                ax.set(xlabel='# of files', ylabel='Energy (eV)')
            else:
                ax.set(xlabel='x (nm)', ylabel='Energy (eV)')
                
        elif files[0].endswith('.VERT'):
            H=CH.Header(files[0])
            G=CL.Line(files,H)
            length=sg.Window('CPlot', [[sg.T("Length of scan:", size=(23,1)), sg.In(size=(10,1)), sg.T('nm')],
              [sg.B('Ok')]]).read(close=True)[1][0]
            try:
                length=float(length)
                ax.set(xlabel='x (nm)', ylabel='Energy (meV)')
            except ValueError:
                length=len(files)
                ax.set(xlabel='Number of spectra', ylabel='Energy (meV)')

        #Obtaining the grid in a plottable format
        name=files[0].split('/')
        ax.set_title('{}'.format(name[-1]))
        plt.title('{}'.format(name[-1]))
        try:
            img=ax.imshow(G.data, cmap='bwr', interpolation='none', norm=None, aspect='auto', extent=(0,length,G.V[-1],G.V[0]))
            cbar = fig.colorbar(img, ax=ax)
            return fig, ax, img, cbar, H, G, length
        except AttributeError:
                pass

       
    def MakeFFT(files, data):
        figFFT,axFFT=plt.subplots()
        figFFT.set_size_inches(6, 6)
        
        linefft=[]
        
        name=files[0].split('/')
        axFFT.set_title('FFT')
        axFFT.set(xlabel='q (nm-1)', ylabel='Energy (eV)')
        
        xf=fftfreq(len(files), length/len(files))[:len(files)//2]
        for i in range (0,(len(G.V)-1)):
            yf=np.abs(rfft(data[i,:])[0:len(files)//2])
            linefft.append(yf)
            i+=1

        datafft=np.vstack(linefft)
        #end=(pi)*xf[(len(files)//2)-1]
        end=(pi)*1/(length*2/len(files))
        imgFFT=axFFT.imshow(abs(datafft), cmap='bwr', interpolation=None, aspect='auto', norm=SymLogNorm(1E-15), extent=(0,end,G.V[-1],G.V[0]))
        cbarFFT = figFFT.colorbar(imgFFT, ax=axFFT)

        return imgFFT, figFFT, axFFT, cbarFFT, end
        

    def MakeAvr(files,data, der, norm):
        if der == 'y':
            derlab = 'dI/dV'
        if der == 'dy/dx':
            derlab = 'd2I/dV2'
        if der == 'abs(dy/dx)':
            derlab = 'abs(d2I/dV2)'
        if norm == 'dIdV/(I/V)':
            norlab = '/(I/V)'
        if norm == 'dIdV':
            norlab = ''
        figAvr,axAvr = plt.subplots()

        spec=axAvr.plot(G.V, data)
        
        name=files[0].split('/')
        axAvr.set_title('Average of {}'.format(name[-1]))
        
        if files[0].endswith('.dat'):
            axAvr.set(xlabel='Energy (eV)', ylabel=f'{derlab}{norlab} (a.u.)')
        elif files[0].endswith('.VERT'):
            axAvr.set(xlabel='Energy (meV)', ylabel='dIdV (a.u.)')
        axAvr.yaxis.set_major_formatter(FormatStrFormatter('%.1g'))
        return figAvr, axAvr, spec
    
    def MakeHor(files, data, der, norm):
        if der == 'y':
            derlab = 'dI/dV'
        if der == 'dy/dx':
            derlab = 'd2I/dV2'
        if der == 'abs(dy/dx)':
            derlab = 'abs(d2I/dV2)'
        if norm == 'dIdV/(I/V)':
            norlab = '/(I/V)'
        if norm == 'dIdV':
            norlab = ''
        figHor,axHor = plt.subplots()

        spec = axHor.plot(np.linspace(0, length, len(files)), data)

        name = files[0].split('/')
        axHor.set_title(f'dIdV(x) average of {name[-1]}')
        
        if files[0].endswith('.dat'):
            axHor.set(xlabel='Distance (nm)', ylabel=f'{derlab}{norlab} (a.u.)')
        elif files[0].endswith('.VERT'):
            axHor.set(xlabel='Distance (x)', ylabel='dIdV (a.u.)')
        axHor.yaxis.set_major_formatter(FormatStrFormatter('%.1g'))
        return figHor, axHor, spec

    def LineWin():
        menu_def = [['&File', ['&Open', '&Save', ['Save Scan', ['Image', 'ASCII file', 'ASCII file Hor'], 'Save FFT', 'Save Spectrum', ['Image Spec', 'ASCII file Avr'],
                                                  'Save H-Spectrum', ['Image H-Spec', 'ASCII file H-Avr']],'---', 'E&xit'  ]],
                ['&Plot Options', ['Advanced', 'Set Range', 'FFT', 'Spectra', 'Horizontal Spectra', 'Channel', ['dIdV', 'd2IdV2']],],
                ['&Help', '&About...'],]


        layout = [[sg.Menu(menu_def)],[sg.Canvas(key='figCanvas', background_color='#B4B9C7')],
                                       [sg.B('Exit', pad=((240, 10), (0, 0)))]]



        return sg.Window('CPlot Linescan Window',
                                layout,
                                finalize=True,
                                resizable=True,
                                location=(100, 100),
                                element_justification="center",
                                background_color='#B4B9C7',
                                modal=False)


    def AdvWin():
        layout2=[[sg.T("Interpolation",size=(23, 1), justification='left'), sg.Combo(values=interpolations, size=(20,3), default_value='none', key='pol', enable_events=True)],
            [sg.T("Colormap", size=(23, 1), justification='left'), sg.Combo(values=cmaps, size=(20,3), default_value='bwr', key='col', enable_events=False)],
            [sg.T("Normalize", size=(23, 1), justification='left'), sg.Combo(values=['dIdV', 'dIdV/(I/V)'], size=(20,3), default_value=norm, key='nor', enable_events=False)],
            [sg.T("Filter", size=(23, 1), justification='left'), sg.Combo(values=['none', 'Savinsky-Golay'], size=(20,3), default_value=fil[0], key='fil', enable_events=False)],
            [sg.T('Filter Window',size=(23, 1), justification='left'), sg.Combo(values=[5, 7, 11, 15, 21], key='filwin', enable_events=True, default_value=fil[1], size=(20,3))],
            [sg.T('Filter Polynomial',size=(23, 1), justification='left'), sg.Combo(values=[1, 2, 3, 4], key='filpol', enable_events=True, default_value=fil[2], size=(20,3))],    
            [sg.T("Derivative", size=(23, 1), justification='left'), sg.Combo(values=['y', 'dy/dx', 'abs(dy/dx)'], size=(20,3), default_value=der, key='der', enable_events=False)],
            [sg.T("Bwd average", size=(23, 1), justification='left'), sg.Combo(values=['yes', 'no'], size=(20, 3), default_value=back, key='bwd', enable_events=False)],
            [sg.B('Exit')]]

        return sg.Window('Advanced',
                     layout2,
                     finalize=True,
                     resizable=True,
                     location=(800, 100),
                     element_justification="center",
                     background_color='#B4B9C7',
                     modal=False)


    def RangeWin(length):
        layout3=[[sg.T('Minimum X (nm)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= 0, size=(20,3))],
        [sg.T('Maximum X (nm)',size=(23, 1), justification='left'), sg.In(key='maxX', enable_events=True, default_text= round(length,2), size=(20,3))],
        [sg.T('Minimum Y (nm)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text= round(G.V[-1],2), size=(20,3))],
        [sg.T('Maximum Y (nm)',size=(23, 1), justification='left'), sg.In(key='maxY', enable_events=True, default_text= round(G.V[0],2), size=(20,3))],
        [sg.T('Minimum of cbar',size=(23, 1), justification='left'), sg.In(key='min', enable_events=True, default_text= format(G.data.min(),'.2e'), size=(20,3))],
        [sg.T('Maximum of cbar',size=(23, 1), justification='left'), sg.In(key='max', enable_events=True, default_text= format(G.data.max(),'.2e'), size=(20,3))],
        [sg.T("Scale", size=(23, 1), justification='left'), sg.Combo(values=['Linear', 'Log'], size=(20,3), default_value='Linear', key='sca', enable_events=True)],
        [sg.B('Set'), sg.B('Exit')]]

        return sg.Window('Set Range',
                         layout3,
                         finalize=True,
                         resizable=True,
                         location=(800, 300),
                         element_justification="center",
                         background_color='#B4B9C7',
                         modal=False)

    def FFTWin(end):
        layout4 = [[sg.Canvas(key='figCanvasFFT', background_color='#B4B9C7')],
                   [sg.T("Interpolation",size=(23, 1), justification='left'), sg.Combo(values=interpolations, size=(20,3), default_value='none', key='pol', enable_events=True)],
            [sg.T("Colormap", size=(23, 1), justification='left'), sg.Combo(values=cmaps, size=(20,3), default_value='bwr', key='col', enable_events=False)],
            [sg.T('Range cbar',size=(23, 1), justification='left'), sg.In(key='min', enable_events=True, default_text= format(G.data.min(),'.2e'), size=(10,3)),
            sg.In(key='max', enable_events=True, default_text= format(G.data.max(),'.2e'), size=(10,3))],
            [sg.T('Range (nm-1)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= 0, size=(10,3)),
             sg.In(key='maxX', enable_events=True, default_text= end, size=(10,3))],
            [sg.T('Energy (eV)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text= G.V[-1], size=(10,3)),
             sg.In(key='maxY', enable_events=True, default_text= G.V[0], size=(10,3))],
            [sg.T("Scale", size=(23, 1), justification='left'), sg.Combo(values=['Linear', 'Log'], size=(20,3), default_value='Linear', key='sca', enable_events=True)],
        [sg.B('Set'), sg.Button('Exit', pad=((140, 10), (0, 0)))]]

        return sg.Window('FFT',
                        layout4,
                        finalize=True,
                        resizable=True,
                        location=(800,500),
                        element_justification="center",
                        background_color='#B4B9C7',
                        modal=False)

    def AvrWin(speclist):
        
        section1 = [[sg.Slider(range=(len(G.V)-1,0), size=(40, 10), orientation="h",
                enable_events=True, text_color='red', default_value=0, key="voltageslid1"), sg.T('x1 = {} meV, y1 = - nA'.format(G.V[0]), key='voltagetext1', size=(30,0))],
                    [sg.Slider(range=(len(G.V)-1,0), size=(40, 10), orientation="h",
                enable_events=True, default_value=0, key="voltageslid2"), sg.T('x2 = {} meV, y2 = - nA'.format(G.V[0]), key='voltagetext2', size=(30,0))],
                    [sg.T('dx = - meV, dy = - nA', key='voltagetext3', size=(68,0), justification = 'right')]]
        
        layout5 = [[sg.Canvas(key='figCanvasAvr', background_color='#B4B9C7')],
                   #[sg.Combo(values=speclist, size = (50,3), key = 'spec', default_value = 'Average', enable_events=True)],
        [sg.T('V range (eV)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= G.V[-1], size=(10,3)),
         sg.In(key='maxX', enable_events=True, default_text= G.V[0], size=(10,3))],
        [sg.T('dIdV range (A)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text=format(G.avr.min(), '.2e') , size=(10,3)),
         sg.In(key='maxY', enable_events=True, default_text= format(G.avr.max(), '.2e'), size=(10,3))],
        [sg.Slider(range=(0, (len(speclist)-1)), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="slider")],
        [sg.T(SYMBOL_DOWN, enable_events=True, k='-OPEN SEC1-', text_color='blue'), sg.T('Peak Finder', enable_events=True, text_color='blue', k='-OPEN SEC1-TEXT')],
            [collapse(section1, '-SEC1-')],
    [sg.B('Set'), sg.Button('Exit', pad=((140, 10), (0, 0)))]]

        return sg.Window('Spectra',
                        layout5,
                        finalize=True,
                        resizable=True,
                        location=(800,500),
                        element_justification="center",
                        background_color='#B4B9C7',
                        modal=False)
    
    def HorWin(speclist):
        
        section1 = [[sg.Slider(range=(0, len(speclist)-1), size=(40, 10), orientation="h",
                enable_events=True, text_color='red', default_value=0, key="voltageslid1"), sg.T('x1 = {} meV, y1 = - nA'.format(G.V[0]), key='voltagetext1', size=(30,0))],
                    [sg.Slider(range=(0, len(speclist)-1), size=(40, 10), orientation="h",
                enable_events=True, default_value=0, key="voltageslid2"), sg.T('x2 = {} meV, y2 = - nA'.format(G.V[0]), key='voltagetext2', size=(30,0))],
                    [sg.T('dx = - meV, dy = - nA', key='voltagetext3', size=(68,0), justification = 'right')]]
        
        layout6 = [[sg.Canvas(key='figCanvasAvr', background_color='#B4B9C7')],
                   #[sg.Combo(values=speclist, size = (50,3), key = 'spec', default_value = 'Average', enable_events=True)],
        [sg.T('X range (nm)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= 0, size=(10,3)),
         sg.In(key='maxX', enable_events=True, default_text= length, size=(10,3))],
        [sg.T('dIdV range (A)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text=format(G.havr.min(), '.2e') , size=(10,3)),
         sg.In(key='maxY', enable_events=True, default_text= format(G.havr.max(), '.2e'), size=(10,3))],
        [sg.Slider(range=(0, len(G.V)), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="slider")],
        [sg.T(SYMBOL_DOWN, enable_events=True, k='-OPEN SEC1-', text_color='blue'), sg.T('Peak Finder', enable_events=True, text_color='blue', k='-OPEN SEC1-TEXT')],
            [collapse(section1, '-SEC1-')],
    [sg.B('Set'), sg.Button('Exit', pad=((140, 10), (0, 0)))]]

        return sg.Window('Horizontal spectra',
                        layout6,
                        finalize=True,
                        resizable=True,
                        location=(800,500),
                        element_justification="center",
                        background_color='#B4B9C7',
                        modal=False)

    # Layout for GUI window
    AppFont = 'Any 16'
    SliderFont = 'Any 14'
    sg.theme('CPlot')

    # ------ Menu Definition ------ #


    win2_active = False
    win3_active = False
    win4_active = False
    win5_active = False
    win6_active = False
    
    opened1 = True
    clear = False

    norm = 'dIdV'
    channel = 'dIdV'
    fil = ['none', 11, 2]
    der = 'y'
    back = 'no'

    check = True
    
    files=''
    files=sg.Window('CPlot', [[sg.T("Select files", size=(23,1)), sg.FilesBrowse(file_types=(('Nanonis spectra','*.dat'),('Createc spectra','*.vert')))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']

    if files != '':
        try:
            filelist=files.split(';')
            try:
                fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                _VARS['window'] = LineWin()
                makeData(fig, ax, cbar)
            except TypeError:
                sg.popup('Not all spectra have the same dimension!')
                check = False
            except ValueError:
                sg.popup('There are incomplete spectra in the list!')
                check = False
        except AttributeError:
            sg.popup('You did not select any spectra!')
            check = False
            
    
    
    #Window loop
    while check:
        event, values = _VARS['window'].read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            plt.close('all')
            break
        if event == 'Open':
            files=sg.Window('CPlot', [[sg.T("Select files", size=(23,1)), sg.FilesBrowse(file_types=(('Nanonis spectra','*.dat'),('Createc spectra','*.vert')))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']
            if files != '':
                try:
                    filelist=files.split(';')
                    _VARS['window'].close()
                    _VARS['window'] = LineWin()
                    try:
                        fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                        plt.close('all')
                        makeData(fig, ax, cbar)
                    except TypeError:
                        sg.popup('Not all spectra have the same dimension!')
                except AttributeError:
                    pass
        if event ==  'Image':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'
                fig.savefig(filename)
            except AttributeError:
                pass
            fig.savefig(filename)
        if win4_active and event == 'Save FFT':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'        
                figFFT.savefig(filename)
            except AttributeError:
                pass
        if win5_active and event == 'Image Spec':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'        
                figAvr.savefig(filename)
            except AttributeError:
                pass
        if win6_active and event == 'Image H-Spec':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'
                figHor.savefig(filename)
            except AttributeError:
                pass
        if event == 'ASCII file Avr':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            name=filelist[0].split('/')
            if foldername != None:
                with open(r'{}\{}_avr.dat'.format(foldername, name[-1]), 'wb') as textfile:
                    np.savetxt(textfile, np.c_[G.V, G.avr, G.avrI],  header = 'CPlot file [V, dIdV, I]', comments = '#')
            else:
                pass
        if event == 'ASCII file H-Avr':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            name=filelist[0].split('/')
            if foldername != None:
                with open(r'{}\{}_horizontal_avr.dat'.format(foldername, name[-1]), 'wb') as textfile:
                    np.savetxt(textfile, np.c_[np.linspace(0,length,len(filelist)), G.havr, G.havrI],  header = 'CPlot file [x, dIdV, I]', comments = '#')
            else:
                pass
        if event == 'ASCII file':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            name=filelist[0].split('/')
            if foldername != None:
                with open(r'{}\{}.dat'.format(foldername, name[-1]), 'wb') as textfile:
                    np.savetxt(textfile, np.flip(G.data),  comments='')
            else:
                pass
        if event == 'ASCII file Hor':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            name=filelist[0].split('/')
            if foldername != None:
                with open(r'{}\{}_horizontal.dat'.format(foldername, name[-1]), 'wb') as textfile:
                    np.savetxt(textfile, np.flip(G.hdata),  comments='')
                for i in range(0, len(G.V)):
                    with open(r'{}\{}_horizontal_{} eV.dat'.format(foldername, name[-1], G.V[i]), 'wb') as textfile:
                        np.savetxt(textfile, np.c_[np.linspace(0,length,len(filelist)), G.hdata[i,:], G.hdataI[i,:]], header = 'CPlot file [x, dIdV, I]', comments='#')
            else:
                pass
##        if event == 'SPIP file':
##            foldername=sg.popup_get_folder('Choose folder for SPIP files')
##            if foldername != None:
##                with open(r'{}\{}_{}eV.asc'.format(foldername, name, round(G.V[slider2.val][0],3)), 'wb') as textfile:
##                    np.savetxt(textfile, np.flip(G.griddic['{}'.format(int(slider2.val))]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = nA\nChannel Name: dIdV\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y), comments='')
##            else:
##                pass
        if event == 'dIdV':
            channel = 'dIdV'
            _VARS['window'].close()
            _VARS['window'] = LineWin()
            fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
            makeData(fig, ax, cbar)
        if event  == 'd2IdV2':
            channel = 'd2IdV2'
            try:
                fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                _VARS['window'].close()
                _VARS['window'] = LineWin()
                makeData(fig, ax, cbar)
            except KeyError:
                channel = 'dIdV'
            
        if not win2_active and event == 'Advanced':
            win2_active = True
            win2=AdvWin()  
        if win2_active:
            event2, values2 = win2.read(timeout=100)
            if event2 == sg.WIN_CLOSED or event2 == 'Exit':
                win2_active=False
                win2.close()
            try:
                if values2['pol']:
                    updatePol(values2['pol'], fig, img)
            except TypeError:
                pass
            try:
                if values2['col']:
                    updateCol(values2['col'], fig, img)
            except TypeError:
                pass
            try:
                if values2['nor'] != norm:
                    norm = values2['nor']
                    try:
                        fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                        _VARS['window'].close()
                        _VARS['window'] = LineWin()
                        makeData(fig, ax, cbar)
                    except KeyError:
                        pass
            except TypeError:
                pass
            try:
                if values2['fil'] != fil[0] or values2['filwin'] != fil[1] or values2['filpol'] != fil[2]:
                    fil = [values2['fil'], values2['filwin'], values2['filpol']]
                    try:
                        fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                        _VARS['window'].close()
                        _VARS['window'] = LineWin()
                        makeData(fig, ax, cbar)
                    except KeyError:
                        pass
            except TypeError:
                pass
            try:
                if values2['der'] != der:
                    der = values2['der']
                    try:
                        fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                        _VARS['window'].close()
                        _VARS['window'] = LineWin()
                        makeData(fig, ax, cbar)
                    except KeyError:
                        pass
            except TypeError:
                pass
            try:
                if values2['bwd'] != back:
                    back = values2['bwd']
                    try:
                        fig, ax, img, cbar, H, G, length = MakeFig(filelist, channel, fil, der, back, norm)
                        _VARS['window'].close()
                        _VARS['window'] = LineWin()
                        makeData(fig, ax, cbar)
                    except KeyError:
                        pass
            except TypeError:
                pass
        if not win3_active and event == 'Set Range':
            win3_active = True
            win3 = RangeWin(length)
        if win3_active:
            event3, values3 = win3.read(timeout=100)
            if event3 == sg.WIN_CLOSED or event3 == 'Exit':
                win3_active=False
                win3.close()
            if event3 == 'Set':
                updateScaRan(values3)
                updateRan(values3)
        if not win4_active and event == 'FFT':
            win4_active = True
            imgFFT, figFFT, axFFT, cbarFFT, end= MakeFFT(filelist, G.data)
            win4=FFTWin(end)
            makeDataFFT(figFFT, axFFT, cbarFFT)   
        if win4_active:
            event4, values4 = win4.read(timeout=100)
            if event4 == sg.WIN_CLOSED or event4 == 'Exit':
                win4_active=False
                plt.close(figFFT)
                win4.close()
            try:
                if values4['pol']:
                    updatePol(values4['pol'], figFFT, imgFFT)
            except TypeError:
                pass
            try:
                if values4['col']:
                    updateCol(values4['col'], figFFT, imgFFT)
            except TypeError:
                pass
            if event4 == 'Set':
                updateRanFFT(values4)
        if not win5_active and not win6_active and event == 'Spectra':
            win5_active=True
            line=ax.axvline(x=0)
            lines1=ax.axhline(y=0)
            lines2=ax.axhline(y=0)
            speclist = ['Average']
            for elem in filelist:
                spectrum=elem.split('/')
                speclist.append(spectrum[-1])
  
            win5=AvrWin(speclist)
            figAvr, axAvr, spec = MakeAvr(filelist, G.avr, der, norm)
            makeDataAvr(figAvr, axAvr)
            x1 = G.V[0]
            y1 = spec[0].get_ydata()[0]
            x2 = G.V[0]
            y2 = spec[0].get_ydata()[0]
            point1=axAvr.scatter(x=G.V[0], y=spec[0].get_ydata()[0])
            point2=axAvr.scatter(x=G.V[0], y=spec[0].get_ydata()[0])
            linev1=axAvr.axvline(x=G.V[0])
            linev2=axAvr.axvline(x=G.V[0])
            lineh1=axAvr.axhline(y=spec[0].get_ydata()[0])
            lineh2=axAvr.axhline(y=spec[0].get_ydata()[0])
        if win5_active:
            event5, values5 = win5.read(timeout=100)
            if event5 == sg.WIN_CLOSED or event5 == 'Exit':
                win5_active=False
                plt.close(figAvr)
                line.remove()
                if not clear:
                    lines1.remove()
                    lines2.remove()
                    point1.remove()
                    point2.remove()
                    linev1.remove()
                    linev2.remove()
                    lineh1.remove()
                    lineh2.remove()
                fig.canvas.draw_idle()
                win5.close()
            if event5 == 'slider':
                spectrum = speclist[int(values5['slider'])]
                line.remove()
                line, spec=updateLine(spectrum, G.data, values5, filelist, der, norm)
                x1= spec[0].get_xdata()[int(values5['voltageslid1'])]
                y1= spec[0].get_ydata()[int(values5['voltageslid1'])]
                x2= spec[0].get_xdata()[int(values5['voltageslid2'])]
                y2= spec[0].get_ydata()[int(values5['voltageslid2'])]
                if not clear:
                    linev1=axAvr.axvline(x=x1,color='red', linewidth=1)
                    linev2=axAvr.axvline(x=x2,color='blue', linewidth=1)
                    lineh1=axAvr.axhline(y=y1,color='red', linewidth=1)
                    lineh2=axAvr.axhline(y=y2,color='blue', linewidth=1)
                    point1=axAvr.scatter(x1,y1)
                    point2=axAvr.scatter(x2,y2)
                    win5.Element('voltagetext1').update('x1 = {} meV, y1 = {} pA'.format(round(x1*1e3,2), round(y1*1e12,2)))
                    win5.Element('voltagetext2').update('x2 = {} meV, y2 = {} pA'.format(round(x2*1e3,2), round(y2*1e12,2)))
                    win5.Element('voltagetext3').update('dx = {} meV, dy = {} pA'.format(round(abs(x1-x2)*1e3,2), round(abs(y1-y2)*1e12,2)))
                figAvr.canvas.draw_idle()
            if event5 == 'Set':
                updatePlot(values5)
            try:
                if event5.startswith('-OPEN SEC1-'):
                    opened1 = not opened1
                    clear = not clear
                    if clear:
                        lines1.remove()
                        lines2.remove()
                        point1.remove()
                        point2.remove()
                        linev1.remove()
                        linev2.remove()
                        lineh1.remove()
                        lineh2.remove()
                    if not clear:
                        lines1=ax.axhline(y=x1, color='red')
                        lines2=ax.axhline(y=x2, color='blue')
                        linev1=axAvr.axvline(x=x1,color='red', linewidth=1)
                        linev2=axAvr.axvline(x=x2,color='blue', linewidth=1)
                        lineh1=axAvr.axhline(y=y1,color='red', linewidth=1)
                        lineh2=axAvr.axhline(y=y2,color='blue', linewidth=1)
                        point1=axAvr.scatter(x1,y1)
                        point2=axAvr.scatter(x2,y2)
                    fig.canvas.draw_idle()
                    figAvr.canvas.draw_idle()
                    win5['-OPEN SEC1-'].update(SYMBOL_DOWN if opened1 else SYMBOL_UP)
                    win5['-SEC1-'].update(visible=opened1)
            except AttributeError:
                pass
            if event5 == 'voltageslid1':
                linev1.remove()
                lineh1.remove()
                point1.remove()
                lines1.remove()
                x1= spec[0].get_xdata()[int(values5['voltageslid1'])]
                y1= spec[0].get_ydata()[int(values5['voltageslid1'])]
                x2= spec[0].get_xdata()[int(values5['voltageslid2'])]
                y2= spec[0].get_ydata()[int(values5['voltageslid2'])]
                win5.Element('voltagetext1').update('x1 = {} meV, y1 = {} pA'.format(round(x1*1e3,2), round(y1*1e12,2)))
                win5.Element('voltagetext3').update('dx = {} meV, dy = {} pA'.format(round(abs(x1-x2)*1e3,2), round(abs(y1-y2)*1e12,2)))
                #x1 = G.V[int(values5['voltageslid1'])]
                linev1=axAvr.axvline(x=x1,color='red',linewidth=1)
                lineh1=axAvr.axhline(y=y1,color='red',  linewidth=1)
                point1=axAvr.scatter(x1,y1, color='red')
                lines1=ax.axhline(y=x1, color='red')
                figAvr.canvas.draw_idle()
                fig.canvas.draw_idle()
            if event5 == 'voltageslid2':
                linev2.remove()
                lineh2.remove()
                point2.remove()
                lines2.remove()
                x1= spec[0].get_xdata()[int(values5['voltageslid1'])]
                y1= spec[0].get_ydata()[int(values5['voltageslid1'])]
                x2= spec[0].get_xdata()[int(values5['voltageslid2'])]
                y2= spec[0].get_ydata()[int(values5['voltageslid2'])]
                win5.Element('voltagetext2').update('x2 = {} meV, y2 = {} pA'.format(round(x2*1e3,2), round(y2*1e12,2)))
                win5.Element('voltagetext3').update('dx = {} meV, dy = {} pA'.format(round(abs(x1-x2)*1e3,2), round(abs(y1-y2)*1e12,2)))
                linev2=axAvr.axvline(x=x2,color='blue', linewidth=1)
                lineh2=axAvr.axhline(y=y2,color='blue', linewidth=1)
                point2=axAvr.scatter(x2,y2, color='blue')
                lines2=ax.axhline(y=x2, color='blue')
                fig.canvas.draw_idle()
                figAvr.canvas.draw_idle()
        if not win6_active and not win5_active and event == 'Horizontal Spectra':
            win6_active=True
            line=ax.axvline(x=0)
            lines1=ax.axhline(y=0)
            lines2=ax.axhline(y=0)
            win6=HorWin(filelist)
            figHor, axHor, spec = MakeHor(filelist, G.havr, der, norm)
            makeDataHor(figHor, axHor)
            x1 = 0
            y1 = spec[0].get_ydata()[0]
            x2 = 0
            y2 = spec[0].get_ydata()[0]
            point1=axHor.scatter(x=0, y=spec[0].get_ydata()[0])
            point2=axHor.scatter(x=0, y=spec[0].get_ydata()[0])
            linev1=axHor.axvline(x=0)
            linev2=axHor.axvline(x=0)
            lineh1=axHor.axhline(y=spec[0].get_ydata()[0])
            lineh2=axHor.axhline(y=spec[0].get_ydata()[0])
        if win6_active:
            event6, values6 = win6.read(timeout=100)
            if event6 == sg.WIN_CLOSED or event6 == 'Exit':
                win6_active=False
                plt.close(figHor)
                line.remove()
                if not clear:
                    lines1.remove()
                    lines2.remove()
                    point1.remove()
                    point2.remove()
                    linev1.remove()
                    linev2.remove()
                    lineh1.remove()
                    lineh2.remove()
                fig.canvas.draw_idle()
                win6.close()
            if event6 == 'slider':
                spectrum = int(values6['slider'])
                line.remove()
                line, spec=updateHLine(spectrum, G.hdata, values6, filelist, der, norm)
                x1= spec[0].get_xdata()[int(values6['voltageslid1'])]
                y1= spec[0].get_ydata()[int(values6['voltageslid1'])]
                x2= spec[0].get_xdata()[int(values6['voltageslid2'])]
                y2= spec[0].get_ydata()[int(values6['voltageslid2'])]
                if not clear:
                    linev1=axHor.axvline(x=x1,color='red', linewidth=1)
                    linev2=axHor.axvline(x=x2,color='blue', linewidth=1)
                    lineh1=axHor.axhline(y=y1,color='red', linewidth=1)
                    lineh2=axHor.axhline(y=y2,color='blue', linewidth=1)
                    point1=axHor.scatter(x1,y1)
                    point2=axHor.scatter(x2,y2)
                    win6.Element('voltagetext1').update('x1 = {} nm, y1 = {} pA'.format(round(x1,2), round(y1*1e12,2)))
                    win6.Element('voltagetext2').update('x2 = {} nm, y2 = {} pA'.format(round(x2,2), round(y2*1e12,2)))
                    win6.Element('voltagetext3').update('dx = {} nm, dy = {} pA'.format(round(abs(x1-x2),2), round(abs(y1-y2)*1e12,2)))
                figHor.canvas.draw_idle()
            if event6 == 'Set':
                updateHPlot(values6)
            try:
                if event6.startswith('-OPEN SEC1-'):
                    opened1 = not opened1
                    clear = not clear
                    if clear:
                        lines1.remove()
                        lines2.remove()
                        point1.remove()
                        point2.remove()
                        linev1.remove()
                        linev2.remove()
                        lineh1.remove()
                        lineh2.remove()
                    if not clear:
                        lines1=ax.axvline(x=x1, color='red')
                        lines2=ax.axvline(x=x2, color='blue')
                        linev1=axHor.axvline(x=x1,color='red', linewidth=1)
                        linev2=axHor.axvline(x=x2,color='blue', linewidth=1)
                        lineh1=axHor.axhline(y=y1,color='red', linewidth=1)
                        lineh2=axHor.axhline(y=y2,color='blue', linewidth=1)
                        point1=axHor.scatter(x1,y1)
                        point2=axHor.scatter(x2,y2)
                    fig.canvas.draw_idle()
                    figHor.canvas.draw_idle()
                    win6['-OPEN SEC1-'].update(SYMBOL_DOWN if opened1 else SYMBOL_UP)
                    win6['-SEC1-'].update(visible=opened1)
            except AttributeError:
                pass
            if event6 == 'voltageslid1':
                linev1.remove()
                lineh1.remove()
                point1.remove()
                lines1.remove()
                x1= spec[0].get_xdata()[int(values6['voltageslid1'])]
                y1= spec[0].get_ydata()[int(values6['voltageslid1'])]
                x2= spec[0].get_xdata()[int(values6['voltageslid2'])]
                y2= spec[0].get_ydata()[int(values6['voltageslid2'])]
                win6.Element('voltagetext1').update('x1 = {} nm, y1 = {} pA'.format(round(x1,2), round(y1*1e12,2)))
                win6.Element('voltagetext3').update('dx = {} nm, dy = {} pA'.format(round(abs(x1-x2),2), round(abs(y1-y2)*1e12,2)))
                #x1 = G.V[int(values5['voltageslid1'])]
                linev1=axHor.axvline(x=x1,color='red',linewidth=1)
                lineh1=axHor.axhline(y=y1,color='red',  linewidth=1)
                point1=axHor.scatter(x1,y1, color='red')
                lines1=ax.axvline(x=x1, color='red')
                figHor.canvas.draw_idle()
                fig.canvas.draw_idle()
            if event6 == 'voltageslid2':
                linev2.remove()
                lineh2.remove()
                point2.remove()
                lines2.remove()
                x1= spec[0].get_xdata()[int(values6['voltageslid1'])]
                y1= spec[0].get_ydata()[int(values6['voltageslid1'])]
                x2= spec[0].get_xdata()[int(values6['voltageslid2'])]
                y2= spec[0].get_ydata()[int(values6['voltageslid2'])]
                win6.Element('voltagetext2').update('x2 = {} nm, y2 = {} pA'.format(round(x2,2), round(y2*1e12,2)))
                win6.Element('voltagetext3').update('dx = {} nm, dy = {} pA'.format(round(abs(x1-x2),2), round(abs(y1-y2)*1e12,2)))
                linev2=axHor.axvline(x=x2,color='blue', linewidth=1)
                lineh2=axHor.axhline(y=y2,color='blue', linewidth=1)
                point2=axHor.scatter(x2,y2, color='blue')
                lines2=ax.axvline(x=x2, color='blue')
                fig.canvas.draw_idle()
                figHor.canvas.draw_idle()

    if check:
        _VARS['window'].close()


