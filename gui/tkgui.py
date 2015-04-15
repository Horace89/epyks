from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style
import tkMessageBox as box
class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.parent.title("epyks")
        self.call_button = Button(self, text="Call", command=self.onCallButton)
        self.pack(fill=BOTH, expand=1)
        self.center_window()

    def onCallButton(self):
        box.showinfo("Yo", "message")

    def center_window(self):
        w = 290
        h = 150
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry("%dx%d+%d+%d" % (w, h, x, y))

def main():
    root = Tk()
    root.resizable(0, 0)
    app = Example(root)
    root.mainloop()

if __name__ == '__main__':
    main()