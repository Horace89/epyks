import functools
import os
import npyscreen
from networking import base
import pdb

#
# #
# class Asdf(npyscreen.Form):
#     def create(self):
#         super(myEmployeeForm, self).create()
#         self.name = self.add(npyscreen.TitleText, name='name')
#         self.department = self.add(npyscreen.TitleSelectOne, name='department',
#                                    max_height=3,
#                                    values=['black mesa', 'nova prospect', 'city 17'],
#                                    scroll_exit=True)
#         self.date = self.add(npyscreen.TitleDateCombo, name='date joined')
#
#     def afterEditing(self):
#         self.parentApp.setNextForm(None)


# noinspection PyAttributeOutsideInit
class MainForm(npyscreen.Form):
    OK_BUTTON_TEXT = "EXIT"  # well...

    def __init__(self, *args, **kwargs):
        self.callfunc = kwargs['call_func']
        super(MainForm, self).__init__(*args, **kwargs)

    def create(self):
        super(MainForm, self).create()
#        self.is_field_here()
        self.name = self.add(npyscreen.TitleText, name="username")
        self.call_to_addr = self.add(npyscreen.TitleText, name="call to addr", value="192.168.0.102")
        self.call_to_port = self.add(npyscreen.TitleText, name="call to port", value="8889")
        self.call_button = self.add(npyscreen.ButtonPress, name="call",
                                    #when_pressed_function=self.callfunc(self.call_to.value))
                                    when_pressed_function=self.makecall)
        self.parentApp.setNextForm('username_form')

    def makecall(self):
        print 'when pressed'
        ip = self.call_to_addr.value
        port = int(self.call_to_port.value)
        self.parentApp.caller_instance.call((ip, port))

    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def start_call(self):
        self.parentApp.server.enter_callmode()

# noinspection PyAttributeOutsideInit
class IntroduceYourself(npyscreen.Popup):

    def create(self):
        self.greeting = self.add(npyscreen.TitleText, name="Username", value=os.getenv('USER'))
        self.lo_addr = self.add(npyscreen.TitleFixedText, name="Your address", value=base.get_local_addr())
        # npyscreen.notify_confirm(message="yo")

    def afterEditing(self):
        self.parentApp.mainform.name.value = self.greeting.value
        self.parentApp.setNextForm('MAIN')


class Application(npyscreen.NPSAppManaged):
    def __init__(self, caller_instance, server_thread, playback_thread, record_thread):
        # Somehow npyscreen __init__() method is not allowing us to create our fields AFTER
        # call of __init__(), so we are doing it right here
        self.caller_instance = caller_instance
        self.server_thread = server_thread
        self.playback_thread = playback_thread
        self.record_thread = record_thread
        self.mainform = None
        super(Application, self).__init__()

    def onStart(self):
        self.addForm('MAIN', MainForm, name="Main form", call_func=self.caller_instance.call)
        self.addForm('username_form', IntroduceYourself, name="Choose username")
        self.mainform = self.getForm('MAIN')  # Dont know how to bind it other way


# def my_function(*args):
#     F = Asdf(name='New employee')
#     F.edit()
#     return 'Recotd for: ' + F.name.value


def initialize(**components):
    Application(**components).run()