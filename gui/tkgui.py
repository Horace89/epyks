
from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style, Entry
import tkMessageBox

ACCEPTABLE_CHARS = "1234567890:."


def is_char_acceptable(char):
    global ACCEPTABLE_CHARS
    if char in ACCEPTABLE_CHARS:
        return True
    return False


# noinspection PyAttributeOutsideInit
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
        #
        #   Call button
        #
        self.buttonCall = Button(self, text="Call",  command=self.onCallClick)
        self.buttonCall.place(x=50, y=50)
        #
        #   Addr textbox
        #
        addr_validate = (self.parent.register(self.addrValidation), '%S',)
        self.entryAddress = Entry(self, validate='key', validatecommand=addr_validate, background="black")
        self.entryAddress.place(x=100, y=50)

    def addrValidation(self, char):
        print "addrValidation: %s" % (char)
        return is_char_acceptable(char)


    def isOkay(self, what):
        return is_char_acceptable(what)

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