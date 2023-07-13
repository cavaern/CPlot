import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Nanonis.NanonisMP as NM
import Nanonis.NanonisHeader as NH
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

def MP():
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

    #Update interpolation
      
    def updatePol(pol, fig, img):
        img.set_interpolation(pol)
        fig.canvas.draw_idle()
        
    #Update colormap
        
    def updateCol(col, fig, img):
        img.set_cmap(col)
        fig.canvas.draw_idle()

    def updateCha(fig, img, channel):
        img.set_data(channel['{}'.format(G.V[0])])
        cbar.update_normal(img)
        fig.canvas.draw_idle()
    
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
                 

        
    def updateVRan(val, channel):
        data = abs(channel['{}'.format(G.V[int(val['slider'])])])
        img.set_data(data)

        img.norm.vmin = float(val['min'])
        img.norm.vmax = float(val['max'])

        cbar.update_normal(img)
        if not H.back:
            ax.set_title('{} {} eV'.format(name, round(G.V[int(val['slider'])],3)))
        if H.back:
            if H.V.index(G.V[int(val['slider'])])%2 == 0:
                ax.set_title('{} {} eV (forw)'.format(name, round(G.V[int(val['slider'])],3)))
            else:
                ax.set_title('{} {} eV (backw)'.format(name, round(G.V[int(val['slider'])],3)))
        
        if win4_active:
            imgFFT.set_data(abs(fftpack.fftshift(fftpack.fft2(data))))
            cbarFFT.update_normal(imgFFT)
            axFFT.set_title('{} {} eV'.format(name, round(G.V[int(val['slider'])],3)))
            figFFT.canvas.draw_idle()
        
        fig.canvas.draw_idle()
        

    def updateV(val):

        data = abs(channel['{}'.format(G.V[int(val)])])
            
        img.set_data(data)
        
        slider.valmax=np.mean(data)+20*np.std(data)
        slider.valmin=np.mean(data)-20*np.std(data)
        slider.set_val((np.mean(data)-4*np.std(data), np.mean(data)+4*np.std(data)))

        slider.ax.set_xlim(slider.valmin,slider.valmax)
        
        cbar.update_normal(img)
        if not H.back:
            ax.set_title('{} {} eV'.format(name, round(G.V[val],3)))
        if H.back:
            if H.V.index(G.V[val])%2 == 0:
                ax.set_title('{} {} eV (forw)'.format(name, round(G.V[val],3)))
            else:
                ax.set_title('{} {} eV (backw)'.format(name, round(G.V[val],3)))
        if win4_active:
            imgFFT.set_data(abs(fftpack.fftshift(fftpack.fft2(data))))
            cbarFFT.update_normal(imgFFT)
            axFFT.set_title('{} {} eV'.format(name, round(G.V[val],3)))
            figFFT.canvas.draw_idle()
            
        fig.canvas.draw_idle()
        
    def mov(filename, val, Ran, channel):
        figmov, axmov= plt.subplots()
        axmov.set_title('{} eV'.format(round(G.V[0],3)))
        axmov.set(xlabel='x (nm)', ylabel='y (nm)')
        plt.title('{} eV'.format(round(G.V[0],3)))
        imgmov=axmov.imshow(channel['{}'.format(G.V[0])], cmap='bwr', interpolation=None, norm=None, extent=(0,H.X,0,H.Y))
        if Ran:
            imgmov.norm.vmin = float(val['min'])
            imgmov.norm.vmax = float(val['max'])
        axmov.set_xlim(ax.get_xlim())
        axmov.set_ylim(ax.get_ylim())
        imgmov.set_interpolation(img.get_interpolation())
        imgmov.set_cmap(img.get_cmap())
        anim = animation.FuncAnimation(figmov, updateMov, blit=False, cache_frame_data = False, frames=np.arange(0, H.points), interval=200, fargs=(axmov, imgmov, Ran, val, channel))
        anim.save('{}.gif'.format(filename),writer='pillow')

    def updateMov(frames, axmov, imgmov, Ran, val, channel):
        datamov = channel['{}'.format(G.V[int(frames)])]
        imgmov.set_data(datamov)
        if not Ran:
            imgmov.norm.vmin = channel['{}'.format(G.V[int(frames)])].min()
            imgmov.norm.vmax = channel['{}'.format(G.V[int(frames)])].max()
        if Ran:
            imgmov.norm.vmin = float(val['min'])
            imgmov.norm.vmax = float(val['max'])
        axmov.set_title('{} eV'.format(round(G.V[frames],3)))
        
    def MakeFig(file):
        #Layout of the figure
        fig,ax=plt.subplots()
        plt.subplots_adjust(bottom=0.25)

        #Extracting the header info

        H=NH.MP(file)
        G=NM.MP(file,H)

        #Obtaining the grid in a plottable format
        name=file.split('/')
        name=name[-1].split('.')
        if not H.back:
            ax.set_title('{} {} eV'.format(name[0], round(G.V[0],3)))
            plt.set_title('{} {} eV (forw)'.format(name[0], round(G.V[0],3)))
        if H.back:
            if H.V.index(G.V[0])%2 == 0:
                ax.set_title('{} {} eV (forw)'.format(name[0], round(G.V[0],3)))
                plt.title('{} {} eV (forw)'.format(name[0], round(G.V[0],3)))
            else:
                ax.set_title('{} {} eV (backw)'.format(name[0], round(G.V[0],3)))
                plt.title('{} {} eV (forw)'.format(name[0], round(G.V[0],3)))
                
        ax.set(xlabel='x (nm)', ylabel='y (nm)')
        img=ax.imshow(G.didvdic['{}'.format(G.V[0])], cmap='afmhot', interpolation=None, norm=None, extent=(0,H.X,0,H.Y))

        slider_ax = plt.axes([0.30, 0.1, 0.50, 0.03])
        slider=RangeSlider(slider_ax, "Range", np.mean(G.didvdic['{}'.format(G.V[0])])-20*np.std(G.didvdic['{}'.format(G.V[0])]), np.mean(G.didvdic['{}'.format(G.V[0])])+20*np.std(G.didvdic['{}'.format(G.V[0])]))

        slider_ax2 = plt.axes([0.30, 0.05, 0.50, 0.03])
        slider2=Slider(slider_ax2, "Voltage", valmin=0, valmax=(H.points-1), valinit=0, valstep=1)

        cbar = fig.colorbar(img, ax=ax)

        return fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name[0]

    def MakeFFT(channel):
        figFFT,axFFT=plt.subplots()
        figFFT.set_size_inches(5, 5)
        axFFT.set_title('FFT {} eV'.format(round(G.V[slider2.val],3)))
        axFFT.set(xlabel='qx (nm-1)', ylabel='qy (nm-1)')
        
        FFT = fftpack.fftshift(fftpack.fft2(channel['{}'.format(G.V[slider2.val])]))
        imgFFT=axFFT.imshow(abs(FFT), cmap='bwr', interpolation=None, norm=SymLogNorm(1E-15), extent=(-pi*H.GridX/(8*H.X),pi*H.GridX/(8*H.X),-pi*H.GridY/(8*H.Y),pi*H.GridY/(8*H.Y)))
        cbarFFT = figFFT.colorbar(imgFFT, ax=axFFT)
        return imgFFT, figFFT, axFFT, cbarFFT
        
    def GridWin():
        menu_def = [['&File', ['&Open', '&Save', ['Image', 'WSxM file', 'SPIP file'], 'Save FFT', ['Image FFT'], 'Save All', ['WSxM files', 'SPIP files'], '---', 'E&xit'  ]],
                ['&Plot Options', ['Advanced', 'Set Channel', ['dIdV', 'd2IdV2', 'I', 'Z', ['Z', 'Z linear fit']], 'Set Range', 'FFT'],],
                ['&Movie', ['Make GIF'],],
                ['&Help', '&About...'],]


        layout = [[sg.Menu(menu_def)],[sg.Canvas(key='figCanvas', background_color='#B4B9C7')],
                                       [sg.B('Exit', pad=((240, 10), (0, 0)))]]



        return sg.Window('CPlot Multipass Window',
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
            [sg.B('Exit')]]

        return sg.Window('Advanced',
                     layout2,
                     finalize=True,
                     resizable=True,
                     location=(800, 100),
                     element_justification="center",
                     background_color='#B4B9C7',
                     modal=False)


    def RangeWin(channel):
        layout3=[[sg.T('Minimum X (nm)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= int(0), size=(20,3))],
        [sg.T('Maximum X (nm)',size=(23, 1), justification='left'), sg.In(key='maxX', enable_events=True, default_text= H.X, size=(20,3))],
        [sg.T('Minimum Y (nm)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text= int(0), size=(20,3))],
        [sg.T('Maximum Y (nm)',size=(23, 1), justification='left'), sg.In(key='maxY', enable_events=True, default_text= H.Y, size=(20,3))],
        [sg.T('Minimum of cbar',size=(23, 1), justification='left'), sg.In(key='min', enable_events=True, default_text= format(channel['{}'.format(G.V[0])].min(),'.2e'), size=(20,3))],
        [sg.T('Maximum of cbar',size=(23, 1), justification='left'), sg.In(key='max', enable_events=True, default_text= format(channel['{}'.format(G.V[0])].max(),'.2e'), size=(20,3))],
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
            [sg.T('Range cbar',size=(23, 1), justification='left'), sg.In(key='min', enable_events=True, default_text= format(channel['{}'.format(G.V[0])].min(),'.2e'), size=(10,3)),
            sg.In(key='max', enable_events=True, default_text= format(channel['{}'.format(G.V[0])].max(),'.2e'), size=(10,3))],
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


    # Layout for GUI window
    AppFont = 'Any 16'
    SliderFont = 'Any 14'
    sg.theme('CPlot')

    # ------ Menu Definition ------ #

    _VARS['window'] = GridWin()

    win2_active = False
    win3_active = False
    win4_active = False


    file=sg.Window('CPlot', [[sg.T("Select multipass file", size=(23,1)), sg.FileBrowse(file_types=(('Nanonis mulitpass','*.sxm'),))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']
    if file == '':
        pass
    elif file is None:
        pass
    else:
        try:
            fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file)
            slider.on_changed(lambda event: update(event))
            slider2.on_changed(lambda event: updateV(event))
            makeData(fig, ax, cbar)
            channel = G.didvdic
            channelname = 'dIdV'
            channelunit = 'pA'
        except TypeError:
            pass

    #Window loop
    while True:
        event, values = _VARS['window'].read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            plt.close('all')
            break
        if event == 'Open':
            file=sg.Window('CPlot', [[sg.T("Select multipass file", size=(23,1)), sg.FileBrowse(file_types=(('Nanonis mulitpass','*.sxm'),))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']
            if file == '':
                pass
            elif file is None:
                pass
            else:
                try:
                    fig, ax, img, cbar, slider, slider_ax, slider2, slider_ax2, H, G, name = MakeFig(file)
                    _VARS['window'].close()
                    _VARS['window'] = GridWin()
                    slider.on_changed(lambda event: update(event))
                    slider2.on_changed(lambda event: updateV(event))
                    makeData(fig, ax, cbar)
                    channel = G.didvdic
                    channelname = 'dIdV'
                    channelunit = 'pA'
                except TypeError:
                    pass
        if event == 'dIdV':
            channel = G.didvdic
            channelname = 'dIdV'
            channelunit= 'pA'
            updateCha(fig, img, channel)
        if event == 'd2IdV2' and G.d2idv2dic:
            channel = G.d2idv2dic
            channelname = 'd2IdV2'
            channelunit= 'pA'
            updateCha(fig, img, channel)
        if event == 'I':
            channel = G.idic
            channelname = 'I'
            channelunit= 'pA'
            updateCha(fig, img, channel)
        if event == 'Z':
            channel = G.zdic
            channelname = 'Z'
            channelunit= 'pm'
            updateCha(fig, img, channel)
        if event == 'Z linear fit':
            channel = G.zdiclin
            channelname = 'Z linear fit'
            channelunit= 'pm'
            updateCha(fig, img, channel)
        if event == 'Make GIF':
            filename=sg.popup_get_file('Choose file (gif) to save to', save_as=True)
            if file == '':
                pass
            else:
                try:
                    if not win3_active:
                        Ran=False
                        mov(filename, values, Ran, channel)
                    elif win3_active:
                        Ran=True
                        mov(filename, values3, Ran, channel)
                except IndexError:
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
        if win4_active and event == 'Image FFT':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'        
                figFFT.savefig(filename)
            except AttributeError:
                pass
        if event == 'WSxM file':
            foldername=sg.popup_get_folder('Choose folder for WSxM files')
            if foldername != None:
                if H.back and H.V.index(G.V[slider2.val])%2 == 1:
                    with open(r'{}\{}_{}_{}eV_(backw).txt'.format(foldername, name, channelname, round(G.V[slider2.val],3)), 'wb') as textfile:
                        np.savetxt(textfile, np.flip(channel['{}'.format(G.V[slider2.val])]/1e-12), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} {}'.format(H.X, H.Y, np.mean(channel['{}'.format(G.V[slider2.val])])/1e-12, channelunit), comments='')
                else:
                    with open(r'{}\{}_{}_{}eV_(forw).txt'.format(foldername, name, channelname, round(G.V[slider2.val],3)), 'wb') as textfile:
                        np.savetxt(textfile, np.flip(channel['{}'.format(G.V[slider2.val])]/1e-12), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} {}'.format(H.X, H.Y, np.mean(channel['{}'.format(G.V[slider2.val])])/1e-12, channelunit), comments='')
            else:
                pass
        if event == 'WSxM files':
            foldername=sg.popup_get_folder('Choose folder for WSxM files')
            if foldername != None:
                for i in range (0, len(G.V)):
                    if H.back and H.V.index(G.V[i])%2 == 1:
                        with open(r'{}\{}_{}_{}eV_(backw).txt'.format(foldername, name, channelname, round(G.V[i],3)), 'wb') as textfile:
                            np.savetxt(textfile, np.flip(channel['{}'.format(G.V[i])]/1e-12), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} {}'.format(H.X, H.Y, np.mean(channel['{}'.format(G.V[i])])/1e-12, channelunit), comments='')
                    else:
                        with open(r'{}\{}_{}_{}eV_(forw).txt'.format(foldername, name, channelname, round(G.V[i],3)), 'wb') as textfile:
                            np.savetxt(textfile, np.flip(channel['{}'.format(G.V[i])]/1e-12), header= 'WSxM file copyright UAM\nWSxM ASCII Matrix file\nX Amplitude: {} nm\nY Amplitude: {} nm\nZ Amplitude: {} {}'.format(H.X, H.Y, np.mean(channel['{}'.format(G.V[i])])/1e-12, channelunit), comments='')
            else:
                pass
        if event == 'SPIP file':
            foldername=sg.popup_get_folder('Choose folder for SPIP files')
            if foldername != None:
                if H.back and H.V.index(G.V[slider2.val])%2 == 1:
                    with open(r'{}\{}_{}_{}eV_(backw).asc'.format(foldername, name, channelname, round(G.V[slider2.val],3)), 'wb') as textfile:
                        np.savetxt(textfile, np.flip(channel['{}'.format(G.V[slider2.val])]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = {}\nChannel Name: {}\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y, channelunit, channelname), comments='')
                else:
                    with open(r'{}\{}_{}_{}eV_(forw).asc'.format(foldername, name, channelname, round(G.V[slider2.val],3)), 'wb') as textfile:
                        np.savetxt(textfile, np.flip(channel['{}'.format(G.V[slider2.val])]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = {}\nChannel Name: {}\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y, channelunit, channelname), comments='')
            else:
                pass
        if event == 'SPIP files':
            foldername=sg.popup_get_folder('Choose folder for SPIP files')
            if foldername != None:
                for i in range (0, len(G.V)):
                    if H.back and H.V.index(G.V[i])%2 == 1:
                        with open(r'{}\{}_{}_{}eV_(backw).asc'.format(foldername, name, channelname, round(G.V[i],3)), 'wb') as textfile:
                            np.savetxt(textfile, np.flip(channel['{}'.format(G.V[i])]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = {}\nChannel Name: {}\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y, channelunit, channelname), comments='')
                    else:
                        with open(r'{}\{}_{}_{}eV_(forw).asc'.format(foldername, name, channelname, round(G.V[i],3)), 'wb') as textfile:
                            np.savetxt(textfile, np.flip(channel['{}'.format(G.V[i])]/1e-12), header= '# File Format = ASCII\n# x-pixels = {}\n# y-pixels = {}\n# x-length = {}\n# y-length = {}\n# z-unit = {}\nChannel Name: {}\n# Start of Data:'.format(H.GridX, H.GridY, H.X, H.Y, channelunit, channelname), comments='')        
            else:
                pass
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
        if not win3_active and event == 'Set Range':
            win3_active = True
            win3 = RangeWin(channel)
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
                updateVRan(values3, channel)
        if not win4_active and event == 'FFT':
            win4_active = True
            win4=FFTWin()
            imgFFT, figFFT, axFFT, cbarFFT= MakeFFT(channel)
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
                
                
    _VARS['window'].close()
