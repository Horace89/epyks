
import os
import npyscreen
from networking import base

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

    def create(self):
        super(MainForm, self).create()
        self.name = self.add(npyscreen.TitleText, name="username", value="username")
        self.call_to = self.add(npyscreen.TitleText, name="call to", value="192.168.0.102:8889")
        self.call_button = self.add(npyscreen.Button, name="call", when_pressed_function="a")
        self.parentApp.setNextForm('username_form')

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
    def __init__(self, server_instance, server_thread, playback_thread, record_thread):
        super(Application, self).__init__()
        self.server = server_instance
        self.server_thread = server_thread
        self.playback_thread = playback_thread
        self.record_thread = record_thread
        self.mainform = None

    def onStart(self):
        self.addForm('MAIN', MainForm, name="Main form")
        self.addForm('username_form', IntroduceYourself, name="Choose username")
        self.mainform = self.getForm('MAIN')  # Dont know how to bind it other way


# def my_function(*args):
#     F = Asdf(name='New employee')
#     F.edit()
#     return 'Recotd for: ' + F.name.value


def initialize(**components):
    Application(**components).run()