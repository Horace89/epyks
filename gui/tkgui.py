
from Tkinter import Tk, BOTH, END
import re
from ttk import Frame, Button, Style, Entry
import tkMessageBox

ACCEPTABLE_CHARS = "1234567890:."
IPV4_RE = re.compile(ur'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')


def full_ipv4_check(fulladdr):
    if ':' not in fulladdr:
        return False
    ip, port = fulladdr.split(':')
    return True if IPV4_RE.match(ip) and (1 < int(port) < 65536) else False

# noinspection PyAttributeOutsideInit,PyPep8Naming,PyMethodMayBeStatic,PyShadowingBuiltins
class MainForm(Frame):
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
        addr_validate = (self.parent.register(self.addrValidation), '%S', '%d')
        self.EntryAddress = Entry(self, validate='key', validatecommand=addr_validate)
        self.EntryAddress.delete(0, END)
        self.EntryAddress.insert(0, "192.168.0.102:8889")
        self.EntryAddress.place(x=10, y=50)

    def addrValidation(self, input, action):
        if action != 1:
            # 0 - delete, 1 - insert, -1 - focus in/out
            return True
        print "addrValidation: %s" % input
        if len(input) > 1:
            return full_ipv4_check(fulladdr=input)
        return input in ACCEPTABLE_CHARS

    def onTextBoxChange(self, *args, **kwargs):
        print 'lol ' + str(args) + str(kwargs)

    def onButtonCallClick(self):
        address = (self.EntryAddress.get())
        if not full_ipv4_check(fulladdr=address):
            tkMessageBox.showerror(message="Incorrect address")
        ip, port = address.split(':')
        self.caller_instance.call((ip, int(port)))

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
    app = MainForm(parent=root, caller_instance=caller_instance)
    root.mainloop()

if __name__ == '__main__':
    initialize(None)