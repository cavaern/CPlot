import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Nanonis.NanonisSpec as NS
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
import seaborn as sns



def Spec():
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

    def on_button_press(event):
        """Callback for mouse button presses."""
        if not showverts:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        ind = fig.canvas.mpl_connect('pick_event', on_pick_leg)

    def on_button_release(event):
        """Callback for mouse button releases."""
        if not showverts:
            return
        if event.button != 1:
            return
        ind = None

    def on_key_press(event):
        """Callback for key presses."""
        if not event.inaxes:
            return
        if event.key == 't':
            showverts = not showverts
            line.set_visible(showverts)
            if not showverts:
                ind = None
        elif event.key == 'd':
            ind = get_ind_under_point(event)
            if ind is not None:
                poly.xy = np.delete(poly.xy,
                                         ind, axis=0)
                line.set_data(zip(*poly.xy))
        elif event.key == 'i':
            xys = poly.get_transform().transform(poly.xy)
            p = event.x, event.y  # display coords
            for i in range(len(xys) - 1):
                s0 = xys[i]
                s1 = xys[i + 1]
                d = dist_point_to_segment(p, s0, s1)
                if d <= epsilon:
                    poly.xy = np.insert(
                        poly.xy, i+1,
                        [event.xdata, event.ydata],
                        axis=0)
                    line.set_data(zip(*poly.xy))
                    break
        if line.stale:
            fig.canvas.draw_idle()
            
    def on_mouse_move(event):
        """Callback for mouse movements."""
        if not showverts:
            return
        if ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return

        x, y = event.xdata, event.ydata
        global vline
        global vline2

        if abs(x - vline.get_xdata()[0]) < abs(x - vline2.get_xdata()[0]):
            vline.remove()
            vline = ax.axvline(x=x, picker=True)
        else:
            vline2.remove()
            vline2 = ax.axvline(x=x, picker=True, color='red')

        fig.canvas.draw_idle()



    def on_pick_leg(event):
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        if isinstance(event.artist, mpl.lines.Line2D):
            try:
                legline = event.artist
                origline = lined[legline]
                visible = not origline.get_visible()
                origline.set_visible(visible)
                # Change the alpha on the line in the legend so we can see what lines
                # have been toggled.
                legline.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()
                ind = None
                return ind
            except KeyError:
                ind = event.ind[0]
                data = event.artist.get_xdata()
                xdata = data[ind:]
                return ind
        else:
            ind = event.ind[0]
            data = event.artist.get_offsets()
            xdata = data[ind:]
            return ind

    def collapse(layout, key):
        return sg.pin(sg.Column(layout, key=key))


    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    #Connecting the figure with the right canvas and window


    def makeData(fig, ax):
        draw_figure(_VARS['window']['figCanvasAvr'].TKCanvas, fig)

    def updatePlot(val):
        try:
            ax.set_xlim([float(val['minX']),float(val['maxX'])])
            ax.set_ylim([float(val['minY']),float(val['maxY'])])
            fig.canvas.draw_idle()
        except ValueError:
            pass

    def MakeSpec(files, names):

        specdic ={}

        for c, file in enumerate(files):
            H=NH.Header(file)
            G=NS.Spectrum(file,H)
            specdic[f'{names[c]}'] = (G.V, G.I, G.dIdV)

        return specdic, H

    def PlotSpec(fig, ax, dic, files, val):

        ax.clear()

        lines=[]

        iter = len(files)

        colorlist = list(reversed(sns.color_palette(f"{val['col']}", iter).as_hex()))

        c = 0
        
        for count, file in enumerate(files):
            V = dic[f'{file}'][0]
            if val['nor'] == 'dI/dV':
                data = dic[f'{file}'][2]
            elif val['nor'] == 'dI/dV/(I/V)':
                data = dic[f'{file}'][2]/((abs(dic[f'{file}'][1]) + float(val['normoffI']))/(abs(dic[f'{file}'][0]+ float(val['normoffV']))))
            if val['fil'] == 'Savinsky-Golay':
                data = savgol_filter(data,filsetwin,filsetpoly)

            if val['der'] == 'dy/dx':
                data = np.gradient(data)
            elif val['der'] == 'abs(dy/dx)':
                data = abs(np.gradient(data))

            if val['nor2'] == 'start':
                data = data/data[0]
            if val['nor2'] == 'end':
                data = data/data[-1]
            if val['nor2'] == 'max':
                data = data/np.max(data)
            if val['nor2'] == 'min':
                data = data/np.min(data)
   
            data += float(val['off'])*count
            spec=ax.plot(V, data, label='{}'.format(file), picker=True, linewidth = val['wid'], color = colorlist[c])
            lines.append(spec)
            if c < 14:
                c+= 1
            else:
                c = 0

        leg = ax.legend(fancybox=True, shadow=True, fontsize='x-small', markerscale=50.0)
        lined = {}  # Will map legend lines to original lines.
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(7)  # Enable picking on the legend line.
            lined[legline] = origline[0]
        name=files[0].split('/')

        fig.canvas.draw_idle()
        return spec, lined, leg

    def SpecWin(names):
        menu_def = [['&File', ['&Open', '&Save', ['Image'],'---', 'E&xit'  ]],
                ['&Help', '&About...'],]
      
        section1 = [[sg.Listbox(values=names, size=(50,10), enable_events=True, bind_return_key=True, select_mode='multiple', key='spectra')]]
        
        col1 = [[sg.Canvas(key='figCanvasAvr', background_color='#B4B9C7')],
                   [sg.T(f'x1 = {linex1} eV', key='X1', text_color='blue'), sg.T(f'x2 = {linex2} eV', key='X2', text_color='red'), sg.T(f'dx = {abs(linex1 - linex2)} eV', key='DX')],
       [sg.T(SYMBOL_DOWN, enable_events=True, k='-OPEN SEC1-', text_color='blue'), sg.T('Data Selection', enable_events=True, text_color='blue', k='-OPEN SEC1-TEXT')],
           [collapse(section1, '-SEC1-')],
    [sg.B('Set'), sg.Button('Exit', pad=((140, 10), (0, 0)))]]

        col2 = [[sg.T("Normalize", size=(23, 1), justification='left'), sg.Combo(values=['dI/dV', 'dI/dV/(I/V)'], size=(20,3), default_value='dI/dV', key='nor', enable_events=False)],
                [sg.T("Norm offset I (A) V (eV)", size=(23, 1), justification='left'), sg.In(size=(10,3), default_text='1e-12', key='normoffI', enable_events=False),
                 sg.In(size=(10,3), default_text='0', key='normoffV', enable_events=False)],
                [sg.T("Normalize to", size=(23, 1), justification='left'), sg.Combo(values=['none','start', 'end', 'max', 'min'], size=(20,3), default_value='none', key='nor2', enable_events=False)],
            [sg.T("Filter", size=(23, 1), justification='left'), sg.Combo(values=['none', 'Savinsky-Golay'], size=(20,3), default_value='none', key='fil', enable_events=False)],
            [sg.T("Derivative", size=(23, 1), justification='left'), sg.Combo(values=['y', 'dy/dx', 'abs(dy/dx)'], size=(20,3), default_value='y', key='der', enable_events=False)],
        [sg.T("Linewidth", size=(23, 1), justification='left'), sg.Combo(values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], size=(20,3), default_value= 3 , key='wid', enable_events=False)],
           [sg.T("Colors", size=(23, 1), justification='left'), sg.Combo(values=['magma', 'magma_r', 'Spectral', 'viridis', 'ocean', 'rainbow', 'gist_rainbow'], size=(20,3), default_value= 'magma_r', key='col', enable_events=False)],
        [sg.T('Offset',size=(23, 1), justification='left'), sg.In(key='off', enable_events=True, default_text = '0', size=(20,3))],
        [sg.T('V range (eV)',size=(23, 1), justification='left'), sg.In(key='minX', enable_events=True, default_text= round(specdic[f'{names[0]}'][0][-1],4), size=(10,3)),
         sg.In(key='maxX', enable_events=True, default_text= round(specdic[f'{names[0]}'][0][0],4), size=(10,3))],
        [sg.T('dIdV range (A)',size=(23, 1), justification='left'), sg.In(key='minY', enable_events=True, default_text=format(np.min(specdic[f"{names[0]}"][2]), '.2e') , size=(10,3)),
         sg.In(key='maxY', enable_events=True, default_text= format(np.max(specdic[f'{names[0]}'][2]), '.2e'), size=(10,3))],
                [sg.Checkbox('Toggle legend', default=True, key="Leg")]
]

        layout=[[sg.Menu(menu_def)], [sg.Column(col1, element_justification='c'), sg.Column(col2,
        element_justification='c')]]

        return sg.Window('Spectra',
                        layout,
                        finalize=True,
                        resizable=True,
                        location=(0,0),
                        element_justification="center",
                        background_color='#B4B9C7',
                        modal=False)

    # Layout for GUI window
    AppFont = 'Any 16'
    SliderFont = 'Any 14'
    sg.theme('CPlot')

    # ------ Menu Definition ------ #

    opened1 = True
    clear = False

    linex1 = 0
    linex2 = 0
    
    norm=False
    fil=False
    der=False

    check = True
    
    startval = {}
    startval['nor'] = 'dI/dV'
    startval['fil'] = 'none'
    startval['der'] = 'y'
    startval['wid'] = 1
    startval['col'] = 'magma_r'
    startval['nor2'] = 'none'
    startval['off'] = 0
    startval['normoffI'] = 1e-12
    startval['normoffV'] = 0
    filsetwin=11
    filsetpoly=2
    
    files=''
    files=sg.Window('CPlot', [[sg.T("Select files", size=(23,1)), sg.FilesBrowse(file_types=(('Nanonis spectra','*.dat'),('Createc spectra','*.vert')))],
              [sg.B('Plot')]]).read(close=True)[1]['Browse']
    
    if files != '':
        try:
            filelist=files.split(';')
            names=[]
            for elem in filelist:
                names.append(elem.split('/')[-1])
            fig, ax = plt.subplots()
            ax.set_title('Spectra')
            specdic, H = MakeSpec(filelist, names)
            if H.hor:
                ax.set(xlabel='Distance (nm)', ylabel='dIdV (A)')
            else:
                ax.set(xlabel='Energy (eV)', ylabel='dIdV (A)')
            spec, lined, leg = PlotSpec(fig, ax, specdic, [names[0]], startval)
            _VARS['window'] = SpecWin(names)
            global vline
            vline=ax.axvline(x=specdic[f'{names[0]}'][0][0], picker=True)
            global vline2
            vline2 = ax.axvline(x=specdic[f'{names[0]}'][0][-1], picker=True, color = 'red')
            makeData(fig, ax)
            linex1 = vline.get_xdata()[0]
            linex2 = vline2.get_xdata()[0]
            showverts=True
            epsilon=5
            ind= None
            fig.canvas.mpl_connect('pick_event', on_pick_leg)
            ind=fig.canvas.mpl_connect('button_press_event', on_button_press)
            fig.canvas.mpl_connect('key_press_event', on_key_press)
            fig.canvas.mpl_connect('button_release_event', on_button_release)
            fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
        except AttributeError:
            check = False
            pass
    else:
        check = False

    #Window loop
    while check:
        event, values = _VARS['window'].read(timeout=100)
        if linex1 != vline.get_xdata()[0] or linex2 != vline2.get_xdata()[0]:
            linex1 = vline.get_xdata()[0]
            linex2 = vline2.get_xdata()[0]
            _VARS['window']['X1'].update(f'x1 = {round(linex1*1000, 2)} meV')
            _VARS['window']['X2'].update(f'x2 = {round(linex2*1000, 2)} meV')
            _VARS['window']['DX'].update(f'dx = {round(abs(linex1 - linex2)*1000, 2)} meV')

        if event == sg.WIN_CLOSED or event == 'Exit':
            plt.close('all')
            break
        try:
            if event.startswith('-OPEN SEC1-'):
                opened1 = not opened1
                _VARS['window']['-OPEN SEC1-'].update(SYMBOL_DOWN if opened1 else SYMBOL_UP)
                _VARS['window']['-SEC1-'].update(visible=opened1)
        except AttributeError:
            pass
        if event == 'Set':
            if values['spectra']:
                spec, lined, leg = PlotSpec(fig, ax, specdic, values['spectra'], values)
                vline = ax.axvline(x=specdic[values['spectra'][0]][0][0], picker=True)
                vline2 = ax.axvline(x=specdic[values['spectra'][0]][0][-1], picker=True, color='red')
                updatePlot(values)
            else:
                ax.clear()
                fig.canvas.draw_idle()

        if event == 'Open':
            files=sg.Window('CPlot', [[sg.T("Select files", size=(23,1)), sg.FilesBrowse(file_types=(('Nanonis spectra','*.dat'),('Createc spectra','*.vert')))],
                                      [sg.B('Plot')]]).read(close=True)[1]['Browse']
            if files != '':
                try:
                    filelist = files.split(';')
                    names = []
                    for elem in filelist:
                        names.append(elem.split('/')[-1])
                    _VARS['window'].close()

                    specdic, H = MakeSpec(filelist, names)
                    spec, lined, leg = PlotSpec(fig, ax, specdic, [names[0]], startval)

                    _VARS['window'] = SpecWin(names)

                    vline = ax.axvline(x=specdic[f'{names[0]}'][0][0], picker=True)
                    vline2 = ax.axvline(x=specdic[f'{names[0]}'][0][-1], picker=True, color='red')

                    makeData(fig, ax)

                    linex1 = vline.get_xdata()[0]
                    linex2 = vline2.get_xdata()[0]

                    showverts = True
                    epsilon = 5
                    ind = None
                    fig.canvas.mpl_connect('pick_event', on_pick_leg)
                    ind = fig.canvas.mpl_connect('button_press_event', on_button_press)
                    fig.canvas.mpl_connect('key_press_event', on_key_press)
                    fig.canvas.mpl_connect('button_release_event', on_button_release)
                    fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
                except AttributeError:
                    pass
        if event == 'Image':
            filename=sg.popup_get_file('Choose file (PNG, SVG, JPG) to save to', save_as=True)
            try:
                if filename.lower().endswith('.svg') or filename.endswith('.png') or filename.endswith('.jpg'):
                    pass
                else:
                    filename += '.png'        
                fig.savefig(filename)
            except AttributeError:
                pass
        if values['Leg'] == True:
            leg.set_visible(True)
            fig.canvas.draw_idle() 
        if values['Leg'] == False:
            leg.set_visible(False)
            fig.canvas.draw_idle()       
    if check:
        _VARS['window'].close()


