from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from functools import partial


class testclass:
    def someth(*args, txt):
        print(txt)


class BeginScreen(Screen):
    def __init__(self, **kwargs):
        super(BeginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=5)
        self.layout.add_widget(Label(text=str('Hello')))

        # layout.add_widget(TextInput(id='test', text=''))  # id in python+kivy is deprecated
        txtInput = TextInput(text='text input')
        self.layout.add_widget(txtInput)
        self.ids['test'] = txtInput

        self.layout.add_widget(Button(text='Button!', on_press=partial(testclass.someth, txt=self.ids.test.text)))
        self.add_widget(self.layout)

        print("self.ids={}".format(self.ids))
        print("self.ids['test']={}".format(self.ids['test']))
        print("self.ids['test'].text={}".format(self.ids['test'].text))
        print("self.ids.test.text={}".format(self.ids.test.text))
        for key, val in self.ids.items():
            print("key={0}, val={1}".format(key, val))


class TestApp(App):
    from kivy.config import Config
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '400')

    def build(self):
        sm = ScreenManager()
        sm.add_widget(BeginScreen(name='test'))
        return sm

TestApp().run()