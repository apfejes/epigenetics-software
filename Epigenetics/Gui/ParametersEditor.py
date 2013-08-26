import sys
import traceback
import Tkinter as tk
from tkFileDialog import askopenfilename, asksaveasfilename, askdirectory


class ParametersEditor (tk.Toplevel):
    '''the parameter editor'''
    def __init__(self, parent, parameters):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.parameters = parameters
        self.title("Parameters Editor")
        self.config(padx = 5, pady = 5)
        self.resizable(0, 0)
        self.createWidgets()


        # initializing variatbles
        self.cancel_but = None
        self.input_options_frame = None
        self.input_file_lab = None
        self.input_file_entry = None
        self.input_file_but = None
        self.extension_options_frame = None
        self.map_type_lab = None
        self.choices = None
        self.map_type_selected = None
        self.map_type_option = None
        self.triangle_min_lab = None
        self.triangle_min_scale = None
        self.triangle_median_lab = None
        self.triangle_median_scale = None
        self.fragment_length_lab = None
        self.fragment_length_entry = None
        self.max_pet_length_lab = None
        self.max_pet_length_entry = None
        self.round_leading_edge = None
        self.round_leading_edge_button = None
        self.wave_calling_options_frame = None
        self.min_height_lab = None
        self.min_height_entry = None
        self.runtime_configuration_options_frame = None
        self.processor_threads_lab = None
        self.processor_threads_entry = None
        self.output_options_frame = None

        self.output_path_lab = None
        self.output_path_entry = None
        self.output_path_button = None
        self.file_name_lab = None
        self.file_name_entry = None

        self.number_waves = None
        self.number_waves_button = None
        self.make_wig = None
        self.make_wig_button = None
        self.bottom_button_frame = None
        self.apply_but = None
        self.load_but = None
        self.save_as_but = None
        self.cancel_but = None


    def createWidgets(self):
        '''The function to create the widgets on the form'''
        # Input Options
        self.input_options_frame = tk.LabelFrame(self, text = "Input Options", padx = 5, pady = 5)
        self.input_options_frame.grid(row = 0, column = 0, sticky = tk.EW)
        self.input_options_frame.columnconfigure(0, weight = 1)
        self.input_file_lab = tk.Label(self.input_options_frame, text = "Input File:")
        self.input_file_lab.grid(row = 0, column = 0, sticky = tk.W)
        self.input_file_entry = tk.Entry(self.input_options_frame)
        self.input_file_entry.grid(row = 0, column = 1, sticky = tk.EW)
        self.input_file_but = tk.Button(self.input_options_frame, text = "Browse...", command = self.askinputfile)
        self.input_file_but.grid(row = 0, column = 2, sticky = tk.E)

        # Extension Options
        self.extension_options_frame = tk.LabelFrame(self, text = "Extension Options", padx = 5, pady = 5)
        self.extension_options_frame.grid(row = 1, column = 0, sticky = tk.EW)
        self.extension_options_frame.columnconfigure(0, weight = 1)
        self.map_type_lab = tk.Label(self.extension_options_frame, text = "Map Type:")
        self.map_type_lab.grid(row = 0, column = 0, sticky = tk.W)
        self.choices = ['Native',
                        'Flat',
                        'Triangle']
        self.map_type_selected = tk.StringVar(self)
        self.map_type_selected.set(self.choices[0])
        self.map_type_option = tk.OptionMenu(self.extension_options_frame, self.map_type_selected, *self.choices)
        self.map_type_option.config(width = 20)
        self.map_type_option.grid(row = 0, column = 1, columnspan = 2)

        self.triangle_min_lab = tk.Label(self.extension_options_frame, text = "Triangle Minimum:")
        self.triangle_min_lab.grid(row = 1, column = 0, sticky = tk.SW)
        self.triangle_min_scale = tk.Scale(self.extension_options_frame, from_ = 0, to = 500, length = 200, orient = tk.HORIZONTAL)
        self.triangle_min_scale.grid(row = 1, column = 1)
        self.triangle_min_scale.set(200)

        self.triangle_median_lab = tk.Label(self.extension_options_frame, text = "Triangle Median:")
        self.triangle_median_lab.grid(row = 2, column = 0, sticky = tk.SW)
        self.triangle_median_scale = tk.Scale(self.extension_options_frame, from_ = 0, to = 500, length = 200, orient = tk.HORIZONTAL)
        self.triangle_median_scale.grid(row = 2, column = 1)
        self.triangle_median_scale.set(250)

        self.fragment_length_lab = tk.Label(self.extension_options_frame, text = "Fragment Length:")
        self.fragment_length_lab.grid(row = 3, column = 0, sticky = tk.W)
        self.fragment_length_entry = tk.Entry(self.extension_options_frame)
        self.fragment_length_entry.grid(row = 3, column = 1)

        self.max_pet_length_lab = tk.Label(self.extension_options_frame, text = "Max PET Length:")
        self.max_pet_length_lab.grid(row = 4, column = 0, sticky = tk.W)
        self.max_pet_length_entry = tk.Entry(self.extension_options_frame)
        self.max_pet_length_entry.grid(row = 4, column = 1)

        self.round_leading_edge = tk.IntVar(self.parent)
        self.round_leading_edge_button = tk.Checkbutton(self.extension_options_frame, text = "Round Leading Edge",
                                                        variable = self.round_leading_edge, onvalue = True,
                                                        offvalue = False)
        self.round_leading_edge_button.grid(row = 5, column = 1)

        # Wave Calling Options
        self.wave_calling_options_frame = tk.LabelFrame(self, text = "Wave Calling Options", padx = 5, pady = 5)
        self.wave_calling_options_frame.grid(row = 2, column = 0, sticky = tk.EW)
        self.wave_calling_options_frame.columnconfigure(0, weight = 1)
        self.min_height_lab = tk.Label(self.wave_calling_options_frame, text = "Minimum Height:")
        self.min_height_lab.grid(row = 0, column = 0, sticky = tk.W)
        self.min_height_entry = tk.Entry(self.wave_calling_options_frame)
        self.min_height_entry.grid(row = 0, column = 1)

        # Runtime Configuration Options
        self.runtime_configuration_options_frame = tk.LabelFrame(self, text = "Run Time Configuration", padx = 5, pady = 5)
        self.runtime_configuration_options_frame.grid(row = 3, column = 0, sticky = tk.EW)
        self.runtime_configuration_options_frame.columnconfigure(0, weight = 1)
        self.processor_threads_lab = tk.Label(self.runtime_configuration_options_frame, text = "Processor Threads:")
        self.processor_threads_lab.grid(row = 0, column = 0, sticky = tk.W)
        self.processor_threads_entry = tk.Entry(self.runtime_configuration_options_frame)
        self.processor_threads_entry.grid(row = 0, column = 1, sticky = tk.EW)

        # Output Options
        self.output_options_frame = tk.LabelFrame(self, text = "Output Options", padx = 5, pady = 5)
        self.output_options_frame.grid(row = 4, column = 0, sticky = tk.EW)
        self.output_options_frame.columnconfigure(0, weight = 1)
        self.output_path_lab = tk.Label(self.output_options_frame, text = "Output Path:")
        self.output_path_lab.grid(row = 0, column = 0, sticky = tk.W)
        self.output_path_entry = tk.Entry(self.output_options_frame)
        self.output_path_entry.grid(row = 0, column = 1)
        self.output_path_button = tk.Button(self.output_options_frame, text = "Browse...", command = self.askdirectory)
        self.output_path_button.grid(row = 0, column = 2)
        self.file_name_lab = tk.Label(self.output_options_frame, text = "Output Prefix:")
        self.file_name_lab.grid(row = 1, column = 0, sticky = tk.W)
        self.file_name_entry = tk.Entry(self.output_options_frame)
        self.file_name_entry.grid(row = 1, column = 1)

        self.number_waves = tk.IntVar(self.parent)
        self.number_waves_button = tk.Checkbutton(self.output_options_frame, text = "Number Waves",
                                                  variable = self.number_waves, onvalue = True,
                                                  offvalue = False)
        self.number_waves_button.grid(row = 2, column = 1, sticky = tk.W)

        self.make_wig = tk.IntVar(self.parent)
        self.make_wig_button = tk.Checkbutton(self.output_options_frame, text = "Make Wig File",
                                              variable = self.make_wig, onvalue = True,
                                              offvalue = False)
        self.make_wig_button.grid(row = 3, column = 1, sticky = tk.W)

        # Bottom buttons (Apply, Load..., Save As..., Cancel)
        self.bottom_button_frame = tk.Frame(self, padx = 5, pady = 5)
        self.bottom_button_frame.grid(row = 5, column = 0)
        self.apply_but = tk.Button(self.bottom_button_frame, text = "Apply", command = self.apply_parameters)
        self.apply_but.grid(row = 0, column = 0)
        self.load_but = tk.Button(self.bottom_button_frame, text = "Load...", command = self.askopenfile)
        self.load_but.grid(row = 0, column = 1)
        self.save_as_but = tk.Button(self.bottom_button_frame, text = "Save...", command = self.asksaveasfile)
        self.save_as_but.grid(row = 0, column = 2)
        self.cancel_but = tk.Button(self.bottom_button_frame, text = "Cancel", command = self.withdraw)
        self.cancel_but.grid(row = 0, column = 3)

    def asksaveasfile(self):
        '''function to save parameters to a file'''
        self.apply_parameters()
        filename = asksaveasfilename()
        if filename:
            f = open(filename, mode = 'w')
            for key, value in self.parameters.parameters.iteritems():
                f.write(key + " = " + str(value) + "\n")
            f.close()

    def apply_parameters(self):
        '''Apply the parameters in an input file'''
        # Input Options
        self.parameters.set_parameter('input_file', self.input_file_entry.get())

        # Extension Options
        self.parameters.set_parameter('map_type', self.map_type_selected.get())
        self.parameters.set_parameter('triangle_min', self.triangle_min_scale.get())
        self.parameters.set_parameter('triangle_median', self.triangle_median_scale.get())
        self.parameters.set_parameter('fragment_length', int(self.fragment_length_entry.get()))
        self.parameters.set_parameter('round_leading_edge', int(self.round_leading_edge.get()))
        self.parameters.set_parameter('max_pet_length', int(self.max_pet_length_entry.get()))

        # Wave Calling Options
        self.parameters.set_parameter('min_height', int(self.min_height_entry.get()))

        # Runtime Configuration Options
        self.parameters.set_parameter('processor_threads', int(self.processor_threads_entry.get()))

        # Output Options
        self.parameters.set_parameter('output_path', self.output_path_entry.get())
        self.parameters.set_parameter('file_name', self.file_name_entry.get())
        if (self.number_waves.get() == 0):
            self.parameters.set_parameter('number_waves', False)
        elif (self.number_waves.get() == 1):
            self.parameters.set_parameter('number_waves', True)
        if (self.make_wig.get() == 0):
            self.parameters.set_parameter('make_wig', False)
        elif (self.make_wig.get() == 1):
            self.parameters.set_parameter('make_wig', True)
        if (self.round_leading_edge.get() == 0):
            self.parameters.set_parameter('round_leading_edge', False)
        elif (self.round_leading_edge.get() == 1):
            self.parameters.set_parameter('round_leading_edge', True)

        # Close the Parameter Editor Window
        self.withdraw()

    def askopenfile(self):
        filename = askopenfilename()
        if filename:
            try:
                f = open(filename, 'r')
                for line in f:
                    if line.startswith("#"):
                        continue
                    else:
                        a = line.split("=")
                        key = a[0].strip()
                        value = a[1].strip()
                        print "read:", key, "->", value
                        if self.parameters.isint(value):    # handle ints
                            self.parameters.parameters[key] = int(value)
                        elif self.parameters.isfloat(value):    # handle floats
                            self.parameters.parameters[key] = float(value)
                        elif self.parameters.isbool(value):    # handle booleans
                            if (value.lower() == "true"):
                                self.parameters.parameters[key] = True
                            else:
                                self.parameters.parameters[key] = False
                        else:    # handle strings
                            self.parameters.parameters[key] = value
                f.close()
            except:
                print "Unexpected error in parameter reading:", sys.exc_info()[0]
                print "Reading parameters failed."
                print traceback.format_exc()

            # Input Options
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(0, self.parameters.get_parameter('input_file'))

            # Extension Options
            self.map_type_selected.set(self.parameters.get_parameter('map_type'))
            self.triangle_min_scale.set(self.parameters.get_parameter('triangle_min'))
            self.triangle_median_scale.set(self.parameters.get_parameter('triangle_median'))
            self.fragment_length_entry.delete(0, tk.END)
            self.fragment_length_entry.insert(0, str(self.parameters.get_parameter('fragment_length')))
            self.round_leading_edge.set(self.parameters.get_parameter('round_leading_edge'))
            if (self.parameters.get_parameter('round_leading_edge')):
                self.round_leading_edge_button.select()
            else:
                self.round_leading_edge_button.deselect()
            self.max_pet_length_entry.delete(0, tk.END)
            self.max_pet_length_entry.insert(0, str(self.parameters.get_parameter('max_pet_length')))

            # Wave Calling Options
            self.min_height_entry.delete(0, tk.END)
            self.min_height_entry.insert(0, str(self.parameters.get_parameter('min_height')))

            # Runtime Configuration Options
            self.processor_threads_entry.delete(0, tk.END)
            self.processor_threads_entry.insert(0, str(self.parameters.get_parameter('processor_threads')))

            # Output Options
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, self.parameters.get_parameter('output_path'))
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.insert(0, self.parameters.get_parameter('file_name'))
            if (self.parameters.get_parameter('number_waves')):
                self.number_waves_button.select()
            else:
                self.number_waves_button.deselect()
            if (self.parameters.get_parameter('make_wig')):
                self.make_wig_button.select()
            else:
                self.make_wig_button.deselect()

    def askdirectory(self):
        path = askdirectory()
        if path:
            self.parameters.set_parameter('output_path', path)
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, self.parameters.get_parameter('output_path'))

    def askinputfile(self):
        filename = askopenfilename()
        if filename:
            self.parameters.set_parameter('input_file', filename)
            self.input_file_entry.delete(0, tk.END)
            self.input_file_entry.insert(0, self.parameters.get_parameter('input_file'))
