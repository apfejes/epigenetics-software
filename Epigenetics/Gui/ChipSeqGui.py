'''
Created on 2013-03-06

@author: dfornika
@author: afejes
'''
import multiprocessing
import tempfile
import Tkinter as tk
import tkFileDialog

from TheWaveGenerator import main as wg_main
from Parameters import parameter
from ParametersEditor import ParametersEditor

class Application(tk.Tk):
    """Main Application Class"""
    def __init__(self):
        """Constructor"""
        tk.Tk.__init__(self)
        self.title("Epigenetics Analysis Suite")
        self.createWidgets()
        self.parameters = parameter('../WaveGenerator/sample_input_chipseq.input')

    def createWidgets(self):
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

    def run_wg(self, parameters):
        temp_paramfile = tempfile.NamedTemporaryFile(prefix = 'wavegen_', suffix = '.input', delete = False)
        for key, value in parameters.parameters.iteritems():
            temp_paramfile.write('%s = %s\n' % (key, str(value)))
        wg_proc = multiprocessing.Process(target = wg_main, args = (temp_paramfile.name,))
        wg_proc.start()

    def launchParametersEditor(self):
        parameters_editor = ParametersEditor(self, self.parameters)

    def askopenfilename(self):
        filename = tkFileDialog.askopenfilename(defaultextension = '.input', title = 'Open File')
        if filename:
            self.parameters.set_parameter('input_file', filename)

def main():
    app = Application()
    app.mainloop()

if __name__ == '__main__':
    main()
