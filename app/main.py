import os

from kivy.lang import Builder

from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty
from validate_email import validate_email
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from kivy.app import App
from kivymd.uix.textfield import MDTextField
import weakref
from kivymd.uix.button import MDRectangleFlatIconButton, MDRectangleFlatButton, MDRaisedButton, MDIconButton

from kivymd.uix.label import MDLabel

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty

from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.lang import Builder

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp

from kivy.uix.screenmanager import ScreenManager, Screen

import requests
import yaml
import json
from kivymd.uix.list import OneLineListItem
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog

# buildozer -v android clean

from functions import load_kv

# callbacks
# access widgets by ids
# authentication using fb, google and others
# screenmanager
# SDK firebase admin: https://console.firebase.google.com/u/0/project/carty-7373e/settings/serviceaccounts/adminsdk?hl=it
# password dimenticata e altri tool: https://stackoverflow.com/questions/54995334/firebase-admin-python-sending-password-reset-email
# adb devices -l per vedere i dispositivi connessi al pc

# debug buildozer
# adb devices
# adb install -r bin/*.apk
# echo 'Please connect on transfer files mode the cellphone'
# adb logcat -s "python"
# buildozer -v android clean
# buildozer android debug

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, auth
from kivy.metrics import dp
import pandas as pd

from data import input_data
from kivy.uix.textinput import TextInput

# festi.alessandro00@gmail.com


import json

if not firebase_admin._apps:
    cred = credentials.Certificate("./carty-7373e-firebase-adminsdk-vuzij-94930417b9.json")
    # firebase_admin.delete_app(firebase_admin.get_app())
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://carty-7373e-default-rtdb.europe-west1.firebasedatabase.app/'
    })

with open("./db_schema.json", "r") as f:
    db_schema = json.load(f)

ref = db.reference('/')
ref.set(db_schema)

left_arrow = "./icons/left-arrow.png"

def load_yaml(file_yaml: str):
    with open(file_yaml, "r") as yamlfile:
        data = yaml.safe_load(yamlfile)[0]
    return data


class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class HelloScreen(Screen):
    def on_enter(self, *args):
        print("on Enter")
        Clock.schedule_once(self.callbackfun, 3)

    def callbackfun(self, dt):
        print("Change Screen")
        print(self.manager.current)
        print(self.manager.next())
        self.manager.current = 'login'

class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.ref = ref

    def on_pre_enter(self):
        # Customize toolbar
        self.user = self.get_user()
        self.ids.toolbar.title = self.user.display_name
        self.ids.toolbar.ids.label_title.font_size = 20
        self.user_groups = self.get_user_groups()

        for group in self.user_groups:
            self.group_screen = group
            # Add dynamic group screens
            self.ids.screen_manager.add_widget(
                Screen(name=f'{self.group_screen}'))
            # Add groups list in scrollview
            self.ids.contentnavigationdrawer.ids.container.add_widget(
                OneLineListItem(text=f"{self.group_screen}",
                                on_press=lambda x: self.change_screen(f'{self.group_screen}')
                                )
            )
            # Add layout
            self.layout = BoxLayout(orientation='vertical',
                                    spacing="12dp",
                                    padding="12dp")
            self.ids.screen_manager.get_screen(f'{self.group_screen}').add_widget(self.layout)
            # Add dataframe
            table = self.get_data_table()
            self.layout.add_widget(table)
            self.create_run_data_buttons()
            self.ids.screen_manager.add_widget(
                Screen(name=f'Add user -- {self.group_screen}')
            )
            self.layout_user = MDFloatLayout(
                size=(self.width, self.height))
            self.ids.screen_manager.get_screen(f'Add user -- {self.group_screen}').add_widget(self.layout_user)
            dice_icon = MDIconButton(
                icon="dice-multiple",
                user_font_size=40,
                theme_text_color="Custom",
                #text_color=app.theme_cls.primary_color
                pos_hint={'top': 0.9, 'center_x': 0.5}
            )
            self.layout_user.add_widget(dice_icon)
            self.ids['dice_icon'] = weakref.ref(dice_icon)
            avaliable_places = MDTextField(
                halign="center",
                size_hint_x=0.6,
                size_hint_y=0.1,
                hint_text="Number of free places avaliable (0 if none)",
                pos_hint={'top': 0.75, 'center_x': 0.5},
                mode="line"
                )
            self.layout_user.add_widget(avaliable_places)
            self.ids['avaliable_places'] = weakref.ref(avaliable_places)
            address_data = MDTextField(
                halign="center",
                size_hint_x=0.6,
                size_hint_y=0.1,
                hint_text="Your address of departure",
                pos_hint={'top': 0.65, 'center_x': 0.5},
                mode="line"
            )
            self.layout_user.add_widget(address_data)
            self.ids['address_button'] = weakref.ref(address_data)
            add_data_button = MDFillRoundFlatButton(
                    text="OK",
                    size_hint_x=5,
                    size_hint_y=5,
                    size=(0.7, 0.05),
                    pos_hint={'top': 0.5, 'center_x': 0.5},
                    on_release=self.get_update_user_data
                )
            self.layout_user.add_widget(add_data_button)
            self.ids['add_data_button'] = weakref.ref(add_data_button)

    def create_run_data_buttons(self, *args):
        self.layout.add_widget(
            MDFillRoundFlatButton(
                text="Add your data",
                size=(0.7, 0.05),
                line_color=(1, 0, 1, 1),
                pos_hint={'center_x': .5, 'center_y': .5},
                on_press=lambda x: self.change_screen(f'Add user -- {self.group_screen}')
            )
        )
        # Add Run button
        self.layout.add_widget(
            MDFillRoundFlatButton(
                text="Run simulation",
                line_color=(1, 0, 1, 1),
                pos_hint={'center_x': .5, 'center_y': .5}
            )
        )

    def update_data_table(self, *args):
        table = self.get_data_table()
        self.layout.clear_widgets()
        self.layout.add_widget(table)
        self.create_run_data_buttons()

    def get_user_groups(self):
        groups = []
        group_path = self.ref.child('groups').get().keys()
        for group in group_path:
            if self.user.uid in self.ref.child('groups').child(f"{group}").child("group_users").get().keys():
                groups.append(group)
        return groups

    def get_update_user_data(self, group, *args):
        self.address_button = self.ids.address_button.text
        self.avaliable_places_button = self.ids.avaliable_places.text

        data_to_set = {
            f"{self.user.uid}": {
                "address": self.address_button,
                "avaliable places": self.avaliable_places_button
            }
        }

        self.ref.child('groups').child(f'{self.group_screen}').child('users_data').update(data_to_set)
        self.update_data_table()
        self.change_screen(self.group_screen)

    def get_box_layout(self):
        bl = BoxLayout(orientation='vertical',
                       spacing="12dp",
                       padding="12dp",
                       size_hint=(1, None),
                       pos_hint={'top': 1})
        return bl

    def get_user(self):
        return auth.get_user_by_email(self.parent.get_screen('login').ids.login_email.text)

    def get_main_screen(self, scrren_name: str):
        self.parent.current = scrren_name
        self.ids.nav_drawer.set_state("close")

    def change_screen(self, scrren_name: str):
        self.ids.screen_manager.current = scrren_name
        self.ids.nav_drawer.set_state("close")

    def add_user_button(self):
        pass

    def get_group_data(self):
        group_path = self.ref.child('groups').child(f'{self.group_screen}').child('users_data').get()
        df_list = []
        for uid in group_path.keys():
            user = auth.get_user(uid)
            username = user.display_name
            dict_grpup = group_path[uid]
            dict_grpup.update({
                "user": username
            })
            df = pd.DataFrame.from_dict(dict_grpup, orient='index')
            df_list.append(df)

        df_group = pd.concat(df_list, axis=1).T.reset_index(drop=True)
        df_group = df_group[['user', "address", "avaliable places"]]
        return df_group

    def get_data_table(self):
        df_group = self.get_group_data()
        column_data = list(df_group.columns)
        column_data = [(x, dp(60)) for x in column_data]
        row_data = df_group.to_records(index=False)
        table = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            #check=True,
            use_pagination=True,
            rows_num=len(df_group)+3
        )
        return table

    def dialog_button(self):
        self.dialog = MDDialog(
            text="Discard draft?",
            buttons=[
                MDFlatButton(text="CANCEL"), MDRaisedButton(text="DISCARD"),
            ],
        )
        return self.dialog.open()

    def close_username_dialog(self, *args):
        self.dialog.dismiss()



class LoginScreen(Screen):
    pass


class SignupScreen(Screen):
    pass


class InputScreen(Screen):
    pass


class ForgotPasswordScreen(Screen):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        """Called when tap on a menu item."""

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color
        # print(f"inst:{instance_item.text_color}", f"thm_txt{self.theme_cls.text_color}",
        #       f"thm_prm{self.theme_cls.primary_color}")



def add_ScreenManager():
    sm = ScreenManager()
    sm.add_widget(HelloScreen(name='hello'))
    sm.add_widget(MainScreen(name='main'))
    sm.add_widget(LoginScreen(name='login'))
    sm.add_widget(SignupScreen(name='signup'))
    sm.add_widget(InputScreen(name='input'))
    sm.add_widget(ForgotPasswordScreen(name='resetpassword'))


class Test(MDApp):
    def __init__(self, *args, **kwargs):
        self.title = "My carty Application"
        self.ref = ref
        self.access_db = access_db
        self.web_apk = web_apk
        self.requests_signup = requests_signup
        self.requests_signin = requests_signin
        self.requests_verify_email = requests_verify_email
        self.requests_reset_email = requests_reset_email
        self.requests_delete_account = requests_delete_account
        super().__init__(**kwargs)

    def build(self):
        self.strng = load_kv('main.kv')
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.primary_hue = "300"
        self.theme_cls.accent_palette = "Purple"
        return self.strng

    def VerifyEmail(self):
        payload = json.dumps({
            "requestType": "VERIFY_EMAIL",
            "idToken": self.idToken
        })
        r = requests.post(self.requests_verify_email.format(self.web_apk),
                          params={"key": self.web_apk},
                          data=payload)
        if 'error' in r.json().keys():
            return {'status': 'error', 'message': r.json()['error']['message']}
        else:
            return r.json()

    def DeleteAccount(self):
        payload = json.dumps({
            "idToken": self.idToken
        })
        r = requests.post(self.requests_delete_account.format(self.web_apk),
                          params={"key": self.web_apk},
                          data=payload)
        if 'error' in r.json().keys():
            return {'status': 'error', 'message': r.json()['error']['message']}
        else:
            self.dialog_button(text_button='OK',
                               dialog_title='Account deleted',
                               dialog_text=f'Adieu')
            self.dialog.open()
            return r.json()

    def SendResetEmail(self):
        self.resetEmail = self.strng.get_screen('resetpassword').ids.reset.text
        payload = json.dumps({
            "requestType": "PASSWORD_RESET",
            "email": self.resetEmail
        })
        r = requests.post(self.requests_reset_email.format(self.web_apk),
                          params={"key": self.web_apk},
                          data=payload)
        if 'error' in r.json().keys():
            return {'status': 'error', 'message': r.json()['error']['message']}
        else:
            self.dialog_button(text_button='OK',
                               dialog_title='Reset email',
                               dialog_text=f'Email sent to {self.resetEmail}')
            #self.dialog.open()
            return r.json()

    add_ScreenManager()

    def signup(self):
        self.signupEmail = self.strng.get_screen('signup').ids.signup_email.text
        self.signupUsername = self.strng.get_screen('signup').ids.signup_username.text
        self.signupPassword = self.strng.get_screen('signup').ids.signup_password.text

        if (len(self.signupEmail.split()) == 0
                or len(self.signupPassword.split()) == 0
                or len(self.signupUsername.split()) == 0):
            self.dialog_button(text_button='Retry',
                               dialog_title='Invalid input',
                               dialog_text='Please Enter a valid Input')

        elif len(self.signupUsername.split()) > 1:
            self.dialog_button(text_button='Retry',
                               dialog_title='Invalid Username',
                               dialog_text='Please enter username without space')

        else:
            print(self.signupEmail, self.signupUsername, self.signupPassword)
            details = {
                'email': self.signupEmail,
                'password': self.signupPassword,
                'display_name': self.signupUsername,
                'returnSecureToken': True
            }
            r = requests.post(self.requests_signup.format(self.web_apk),
                              data=details)

            if 'error' in r.json().keys():
                self.dialog_button(text_button='Retry',
                                   dialog_title='Error',
                                   dialog_text=f'{r.json()["error"]["message"]}')

            if 'idToken' in r.json().keys():
                self.idToken = r.json()['idToken']
                self.VerifyEmail()
                self.dialog_button(text_button='OK',
                                   dialog_title='Weeeee',
                                   dialog_text=f'We sent you a verification email')
                self.strng.get_screen('login').manager.current = 'login'

    def login(self):
        self.loginEmail = self.strng.get_screen('login').ids.login_email.text
        self.loginPassword = self.strng.get_screen('login').ids.login_password.text
        self.login_check = False

        try:
            self.user = auth.get_user_by_email(self.loginEmail)
        except:
            self.dialog_button(text_button='Retry',
                               dialog_title='Error',
                               dialog_text='email not recognized')

        details = {
            'email': self.loginEmail,
            'password': self.loginPassword,
            'returnSecureToken': True
        }

        r = requests.post(self.requests_signin.format(self.web_apk),
                          data=details)

        if 'error' in r.json().keys():
            self.dialog_button(text_button='Retry',
                               dialog_title='Error',
                               dialog_text=f'{r.json()["error"]["message"]}')

        elif 'idToken' in r.json().keys() and not self.user.email_verified:
            self.dialog_button(text_button='Retry',
                               dialog_title='Error',
                               dialog_text='Your email has not been verified')

        elif 'idToken' in r.json().keys() and self.user.email_verified:
            self.login_check = True
            self.idToken = r.json()['idToken']
            self.strng.get_screen('main').manager.current = 'main'

        else:
            self.dialog_button(text_button='Retry',
                               dialog_title='Error',
                               dialog_text='Unknown error')

    def dialog_button(self,
                      text_button: str,
                      dialog_title: str,
                      dialog_text: str):

        cancel_btn_username_dialogue_mail = MDFlatButton(text=text_button,
                                                         on_release=self.close_username_dialog)
        self.dialog = MDDialog(title=dialog_title,
                               text=dialog_text,
                               size_hint=(0.7, 0.2),
                               buttons=[cancel_btn_username_dialogue_mail])
        self.dialog.open()

    def close_username_dialog(self, *args):
        self.dialog.dismiss()



if __name__ == '__main__':
    # load data
    data = load_yaml('config.yaml')
    access_db = data['General']['access_db']
    web_apk = data['General']['web_apk']
    requests_signup = data['General']['requests_signup']
    requests_signin = data['General']['requests_signin']
    requests_verify_email = data['General']['requests_verify_email']
    requests_reset_email = data['General']['requests_reset_email']
    requests_delete_account = data['General']['requests_delete_account']

    Test().run()