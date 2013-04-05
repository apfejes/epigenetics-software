import Tkinter as tk
from tkFileDialog import askopenfilename
from ..WaveGenerator.Utilities.Parameters import parameter

class ParametersEditor (tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Parameters Editor")
        self.geometry("640x320")
        self.createWidgets()

    def createWidgets(self):
        self.input_options_frame = tk.LabelFrame(self, text="Input Options")
        self.input_options_frame.grid(row=0, column=0)
        self.input_file_lab = tk.Label(self.input_options_frame, text="Input File:").grid(row=0)
        self.input_file_entry = tk.Entry(self.input_options_frame)
        self.input_file_entry.grid(row=0, column=1)
        self.input_file_button = tk.Button(self.input_options_frame, text="Browse...", command=askopenfilename)
        self.input_file_button.grid(row=0, column=2)
        
        self.extension_options_frame = tk.LabelFrame(self, text="Extension Options")
        self.extension_options_frame.grid(row=1, column=0)
        self.map_type_lab = tk.Label(self.extension_options_frame, text="Map Type:").grid(row=1)
        choices = ['Native Distribution - coverage is only for sequenced bases',
                   'Flat Distribution - coverage is extended to user provided length',
                   'Triangle Distribution - weighted coverage using user provided values']
        map_type_selected = tk.StringVar(self.parent)
        map_type_selected.set(choices[0])
        self.map_type_option = tk.OptionMenu(self.extension_options_frame, map_type_selected, *choices).grid(row=1, column=1)

        self.triangle_min_lab = tk.Label(self.extension_options_frame, text="Triangle Minimum:").grid(row=2, column=0)
        self.triangle_min_scale = tk.Scale(self.extension_options_frame, from_=0, to=500, orient=tk.HORIZONTAL)
        self.triangle_min_scale.grid(row=2, column = 1)
        self.triangle_min_scale.set(200)

        self.triangle_median_lab = tk.Label(self.extension_options_frame, text="Triangle Median:").grid(row=3, column=0) 
        self.triangle_median_entry = tk.Scale(self.extension_options_frame, from_=0, to=500, orient=tk.HORIZONTAL)
        self.triangle_median_entry.grid(row=3, column = 1)
        self.triangle_median_entry.set(250)

        self.fragment_length_lab = tk.Label(self.extension_options_frame, text="Fragment Length:").grid(row=4, column=0)
        self.fragment_length_entry = tk.Entry(self.extension_options_frame)
        self.fragment_length_entry.grid(row=4,column=1)
        self.fragment_length_entry.insert(0, 300)

        round_leading_edge = tk.IntVar(self.parent)
        self.round_leading_edge_button = tk.Checkbutton(self.extension_options_frame, text="Round Leading Edge",
                                                        variable=round_leading_edge, onvalue=True, 
                                                        offvalue=False).grid(row=5, column=0)

        self.max_pet_length_lab = tk.Label(self.extension_options_frame, text="Max PET Length:").grid(row=6, column=0)
        self.max_pet_length_entry = tk.Entry(self.extension_options_frame).grid(row=6,column=1)
        
        self.wave_calling_options_frame = tk.LabelFrame(self, text="Wave Calling Options")
        self.wave_calling_options_frame.grid(row=2, column=0)
        self.min_height_lab = tk.Label(self.wave_calling_options_frame, text="Minimum Height:")
        self.min_height_lab.grid(row=7, column=0)
        self.min_height_entry = tk.Entry(self.wave_calling_options_frame)
        self.min_height_entry.grid(row=7,column=1)
        
        self.processor_threads_lab = tk.Label(self, text="Processor Threads:").grid(row=8, column=0)
        self.processor_threads_entry = tk.Entry(self).grid(row=8,column=1)
        
        self.output_path_lab = tk.Label(self, text="Output Path:").grid(row=9, column=0)
        self.output_path_entry = tk.Entry(self).grid(row=9,column=1)
        
        self.file_name_lab = tk.Label(self, text="Output Filename Prefix:").grid(row=10, column=0)
        self.file_name_entry = tk.Entry(self)
        self.file_name_entry.grid(row=10,column=1)

        number_waves = tk.IntVar(self.parent)
        self.number_waves_button = tk.Checkbutton(self, text="Number Waves",
                                                  variable=number_waves, onvalue=True,
                                                  offvalue=False)
        self.number_waves_button.grid(row=11, column=0)

        make_wig = tk.IntVar(self.parent)
        self.make_wig_button = tk.Checkbutton(self, text="Make Wig File",
                                              variable=make_wig, onvalue=True,
                                              offvalue=False)
        self.make_wig_button.grid(row=12, column=0)

        self.load = tk.Button(self, text="Load...", command=askopenfilename)
        self.load.grid(row=13, column=0)
        self.save = tk.Button(self, text="Save...")
        self.save.grid(row=13, column=1)
        self.cancel = tk.Button(self, text="Cancel", command=self.withdraw)
        self.save.grid(row=13, column=2)

    def writeToFile():
        pass

    def readParameterFile():
        pass
