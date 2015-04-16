
from Tkinter import Tk, BOTH, END
import re
from ttk import Frame, Button, Style, Entry
import tkMessageBox

ACCEPTABLE_CHARS = "1234567890:."
IPV4_RE = "(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}"

# noinspection PyAttributeOutsideInit,PyPep8Naming,PyMethodMayBeStatic,PyShadowingBuiltins
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
        self.parent.title("epyks")
        self.pack(fill=BOTH, expand=1)
        #
        #   Call button
        #
        self.ButtonCall = Button(self, text="Call",  command=self.onButtonCallClick)
        self.ButtonCall.place(x=200, y=50)
        #
        #   Addr textbox
        #
        addr_validate = (self.parent.register(self.addrValidation), '%S',)
        self.EntryAddress = Entry(self, validate='key', validatecommand=addr_validate)
        self.EntryAddress.delete(0, END)
        self.EntryAddress.insert(0, "192.168.0.102:8889")
        #self.EntryAddress.pack()
        self.EntryAddress.place(x=10, y=50)

    def addrValidation(self, input):
        print "addrValidation: %s" % input
        if len(input) > 1:
            return True if re.match(pattern=IPV4_RE, string=input) else False  # because module "re" returns SRE object, we need boolean
        return input in ACCEPTABLE_CHARS

    def onTextBoxChange(self, *args, **kwargs):
        print 'lol ' + str(args) + str(kwargs)

    def onButtonCallClick(self, *args, **kwargs):
        addr = (self.EntryAddress.get())
        print addr
        print re.match(pattern=IPV4_RE, string=addr) is None
        print re.match(pattern=IPV4_RE, string=addr) is not None
        if not re.match(pattern=IPV4_RE, string=addr):
            tkMessageBox.showerror(message="Incorrect ip address", title="Error")
        tkMessageBox.showinfo(title="Call", message=str(args) + str(kwargs))

    def __centerWindow(self):
        w = 300
        h = 100
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