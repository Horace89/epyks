from Tkconstants import W
from Tkinter import Tk, BOTH, END, Canvas
import re
from ttk import Frame, Button, Style, Entry, Label
import tkMessageBox
from mock import Mock
from proto.parallels import SHUTDOWN
from networking.base import get_local_addr

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
        self.running_on = "%s:%s" % (get_local_addr(), getattr(self.caller_instance, 'port', None) or "8888")
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.__centerWindow()
        self.parent.title("epyks %s" % self.running_on)
        #self.pack(fill=BOTH, expand=1)
        #
        #   Addr textbox
        #
        addr_validate = (self.parent.register(self.addrValidation), '%S', '%d')
        self.EntryAddress = Entry(self, validate='key', validatecommand=addr_validate, width=17)
        self.EntryAddress.grid(row=0, column=0, padx=10, pady=5, columnspan=3, sticky=W)
        self.EntryAddress.delete(0, END)
        self.EntryAddress.insert(0, "192.168.0.102:8889")
        #
        #   Call button
        #
        self.ButtonCall = Button(self, text="Call",  command=self.onButtonCallClick)
        self.ButtonCall.grid(row=0, column=3, pady=5)
        #
        #   Callmode status canvas
        #
        self.CanvasCallmode = Canvas(self, width=20, height=20, bg="light grey")
        self.CanvasCallmode.create_oval(1, 1, 20, 20, fill="red", outline="light grey")
        self.CanvasCallmode.grid(row=1, column=0, pady=0, padx=10, sticky=W)
        #
        #   Callmode status label
        #
        self.LabelCallmode = Label(self, text="Not connected")
        self.LabelCallmode.grid(row=1, column=0, padx=35)
        #
        #   End call button
        #
        self.ButtonEndCall = Button(self, text="End call",  command=self.onButtonEndCallClick)
        self.ButtonEndCall.grid(row=1, column=3)

        # Testing

        # Pack all
        self.pack(fill=BOTH, expand=1)

    def addrValidation(self, string, action):
        if action != 1:
            # 0 - delete, 1 - insert, -1 - focus in/out
            return True
        print "addrValidation: %s" % string
        if len(string) > 1:
            return full_ipv4_check(fulladdr=string)
        return string in ACCEPTABLE_CHARS

    def onTextBoxChange(self, *args, **kwargs):
        print 'lol ' + str(args) + str(kwargs)

    def onButtonCallClick(self):
        address = (self.EntryAddress.get())
        if not full_ipv4_check(fulladdr=address):
            tkMessageBox.showerror(message="Incorrect address")
        ip, port = address.split(':')
        self.caller_instance.call((ip, int(port)))

    def onButtonEndCallClick(self):
        self.caller_instance.hang_up()

    def checkStatus(self):
        status = self.caller_instance.status
        if status.startswith('On'):
            self.CanvasCallmode.create_oval(1, 1, 20, 20, fill="green", outline="light grey")
            self.EntryAddress.configure(state='readonly')
        elif status.startswith('Not'):
            self.CanvasCallmode.create_oval(1, 1, 20, 20, fill="red", outline="light grey")
            self.EntryAddress.configure(state='')
        else:
            self.CanvasCallmode.create_oval(1, 1, 20, 20, fill="yellow", outline="light grey")
            self.EntryAddress.configure(state='readonly')
        self.LabelCallmode['text'] = status
        self.parent.after(ms=100, func=self.checkStatus)

    def __centerWindow(self):
        w = 250
        h = 70
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


def initialize(caller_instance):
    root = Tk()
    root.resizable(0, 0)
    app = MainForm(parent=root, caller_instance=caller_instance)
    root.after(ms=100, func=app.checkStatus)
    root.mainloop()
    SHUTDOWN.set()

if __name__ == '__main__':
    caller_instance = Mock
    caller_instance.status = "Not connected"
    caller_instance.port = "3333"
    initialize(caller_instance)