''' A simple testing framework for GUI applications.  Doesn't do a whole heck of a lot. '''


from Tkinter import Frame, Label, Button, Tk

class Application(Frame):
    ''' Framework for GUI testing '''

    @staticmethod
    def hello():
        ''' Testing framework for GUI applications.  Does not do much, at this point'''
        print "Hello world!"

    def createWidget(self):
        ''' creates widgets for the GUI '''
        self.Text = Label(self)
        self.Text["text"] = "Hello World!"
        self.Text.pack()

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side":"left"})

        self.hi = Button(self)
        self.hi["text"] = "Hi"
        self.hi["command"] = self.hello

        self.hi.pack({"side":"left"})

    def __init__(self, master = None):
        ''' Initialize the GUI and call create widget '''
        Frame.__init__(self, master = None)
        self.pack()
        self.createWidget()

        self.hi = None
        self.QUIT = None
        self.Text = None



root = Tk()
app = Application(master = root)
app.mainloop()
root.destroy()
