import os

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder



def load_kv(file):
    return Builder.load_file(os.path.join(file))
