from Tkinter import *

class Application(Frame):
    def hello(self):
        print "Hello world!" 
    
    def createWidget(self):
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
    
    def __init__(self, master=None):
        Frame.__init__(self, master=None)
        self.pack()
        self.createWidget()



root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
