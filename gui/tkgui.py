
from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style, Entry
import tkMessageBox


class Example(Frame):
    """
    If method is handling some GUI shit, its written in camelCase style
    """

    def __init__(self, parent, caller_instance):
        Frame.__init__(self, parent)
        self.caller_instance = caller_instance
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.__centerWindow()
        self.parent.title("epyks!")
        self.pack(fill=BOTH, expand=1)
        quitButton = Button(self, text="Call",  command=self.onCallClick)
        quitButton.place(x=50, y=50)
        #addressTextBox = Entry(self,) # command=self.onTextBoxChange)
        #addressTextBox.place(x=200, y=50)
        okayCommand = self.register(self.isOkay)
        self.w = Entry(self, validate='key', validatecommand=(okayCommand, '%P'))
        self.w.place(x=100, y=50)


    def isOkay(self, what):
        print what
        return True

    def onTextBoxChange(self, *args, **kwargs):
        print 'lol ' + str(args) + str(kwargs)

    def onCallClick(self, *args, **kwargs):
        tkMessageBox.showinfo(title="Call", message=str(args) + str(kwargs))

    def __centerWindow(self):
        w = 500
        h = 500
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

def initialize(caller_instance):
    root = Tk()
    root.resizable(0, 0)
    app = Example(parent=root, caller_instance=caller_instance)
    root.mainloop()

if __name__ == '__main__':
    initialize(None)