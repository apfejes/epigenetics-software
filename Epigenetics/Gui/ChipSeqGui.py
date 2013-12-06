'''
Created on 2013-03-06

@author: dfornika
@author: afejes
'''


import multiprocessing
import Tkinter as tk
import tkFileDialog
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator")    # add the utilities folder here
sys.path.insert(0, _cur_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")

from TheWaveGenerator import main as wg_main
from CommonUtils.Parameters import parameter
from . import ParametersEditor

class Application(tk.Tk):
    """Main Application Class"""
    def __init__(self):
        """Constructor"""
        tk.Tk.__init__(self)
        self.title("Epigenetics Analysis Suite")
        self.createWidgets()
        self.parameters = parameter(_root_dir + os.sep + '/WaveGenerator/sample_input_chipseq.input')

    def createWidgets(self):
        '''Generate the widgets on the form'''
        menu_bar = tk.Menu(self)
        self.config(menu = menu_bar)

        file_menu = tk.Menu(menu_bar)
        file_menu.add_command(label = "Open...", command = self.askopenfilename)
        file_menu.add_command(label = "Exit", command = self.quit)
        menu_bar.add_cascade(label = "File", menu = file_menu)

        edit_menu = tk.Menu(menu_bar)
        edit_menu.add_command(label = "Parameters", command = self.launchParametersEditor)
        menu_bar.add_cascade(label = "Edit", menu = edit_menu)

        run_wg_but = tk.Button(text = "Run WaveGenerator", command = lambda: self.run_wg(self.parameters))
        run_wg_but.pack()

    @classmethod
    def run_wg(cls, parameters):
        '''function to launch the wave generator'''
        wg_proc = multiprocessing.Process(target = wg_main, args = (parameters,))
        wg_proc.start()

    def launchParametersEditor(self):
        '''start the parameter editor'''
        _parameters_editor = ParametersEditor.ParametersEditor(self, self.parameters)

    def askopenfilename(self):
        '''dialog box for opening a new input filename'''
        filename = tkFileDialog.askopenfilename(defaultextension = '.input', title = 'Open File')
        if filename:
            self.parameters.set('input_file', filename)

def main():
    '''start the application'''
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()
