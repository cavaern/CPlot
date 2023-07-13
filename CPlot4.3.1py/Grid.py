import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Nanonis.NanonisGrid as NG
import Nanonis.NanonisHeader as NH
import Createc.CreatecGrid as CG
import Createc.CreatecHeader as CH
import struct as struct
from matplotlib import colors
from matplotlib.colors import SymLogNorm
from scipy import fftpack
import matplotlib as mpl
from matplotlib.widgets import RangeSlider
from matplotlib.widgets import Slider
from math import pi
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from matplotlib.patches import Rectangle

def Grid():
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
    mpl.rcParams['font.sans-serif']='Arial'
    mpl.rcParams['font.size']=14
    plt.rcParams['axes.titlepad'] = 20

    interpolations=['none', 'hanning', 'gaussian', 'antialiased']
    cmaps=['gray', 'viridis', 'bwr', 'binary', 'afmhot', 'cividis']

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

    def makeDataSpec(fig, ax):
        draw_figure(win5['figCanvasAvr'].TKCanvas, fig)

    #Update interpolation
      
    def updatePol(pol, fig, img):
        img.set_interpolation(pol)
        fig.canvas.draw_idle()
        
    #Update colormap
        
    def updateCol(col, fig, img):
        img.set_cmap(col)
        fig.canvas.draw_idle()

    def updateNor(val, fig, img, norm):
        if val=='dIdV/(I/V)' and not norm:
            norm=True
            img.set_data(G.griddicnorm['0'])
        elif val=='dIdV' and norm:
            norm=False
            img.set_data(G.griddic['0'])
        cbar.update_normal(img)
        fig.canvas.draw_idle()
        return norm
    
    #Update scale

    def updateSca(sca,val):
        if sca == 'Log':
            img.set_norm(SymLogNorm(1E-15,vmin=val[0], vmax=val[1]))
        if sca == 'Linear':
            img.set_norm(None)
            img.norm.vmin = val[0]
            img.norm.vmax = val[1]
            
        cbar.update_normal(img)
        fig.canvas.draw_idle()

    #When the range slider is moved the image and histogram are updated

    def update(val):                               #
        img.norm.vmin = val[0]
        img.norm.vmax = val[1]

        cbar.update_normal(img)
        
        fig.canvas.draw_idle()


    def updateScaRan(sca,val):
        if sca == 'Log':
            img.set_norm(SymLogNorm(1E-15,vmin=val['min'], vmax=val['max']))
        if sca == 'Linear':
            img.set_norm(None)
            img.norm.vmin = float(val['min'])
            img.norm.vmax = float(val['max'])
            
    def updateRanFFT(val):
        axFFT.set_xlim(float(val['minX']), float(val['maxX']))
        axFFT.set_ylim(float(val['minY']), float(val['maxY']))
        
        imgFFT.norm.vmin = float(val['min'])
        imgFFT.norm.vmax = float(val['max'])
        cbarFFT.update_normal(imgFFT)
        
        figFFT.canvas.draw_idle()


    def updateRan(val):
        ax.set_xlim(float(val['minX']), float(val['maxX']))
        ax.set_ylim(float(val['minY']), float(val['maxY']))
        
        img.norm.vmin = float(val['min'])
        img.norm.vmax = float(val['max'])
        
        cbar.update_normal(img)
        
        fig.canvas.draw_idle()
                 

        
    def updateVRan(val, grid):
        data = abs(grid['{}'.format(int(val['slider']))])
        img.set_data(data)

        img.norm.vmin = float(val['min'])
        img.norm.vmax = float(val['max'])

        cbar.update_normal(img)
        ax.set_title('{} {} eV'.format(name, round(G.V[int(val['slider'])][0],3)))
        
        if win4_active:
            imgFFT.set_data(abs(fftpack.fftshift(fftpack.fft2(data))))
            cbarFFT.update_normal(imgFFT)
            axFFT.set_title('{} eV'.format(round(G.V[int(val['slider'])][0],3)))
            figFFT.canvas.draw_idle()
        
        fig.canvas.draw_idle()
        

    def updateV(val):
        global line
        if norm:
            data = abs(G.griddicnorm['{}'.format(int(val))])
        elif not norm:
            data = abs(G.griddic['{}'.format(int(val))])
        img.set_data(data)
        
        slider.valmax=np.mean(data)+10*np.std(data)
        slider.valmin=np.mean(data)-10*np.std(data)
        slider.set_val((np.mean(data)-2*np.std(data), np.mean(data)+2*np.std(data)))

        slider.ax.set_xlim(slider.valmin,slider.valmax)
        
        cbar.update_normal(img)
        ax.set_title('{} {} meV'.format(name, round(G.V[val][0]*1000,2)))
        if win4_active:
            imgFFT.set_data(abs(fftpack.fftshift(fftpack.fft2(data))))
            cbarFFT.update_normal(imgFFT)
            axFFT.set_title('{} meV'.format(round(G.V[val][0]*1000,2)))
            figFFT.canvas.draw_idle()
            
        fig.canvas.draw_idle()

        if win5_active:
            line.remove()
            x=G.V[int(val)]
            line=axSpec.axvline(x=x, color='red')
            figSpec.canvas.draw_idle()

        
    def mov(filename, val, Ran, grid):
        figmov, axmov= plt.subplots()
        axmov.set_title('{} eV'.format(round(G.V[0][0],3)))
        axmov.set(xlabel='x (nm)', ylabel='y (nm)')
        plt.title('{} eV'.format(round(G.V[0][0],3)))
        imgmov=axmov.imshow(grid['0'], cmap='bwr', interpolation=None, norm=None, extent=(0,H.X,0,H.Y))
        if Ran:
            imgmov.norm.vmin = float(val['min'])
            imgmov.norm.vmax = float(val['max'])
        axmov.set_xlim(ax.get_xlim())
        axmov.set_ylim(ax.get_ylim())
        imgmov.set_interpolation(img.get_interpolation())
        imgmov.set_cmap(img.get_cmap())
        anim = animation.FuncAnimation(figmov, updateMov, blit=False, cache_frame_data = False, frames=np.arange(0, H.points), interval=200, fargs=(axmov, imgmov, Ran, val, grid))
        anim.save('{}.gif'.format(filename),writer='pillow')

    def updateMov(frames, axmov, imgmov, Ran, val, grid):
        datamov = grid['{}'.format(int(frames))]
        imgmov.set_data(datamov)
        if not Ran:
            imgmov.norm.vmin = np.mean(grid['{}'.format(int(frames))]) - 2 * np.std(grid['{}'.format(int(frames))])
            imgmov.norm.vmax = np.mean(grid['{}'.format(int(frames))]) + 2 * np.std(grid['{}'.format(int(frames))])
        if Ran:
            imgmov.norm.vmin = float(val['min'])
            imgmov.norm.vmax = float(val['max'])
        axmov.set_title('{} eV'.format(round(G.V[frames][0],3)))
        
    def MakeFig(file, channel, fil, der, back, size):
        #Layout of the figure
        fig,ax=plt.subplots()
        plt.subplots_adjust(bottom=0.25)

        name=file.split('/')
        name=name[-1].split('.')
        
        #Extracting the header info
        G=NG.Grid(file, H, channel, fil, der, back, size)
        ax.set_title('{} {} meV'.format(name[0], round(G.V[0][0]*1000,2)))
        plt.title('{} {} meV'.format(name[0], round(G.V[0][0]*1000,2)))

        scaleX = H.X*abs(size[1]-size[0])/H.GridX
        scaleY = H.Y*abs(size[3]-size[2])/H.GridY

        #Obtaining the grid in a plottable format
        
        ax.set(xlabel='x (nm)', ylabel='y (nm)')

        img=ax.imshow(G.griddic['0'], cmap='bwr', interpolation='none', norm=None, extent=(0,scaleX,0,scaleY), origin='lower')
        #-H.X*(1-(size[1]-size[0])/H.GridX)-H.Y*(1-(size[3]-size[2])/H.GridY)
        slider_ax = plt.axes([0.30, 0.1, 0.50, 0.03])
        slider=RangeSlider(slider_ax, "Range", np.mean(G.griddic['0'])-10*np.std(G.griddic['0']), np.mean(G.griddic['0'])+10*np.std(G.griddic['0']))

        slider_ax2 = plt.axes([0.30, 0.05, 0.50, 0.03])
        slider2=Slider(slider_ax2, "Voltage", valmin=0, valmax=(H.points-1), valinit=0, valstep=1)

        cbar = fig.colorbar(img, ax=ax)

        return fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name[0]
    
    def MakeFFT(grid):
        figFFT,axFFT=plt.subplots()
        figFFT.set_size_inches(5, 5)
        axFFT.set_title('FFT {} meV'.format(round(G.V[slider2.val][0]*1000,2)))
        axFFT.set(xlabel='qx (nm-1)', ylabel='qy (nm-1)')
        
        FFT = fftpack.fftshift(fftpack.fft2(grid['{}'.format(slider2.val)]))
        imgFFT=axFFT.imshow(abs(FFT), cmap='bwr', interpolation=None, norm=SymLogNorm(1E-15), extent=(-pi*H.GridX/(8*H.X),pi*H.GridX/(8*H.X),-pi*H.GridY/(8*H.Y),pi*H.GridY/(8*H.Y)))
        cbarFFT = figFFT.colorbar(imgFFT, ax=axFFT)
        return imgFFT, figFFT, axFFT, cbarFFT
    
    def MakeSpec(spec):
        figSpec,axSpec = plt.subplots()
        axSpec.plot(G.V, spec)
        axSpec.set_title('Average of grid')
        return figSpec, axSpec
    
    def updateSpec(grid, val, val2, avr):
        axSpec.clear()
        if int(val['sliderh']) == 0:
            axSpec.plot(G.V, avr)
            axSpec.set_title('Average of grid')
            x = 0
            y = 0
        else:
            spectrum=[]
            for i in range (0,len(G.V)):
                spectrum.append(grid['{}'.format(i)][int(val['sliderv'])][int(val['sliderh'])-1])
            axSpec.plot(G.V, spectrum)
            axSpec.set_title('spectrum at {},{}'.format(int(val['sliderh'])-1, int(val['sliderv'])))

            x=int(val['sliderh']-1)*H.X/(H.GridX-1)
            y=int(val['sliderv'])*H.Y/(H.GridY-1)

        point=ax.scatter(x,y)
        lineh=ax.axhline(y=y)
        linev=ax.axvline(x=x)
        global line
        x=G.V[int(val2)]
        line=axSpec.axvline(x=x, color='red')
        figSpec.canvas.draw_idle()
        fig.canvas.draw_idle()
        return point, lineh, linev

    def updateRect(val):
        x1=int(val['sliderX1']-1)*H.X/(H.GridX-1)
        x2=int(val['sliderX2']-1)*H.X/(H.GridX-1)
        y1=int(val['sliderY1']-1)*H.Y/(H.GridY-1)
        y2=int(val['sliderY2']-1)*H.Y/(H.GridY-1)
        cutout = ax.add_patch(Rectangle((x1,y1), x2-x1, y2-y1, fill = False, edgecolor = 'tab:orange', lw=3))
        fig.canvas.draw_idle()
        return cutout
    
    def GridWin():
        menu_def = [['&File', ['&Open', '&Save', ['Image', 'WSxM file', 'SPIP file'], 'SaveFFT', 'Save Spectra',
                               ['Spectrum', 'Row', 'Column'], 'Save All', ['WSxM files', 'SPIP files'], '---', 'E&xit'  ]],
                ['&Plot Options', ['Advanced', 'Set Range', 'Set Size', 'FFT', 'Spectra', 'Topography', 'channel', ['dIdV', 'd2IdV2', 'Z']],],
                ['&Movie', ['GridMov'],],
                ['&Help', '&About...'],]


        layout = [[sg.Menu(menu_def)],[sg.Canvas(key='figCanvas', background_color='#B4B9C7')],
                                       [sg.B('Exit', pad=((240, 10), (0, 0)))]]



        return sg.Window('CPlot Grid Window',
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
            [sg.T("Scale", size=(23, 1), justification='left'), sg.Combo(values=['Linear', 'Log'], size=(20,3), default_value='Linear', key='sca', enable_events=True)],
            [sg.T("Normalize", size=(23, 1), justification='left'), sg.Combo(values=['dIdV', 'dIdV/(I/V)'], size=(20,3), default_value='dIdV', key='nor', enable_events=False)],
            [sg.T("Filter", size=(23, 1), justification='left'),
                  sg.Combo(values=['none', 'Savinsky-Golay'], size=(20, 3), default_value='none', key='fil',
                           enable_events=False)],
            [sg.T('Filter Window', size=(23, 1), justification='left'),
                  sg.Combo(values=[5, 7, 11, 15, 21], key='filwin', enable_events=True, default_value=11,
                           size=(20, 3))],
            [sg.T('Filter Polynomial', size=(23, 1), justification='left'),
                  sg.Combo(values=[1, 2, 3, 4], key='filpol', enable_events=True, default_value=2, size=(20, 3))],
            [sg.T("Derivative", size=(23, 1), justification='left'),
                  sg.Combo(values=['y', 'dy/dx'], size=(20, 3), default_value='y', key='der', enable_events=False)],
            [sg.T("Bwd average", size=(23, 1), justification='left'),
                  sg.Combo(values=['yes', 'no'], size=(20, 3), default_value='no', key='bwd', enable_events=False)],
            [sg.B('Exit')]]

        return sg.Window('Advanced',
                     layout2,
                     finalize=True,
                     resizable=True,
                     location=(800, 100),
                     element_justification="center",
                     background_color='#B4B9C7',
                     modal=False)


    def RangeWin():
        layout3=[[sg.T('Minimum X (nm)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= int(0), size=(20,3))],
        [sg.T('Maximum X (nm)',size=(23, 1), justification='left'), sg.In(key='maxX', enable_events=True, default_text= H.X, size=(20,3))],
        [sg.T('Minimum Y (nm)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text= int(0), size=(20,3))],
        [sg.T('Maximum Y (nm)',size=(23, 1), justification='left'), sg.In(key='maxY', enable_events=True, default_text= H.Y, size=(20,3))],
        [sg.T('Minimum of cbar',size=(23, 1), justification='left'), sg.In(key='min', enable_events=True, default_text= format(G.griddic['0'].min(),'.2e'), size=(20,3))],
        [sg.T('Maximum of cbar',size=(23, 1), justification='left'), sg.In(key='max', enable_events=True, default_text= format(G.griddic['0'].max(),'.2e'), size=(20,3))],
        [sg.Slider(range=(0, (H.points-1)), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="slider")],
        [sg.B('Set'), sg.B('Exit')]]

        return sg.Window('Set Range',
                         layout3,
                         finalize=True,
                         resizable=True,
                         location=(800, 300),
                         element_justification="center",
                         background_color='#B4B9C7',
                         modal=False)

    def FFTWin():
        layout4 = [[sg.Canvas(key='figCanvasFFT', background_color='#B4B9C7')],
                   [sg.T("Interpolation",size=(23, 1), justification='left'), sg.Combo(values=interpolations, size=(20,3), default_value='none', key='pol', enable_events=True)],
            [sg.T("Colormap", size=(23, 1), justification='left'), sg.Combo(values=cmaps, size=(20,3), default_value='bwr', key='col', enable_events=False)],
            [sg.T('Range cbar',size=(23, 1), justification='left'), sg.In(key='min', enable_events=True, default_text= format(G.griddic['0'].min(),'.2e'), size=(10,3)),
            sg.In(key='max', enable_events=True, default_text= format(G.griddic['0'].max(),'.2e'), size=(10,3))],
            [sg.T('Range X(nm)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= round(-pi*H.GridX/(8*H.X),2), size=(10,3)),
             sg.In(key='maxX', enable_events=True, default_text= round(pi*H.GridX/(8*H.X),2), size=(10,3))],
            [sg.T('Range Y (nm)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text= round(-pi*H.GridY/(8*H.Y),2), size=(10,3)),
            sg.In(key='maxY', enable_events=True, default_text= round(pi*H.GridY/(8*H.Y),2), size=(10,3))],
        [sg.B('Set'), sg.Button('Exit', pad=((140, 10), (0, 0)))]]

        return sg.Window('FFT',
                        layout4,
                        finalize=True,
                        resizable=True,
                        location=(800,500),
                        element_justification="center",
                        background_color='#B4B9C7',
                        modal=False)

        
    def SpecWin():
        col1=[[sg.Slider(range=(0, H.GridY-1), size=(10, 50), orientation="v",
                enable_events=True, default_value=0, key="sliderv")]]
        col2 = [[sg.Canvas(key='figCanvasAvr', background_color='#B4B9C7')],
##        [sg.T('V range (eV)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= G.V[-1], size=(10,3)),
##         sg.In(key='maxX', enable_events=True, default_text= G.V[0], size=(10,3))],
##        [sg.T('dIdV range (A)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text=format(G.avr.min(), '.2e') , size=(10,3)),
##         sg.In(key='maxY', enable_events=True, default_text= format(G.avr.max(), '.2e'), size=(10,3))],
        [sg.Slider(range=(0, H.GridX), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="sliderh")],
        [sg.B('Set'), sg.Button('Exit', pad=((140, 10), (0, 0)))]]

        layout5=[[sg.Column(col1, element_justification='c'), sg.Column(col2,
        element_justification='c')]]

        return sg.Window('Spectra',
                        layout5,
                        finalize=True,
                        resizable=True,
                        location=(800,500),
                        element_justification="center",
                        background_color='#B4B9C7',
                        modal=False)

    def CutWin():
        layout6=[[sg.T('X1', size=(23, 1), justification='left'), sg.Slider(range=(0, H.GridX), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="sliderX1")],
                     [sg.T('X2', size=(23, 1), justification='left'), sg.Slider(range=(0, H.GridX), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="sliderX2")],
                     [sg.T('Y1', size=(23, 1), justification='left'), sg.Slider(range=(0, H.GridY), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="sliderY1")],
                     [sg.T('Y2', size=(23, 1), justification='left'), sg.Slider(range=(0, H.GridY), size=(50, 10), orientation="h",
                enable_events=True, default_value=0, key="sliderY2")],
            [sg.B('Reset'), sg.B('Set'), sg.B('Exit')]]

        return sg.Window('Set Size',
                            layout6,
                            finalize=True,
                            resizable=True,
                            location=(800, 300),
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
    
    norm = False
    channel='dIdV'
    fil=['none', 11, 2]
    der = 'y'
    back = 'no'
    
    
    file=sg.Window('CPlot', [[sg.T("Select grid file", size=(23,1)), sg.FileBrowse(file_types=(('Nanonis grids','*.3ds'),('Createc grids', '*.specgrid'),))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']
    if file == '':
        pass
    elif file is None:
        pass
    # else:
    #     try:
    #         fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel)
    #         slider.on_changed(lambda event: update(event))
    #         slider2.on_changed(lambda event: updateV(event))
    #         makeData(fig, ax, cbar)
    #     except TypeError:
    #         pass
    
    H=NH.Grid(file)
    size = [0, H.GridX, 0, H.GridY]
    
    fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
    
    _VARS['window'] = GridWin()
    
    slider.on_changed(lambda event: update(event))
    slider2.on_changed(lambda event: updateV(event))
    
    makeData(fig, ax, cbar)

    #Window loop
    while True:
        event, values = _VARS['window'].read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            plt.close('all')
            break
        if event == 'Open':
            file=sg.Window('CPlot', [[sg.T("Select grid file", size=(23,1)), sg.FileBrowse(file_types=(('Nanonis grids','*.3ds'),('Createc grids', '*.specgrid'),))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']
            if file == '':
                pass
            elif file is None:
                pass
            else:
                try:
                    H=NH.Grid(file)
                    size = [0, H.GridX, 0, H.GridY]
                    fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
                    _VARS['window'].close()
                    _VARS['window'] = GridWin()
                    slider.on_changed(lambda event: update(event))
                    slider2.on_changed(lambda event: updateV(event))
                    makeData(fig, ax, cbar)
                except TypeError:
                    pass
        if event == 'GridMov':
            filename=sg.popup_get_file('Choose file (gif) to save to', save_as=True)
            if file == '':
                pass
            else:
                try:
                    if not win3_active:
                        Ran=False
                        if norm:
                            mov(filename, values, Ran, G.griddicnorm)
                        elif not norm:
                            mov(filename, values, Ran, G.griddic)
                    elif win3_active:
                        Ran=True
                        if norm:
                            mov(filename, values3, Ran, G.griddicnorm)
                        elif not norm:
                            mov(filename, values3, Ran, G.griddic)
                except IndexError:
                    pass
        if event == 'WSxM file':
            foldername=sg.popup_get_folder('Choose folder for WSxM files')
            if foldername != None:
                with open(r'{}\{}_{}meV.txt'.format(foldername, name, round(G.V[slider2.val][0]*1000,2)), 'wb') as textfile:
                    if norm:
                        np.savetxt(textfile, np.flip(G.griddicnorm['{}'.format(int(slider2.val))]), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} pA'.format(H.X, H.Y, np.mean(G.griddic['{}'.format(int(slider2.val))])/1e-12), comments='')
                    else:
                        np.savetxt(textfile, np.flip(G.griddic['{}'.format(int(slider2.val))]/1e-12), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} pA'.format(H.X, H.Y, np.mean(G.griddic['{}'.format(int(slider2.val))])/1e-12), comments='')
            else:
                pass
        if event == 'WSxM files':
            foldername=sg.popup_get_folder('Choose folder for WSxM files')
            if foldername != None:
                for i in range (0, len(G.V)):
                    with open(r'{}\{}_{}meV.txt'.format(foldername, name, round(G.V[i][0]*1000,2)), 'wb') as textfile:
                        if norm:
                            np.savetxt(textfile, np.flip(G.griddicnorm['{}'.format(i)]), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} pA'.format(H.X, H.Y, np.mean(G.griddic['{}'.format(i)])/1e-12), comments='')
                        else:
                            np.savetxt(textfile, np.flip(G.griddic['{}'.format(i)]/1e-12), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} pA'.format(H.X, H.Y, np.mean(G.griddic['{}'.format(i)])/1e-12), comments='')                
                with open(r'{}\{}_Topography.txt'.format(foldername, name), 'wb') as textfile:
                    np.savetxt(textfile, np.flip(G.griddic['Z']), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} m'.format(H.X, H.Y, np.mean(G.griddic['Z'])), comments='')                
            else:
                pass
        if event == 'SPIP file':
            foldername=sg.popup_get_folder('Choose folder for SPIP files')
            if foldername != None:
                with open(r'{}\{}_{}meV.asc'.format(foldername, name, round(G.V[slider2.val][0]*1000,2)), 'wb') as textfile:
                    if norm:
                        np.savetxt(textfile, np.flip(G.griddicnorm['{}'.format(int(slider2.val))]), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = nA\nChannel Name: dIdV\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y), comments='')
                    else:
                        np.savetxt(textfile, np.flip(G.griddic['{}'.format(int(slider2.val))]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = nA\nChannel Name: dIdV\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y), comments='')
            else:
                pass
        if event == 'SPIP files':
            foldername=sg.popup_get_folder('Choose folder for SPIP files')
            if foldername != None:
                for i in range (0, len(G.V)):
                    with open(r'{}\{}_{}meV.asc'.format(foldername, name, round(G.V[i][0]*1000,2)), 'wb') as textfile:
                        if norm:
                            np.savetxt(textfile, np.flip(G.griddicnorm['{}'.format(i)]), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = nA\nChannel Name: dIdV\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y), comments='')
                        else:
                            np.savetxt(textfile, np.flip(G.griddic['{}'.format(i)]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = nA\nChannel Name: dIdV\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y), comments='')         
                with open(r'{}\{}_Topography.asc'.format(foldername, name), 'wb') as textfile:
                    np.savetxt(textfile, np.flip(G.griddic['Z']), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = m\nChannel Name: Z\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y), comments='')        
            else:
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
        if win4_active and event == 'SaveFFT':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'        
                figFFT.savefig(filename)
            except AttributeError:
                pass
        if win5_active and event == 'Spectrum':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            if int(values5['sliderh']) == 0:
                name = 'Average of grid'
                if norm:
                    spectrum = G.gridavrnorm
                else:
                    spectrum = G.gridavr
                spectrumI = G.gridavrI
            else:
                name='{},{}'.format(int(values5['sliderv']), int(values5['sliderh'] - 1))
                spectrum = []
                spectrumI = []
                for i in range(0, len(G.V)):
                    spectrum.append(G.griddic['{}'.format(i)][int(values5['sliderv'])][int(values5['sliderh'])-1])
                    spectrumI.append(G.griddicI['{}'.format(i)][int(values5['sliderv'])][int(values5['sliderh'])-1])
            if foldername != None:
                with open(r'{}\{}.dat'.format(foldername, name), 'wb') as textfile:
                    np.savetxt(textfile, np.c_[G.V, spectrum, spectrumI],  header = 'CPlot file [V, dIdV, I]', comments = '#')
            else:
                pass
        if win5_active and event == 'Column':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            for j in range(0, H.GridY):
                name='{},{}'.format(j, int(values5['sliderh']))
                spectrum = []
                spectrumI = []
                for i in range(0, len(G.V)):
                    spectrum.append(G.griddic['{}'.format(i)][j][int(values5['sliderh'])])
                    spectrumI.append(G.griddicI['{}'.format(i)][j][int(values5['sliderh'])])
                if foldername != None:
                    with open(r'{}\{}.dat'.format(foldername, name), 'wb') as textfile:
                        np.savetxt(textfile, np.c_[G.V, spectrum, spectrumI],  header = 'CPlot file [V, dIdV, I]', comments = '#')
                else:
                    pass
        if win5_active and event == 'Row':
            foldername=sg.popup_get_folder('Choose folder for ASCII files')
            for j in range(0, H.GridX):
                name='{},{}'.format(int(values5['sliderv']), j)
                spectrum = []
                spectrumI = []
                for i in range(0, len(G.V)):
                    spectrum.append(G.griddic['{}'.format(i)][int(values5['sliderv'])][j])
                    spectrumI.append(G.griddicI['{}'.format(i)][int(values5['sliderv'])][j])
                if foldername != None:
                    with open(r'{}\{}.dat'.format(foldername, name), 'wb') as textfile:
                        np.savetxt(textfile, np.c_[G.V, spectrum, spectrumI],  header = 'CPlot file [V, dIdV, I]', comments = '#')
                else:
                    pass
        if event == 'dIdV':
            channel = 'dIdV'
            try:
                fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
                _VARS['window'].close()
                _VARS['window'] = GridWin()
                slider.on_changed(lambda event: update(event))
                slider2.on_changed(lambda event: updateV(event))
                makeData(fig, ax, cbar)
            except TypeError:
                pass
        if event == 'd2IdV2':
            channel = 'd2IdV2'
            try:
                fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
                _VARS['window'].close()
                _VARS['window'] = GridWin()
                slider.on_changed(lambda event: update(event))
                slider2.on_changed(lambda event: updateV(event))
                makeData(fig, ax, cbar)
            except KeyError:
                pass
        if event == 'Z':
            channel = 'Z'
            try:
                fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
                _VARS['window'].close()
                _VARS['window'] = GridWin()
                slider.on_changed(lambda event: update(event))
                slider2.on_changed(lambda event: updateV(event))
                makeData(fig, ax, cbar)
            except KeyError:
                pass
        if event == 'Topography':
            data = G.griddic['Z']-np.min(G.griddic['Z'])
            img.set_data(data)
            img.norm.vmin = float(np.min(data))
            img.norm.vmax = float(np.max(data))
            slider.valmax = np.mean(data) + 10 * np.std(data)
            slider.valmin = np.mean(data) - 10 * np.std(data)
            slider.set_val((np.mean(data) - 2 * np.std(data), np.mean(data) + 2 * np.std(data)))
            slider.ax.set_xlim(slider.valmin, slider.valmax)
            cbar.update_normal(img)
            fig.canvas.draw_idle()

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
                if values2['sca']:
                    if not win3_active:
                        updateSca(values2['sca'], slider.val)
                    else:
                        pass
            except TypeError:
                pass
            try:
                if values2['nor']:
                    norm=updateNor(values2['nor'], fig, img, norm)      
            except TypeError:
                pass
            try:
                if values2['fil'] != fil[0] or values2['filwin'] != fil[1] or values2['filpol'] != fil[2]:
                    fil = [values2['fil'], values2['filwin'], values2['filpol']]
                    try:
                        fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel,
                                                                                                             fil, der, back, size)
                        _VARS['window'].close()
                        _VARS['window'] = GridWin()
                        slider.on_changed(lambda event: update(event))
                        slider2.on_changed(lambda event: updateV(event))
                        makeData(fig, ax, cbar)
                    except TypeError:
                        pass
            except TypeError:
                pass
            try:
                if values2['der'] != der:
                    der = values2['der']
                    try:
                        fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel,
                                                                                                         fil, der, back, size)
                        _VARS['window'].close()
                        _VARS['window'] = GridWin()
                        slider.on_changed(lambda event: update(event))
                        slider2.on_changed(lambda event: updateV(event))
                        makeData(fig, ax, cbar)
                    except TypeError:
                        pass
            except TypeError:
                pass
            try:
                if values2['bwd'] != back:
                    back = values2['bwd']
                    try:
                        fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel,
                                                                                                         fil, der, back, size)
                        _VARS['window'].close()
                        _VARS['window'] = GridWin()
                        slider.on_changed(lambda event: update(event))
                        slider2.on_changed(lambda event: updateV(event))
                        makeData(fig, ax, cbar)
                    except TypeError:
                        pass
            except TypeError:
                pass

        if not win3_active and event == 'Set Range':
            win3_active = True
            win3 = RangeWin()
        if win3_active:
            event3, values3 = win3.read(timeout=100)
            if event3 == sg.WIN_CLOSED or event3 == 'Exit':
                win3_active=False
                win3.close()
            if event3 == 'Set':
                if win2_active:
                    updateScaRan(values2['sca'], values3)
                updateRan(values3)
            if event3 == 'slider':
                if not norm:
                    updateVRan(values3, G.griddic)
                elif norm:
                    updateVRan(values3, G.griddicnorm)
        if not win4_active and event == 'FFT':
            win4_active = True
            win4=FFTWin()
            if norm:
                imgFFT, figFFT, axFFT, cbarFFT= MakeFFT(G.griddicnorm)
            if not norm:
                imgFFT, figFFT, axFFT, cbarFFT= MakeFFT(G.griddic)
            makeDataFFT(figFFT, axFFT, cbarFFT)   
        if win4_active:
            event4, values4 = win4.read(timeout=100)
            if event4 == sg.WIN_CLOSED or event4 == 'Exit':
                win4_active=False
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
        if not win5_active and event == 'Spectra':
            win5_active=True
            point=ax.scatter(0,0)
            lineh=ax.axhline(y=0)
            linev=ax.axvline(x=0)
            win5=SpecWin()
            if not norm:
                figSpec, axSpec = MakeSpec(G.gridavr)
            elif norm:
                figSpec, axSpec = MakeSpec(G.gridavrnorm)
            global line
            line=axSpec.axvline(x=0, color='red')
            makeDataSpec(figSpec, axSpec)
        if win5_active:
            event5, values5 = win5.read(timeout=100)
            if event5 == sg.WIN_CLOSED or event5 == 'Exit':
                win5_active=False
                plt.close(figSpec)
                point.remove()
                lineh.remove()
                linev.remove()
                fig.canvas.draw_idle()
                win5.close()
            if event5 == 'sliderh' or event5=='sliderv':
                point.remove()
                lineh.remove()
                linev.remove()
                if not norm:
                    point, lineh, linev=updateSpec(G.griddic, values5, slider2.val, G.gridavr)
                elif norm:
                    point, lineh, linev=updateSpec(G.griddicnorm, values5, slider2.val, G.gridavrnorm)
                    
        if not win6_active and event == 'Set Size':
            win6_active = True
            cutout = ax.add_patch(Rectangle((0,0), 0, 0, fill = False, edgecolor = 'tab:orange', lw=3))
            win6=CutWin()
            
        if win6_active:
            event6, values6 = win6.read(timeout=100)
            if event6 == sg.WIN_CLOSED or event6 == 'Exit':
                win6_active=False
                cutout.remove()
                fig.canvas.draw_idle()
                win6.close()
            if event6 == sg.WIN_CLOSED or event6 == 'Exit':
                win6_active=False
                win6.close()
            if event6 == 'sliderX1' or event6=='sliderX2' or event6 == 'sliderY1' or event6=='sliderY2':
                cutout.remove()
                cutout = updateRect(values6)
            if event6 == 'Set':
                size[0] = int(values6['sliderX1'])
                size[1] = int(values6['sliderX2'])
                size[2] = int(values6['sliderY1'])
                size[3] = int(values6['sliderY2'])
                try:
                    fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
                    _VARS['window'].close()
                    _VARS['window'] = GridWin()
                    slider.on_changed(lambda event: update(event))
                    slider2.on_changed(lambda event: updateV(event))
                    makeData(fig, ax, cbar)
                except TypeError or ValueError:
                    pass
            if event6 == 'Reset':
                size = [0, H.GridX, 0, H.GridY]
                try:
                    fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file, channel, fil, der, back, size)
                    _VARS['window'].close()
                    _VARS['window'] = GridWin()
                    slider.on_changed(lambda event: update(event))
                    slider2.on_changed(lambda event: updateV(event))
                    makeData(fig, ax, cbar)
                except TypeError or ValueError:
                    pass
    _VARS['window'].close()


