'''
Created on 2013-03-06

@author: afejes
'''

from Tkinter import *

class Application(Frame):

    def createWidget(self):
        self.Text = Label(self)
        self.Text["text"] = "Hello World!"
        self.Text.pack()

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["command"] = self.quit

        self.QUIT.pack({"side":"left"})

        self.hi = Button(self)
        self.hi["text"] = "Run"
        self.hi["command"] = self.run

        self.hi.pack({"side":"left"})

        choices = ['Native Distribution - coverage is only for sequenced bases',
                   'Flat Distribution - coverage is extended to user provided length',
                   'Triangle Distribution - weighted coverage using user provided values']
        self.OptionMenu = OptionMenu(root, 0, *choices)
        self.OptionMenu.pack({"side":"left"})
        # option = self.OptionMenu(root, 0, *choices)

    def run(self):
        pass

    def __init__(self, master = None):
        Frame.__init__(self, master = None)
        self.pack()
        self.createWidget()


root = Tk()
app = Application(master = root)
app.mainloop()
root.destroy()
