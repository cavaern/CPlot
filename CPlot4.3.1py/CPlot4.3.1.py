import Grid as G
import Line as L
import MP as M
import Spec as S
import glob
import os
import PySimpleGUI as sg
cwd = os.getcwd()



my_new_theme = {'BACKGROUND': '#B4B9C7',
                        'TEXT': '#023f4a',
                        'INPUT': '#f2f7fb',
                        'TEXT_INPUT': '#000000',
                        'SCROLL': '#c7e78b',
                        'BUTTON': ('white', '#3526CB'),
                        'PROGRESS': ('#01826B', '#D0D0D0'),
                        'BORDER': 1,
                        'SLIDER_DEPTH': 0,
                        'PROGRESS_DEPTH': 0}
         
sg.theme_add_new('MyNewTheme', my_new_theme)
        

        


def main(cwd):
    AppFont = 'Any 16'
    sg.theme('MyNewTheme')
    col1=[[sg.B('Spectra', size=(10,1))],
        [sg.B('Grid', size=(10,1))],
           [sg.B('Linescan', size=(10,1))],
          [sg.B('Multipass', size=(10,1))],
          [sg.B('Exit', size=(10,1))]]  
    col2=[[sg.Image(r'{}\Images\BB VB 1503.png'.format(cwd),
size=(150,150))],]

    layout=[[[sg.Column(col1, element_justification='c'), sg.Column(col2,
element_justification='c')]]
        ]
    win=sg.Window('CPlot', layout, location=(0,0))
    while True:
        e,vm=win.read()
        if e == 'Exit' or e == sg.WIN_CLOSED:
            break
        elif e == 'Grid':
            G.Grid()
        elif e == 'Linescan':
            L.Line()
        elif e == 'Multipass':
            M.MP()
        elif e == 'Spectra':
            S.Spec()
    win.close()

a=main(cwd)
      
