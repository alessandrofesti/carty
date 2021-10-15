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
import threading
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
from kivymd.uix.spinner.spinner import MDSpinner
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

from kivy.clock import mainthread
from data import input_data
from kivy.uix.textinput import TextInput
from kivymd.uix.banner.banner import MDBanner
# festi.alessandro00@gmail.com


# TODO:
#   add password button
#   unjoin user from group
#   ottimizzare chiamate DB, farne solo una iniziale (forse): lentezza sono tutte le chiamate al DB

import json
import pdb

if not firebase_admin._apps:
    cred = credentials.Certificate("./carty-7373e-firebase-adminsdk-vuzij-94930417b9.json")
    # firebase_admin.delete_app(firebase_admin.get_app())
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://carty-7373e-default-rtdb.europe-west1.firebasedatabase.app/'
    })

# with open("./db_schema.json", "r") as f:
#     db_schema = json.load(f)

ref = db.reference('/')
# ref.set(db_schema)

# debugger carino https://kivy.org/doc/stable/api-kivy.modules.webdebugger.html

# for i in self.ids.screen_manager.get_screen('www').children:
#     for j in i.children:
#         print(j)
#         try:
#             print(j.row_data)
#         except:
#             print('no data table')

import time

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
        self.manager.current = 'login'


class MainScreen(Screen):
    def on_pre_enter(self):
        # TODO: including spinner
        #self.on_pre_enter_funcs()
        # x = threading.Thread(target=self.on_pre_enter_funcs, daemon=True).start()
        # y = threading.Thread(target=self.get_main_spinner, daemon=True)
        # y.start()

        # Customize toolbar
        self.user = self.get_user()
        self.app = Test.get_running_app()
        self.ref = self.app.ref
        self.ids.toolbar.title = self.user.display_name
        self.ids.toolbar.ids.label_title.font_size = 20
        self.user_groups = self.get_user_groups()

        # DYNAMIC CONSTRUCTION
        for group in self.user_groups:
            self.group_screen = group
            self.add_dynamic_screen()
            self.add_groups_in_scrollview()
            self.create_user_data_layout()
            self.create_group_data_to_layout()
            self.create_run_data_buttons()

        # USAGE
        self.mycallback_scroll()

    # USAGE
    def usage_main(self, child):
        self.group_screen = child.text
        self.layout = self.ids.screen_manager.get_screen(f'{self.group_screen}').children[0]
        self.layout_user = self.ids.screen_manager.get_screen(f'Add user -- {self.group_screen}').children[0]
        print(f'current group_screen in {self.group_screen}')

    def change_screen_scrollview(self, child):
        self.usage_main(child=child)
        self.ids.screen_manager.current = child.text
        self.ids.nav_drawer.set_state("close")

    def mycallback_scroll(self, *args):
        for child in self.ids.contentnavigationdrawer.ids.container.children:
            if child.text in self.user_groups:
                child.bind(on_press=self.change_screen_scrollview)

    # DYNAMIC CONSTRUCTION
    def update_data_table(self, *args):
        self.table = self.get_data_table()
        self.layout.clear_widgets()
        self.layout.add_widget(self.table)
        self.create_run_data_buttons()

    def add_dynamic_screen(self):
        group_screen = Screen(name=f"{self.group_screen}")
        self.ids.screen_manager.add_widget(group_screen)
        self.ids.screen_manager.ids[f"{self.group_screen}"] = weakref.ref(group_screen)

    def add_user_data_screen(self):
        self.ids.screen_manager.add_widget(
            Screen(name=f'Add user -- {self.group_screen}'))

    def add_groups_in_scrollview(self):
        onelistitem = OneLineListItem(text=f"{self.group_screen}")
        self.ids.contentnavigationdrawer.ids.container.add_widget(onelistitem)

    def create_user_data_layout(self):
        self.add_user_data_screen()
        self.layout_user = MDFloatLayout(
            size=(self.width,
                  self.height)
        )
        self.ids.screen_manager.get_screen(f'Add user -- {self.group_screen}').add_widget(self.layout_user)
        dice_icon = MDIconButton(
            icon="dice-multiple",
            user_font_size=40,
            theme_text_color="Custom",
            # text_color=app.theme_cls.primary_color
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

    def create_group_data_to_layout(self):
        self.layout = BoxLayout(orientation='vertical',
                                spacing="12dp",
                                padding="12dp")
        self.ids.screen_manager.get_screen(f'{self.group_screen}').add_widget(self.layout)

        # Add password label
        pass_path = self.ref.child('groups').child(f"{self.group_screen}").child("admin").get()
        self.group_pass_join = pass_path['password']
        self.pass_label = OneLineListItem(text=f"Group password is {self.group_pass_join} -- share it with your friends to let them join the group")
        self.layout.add_widget(self.pass_label)

        # Add data table
        self.table = self.get_data_table()
        self.layout.add_widget(self.table)

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
        # Add Run button
        self.layout.add_widget(
            MDFillRoundFlatButton(
                text="Leave group",
                line_color=(1, 0, 1, 1),
                pos_hint={'center_x': .5, 'center_y': .5},
                on_press=lambda x: self.leave_group()
            )
        )

    def join_existing_group(self):
        self.join_group_name = self.ids.join_group_name.text
        self.join_group_password = self.ids.join_group_password.text
        join_path = self.ref.child('groups').get()

        if self.join_group_name in join_path.keys():
            if self.user.uid in join_path[self.join_group_name]['group users'].keys():
                self.dialog_button(text_button='Retry',
                                   dialog_title=f'join not succeed',
                                   dialog_text='user already joined the group')
            elif self.join_group_password != str(join_path[self.join_group_name]['admin']['password']):
                self.dialog_button(text_button='Retry',
                                   dialog_title=f'join not succeed',
                                   dialog_text='wrong password')
            else:
                self.dialog_button(text_button='OK',
                                   dialog_title=f'join succeed',
                                   dialog_text=f'Joined group {self.join_group_name}')

                self.ref.child('groups').child(f"{self.join_group_name}").child('group users').update(
                    {f"{self.user.uid}": True}
                )
                self.remove_screens()
                self.on_pre_enter()
        else:
            self.dialog_button(text_button='Retry',
                               dialog_title=f'join not succeed',
                               dialog_text=f'{self.join_group_name} does not exists')

    def leave_group(self):
        self.ref.child('groups').child(self.group_screen).child('group users').child(f'{self.user.uid}').delete()
        if self.user.uid in self.ref.child('groups').child(self.group_screen).child('users data').get().keys():
            self.ref.child('groups').child(self.group_screen).child('users data').child(f'{self.user.uid}').delete()

        self.remove_screens()
        self.on_pre_enter()
        self.dialog_button(text_button='OK',
                           dialog_title='Succeed',
                           dialog_text='Group deleted')

    def create_new_group(self):
        self.group_name = self.ids.group_name.text
        self.group_password = self.ids.group_password.text
        self.group_destination_address = self.ids.group_destination_address.text
        self.user_departure_address = self.ids.user_departure_address.text
        self.user_n_avaliable_places = self.ids.user_n_avaliable_places.text

        data_to_set = {
            f"{self.group_name}": {
                "admin": {
                    "admin uid": self.user.uid,
                    "password": self.group_password,
                    "destination address": self.group_destination_address
                },
                "group users": {
                    f"{self.user.uid}": True
                },
                "users data": {
                    f"{self.user.uid}": {
                        "address": self.user_departure_address,
                        "avaliable places": self.user_n_avaliable_places #TODO: check toint
                    }
                }
            }
        }

        if not self.group_name in self.ref.child('groups').get().keys():
            self.ref.child('groups').update(data_to_set)
            self.remove_screens()
            self.on_pre_enter()
            self.dialog_button(text_button='OK',
                               dialog_title='Group created',
                               dialog_text='Share the group password with your friends to let them join the group')

        else:
            self.dialog_button(text_button='Retry',
                               dialog_title='Group name already exists',
                               dialog_text='A group with the same name already exists, choose another name')

    def remove_screens(self):
        keep_groups = ['scr add group', 'screen profile', 'screen join group']
        keep_scroll_items = ['Profile', 'Join existing group']
        for screen in self.ids.screen_manager.screen_names:
            if screen not in keep_groups:
                self.ids.screen_manager.remove_widget(self.ids.screen_manager.get_screen(screen))
                # TODO: da togliere gli schermi add user
                #self.ids.screen_manager.remove_widget(self.ids.screen_manager.get_screen(f'Add user -- {screen}'))
        for i, scroll_element in enumerate(self.ids.contentnavigationdrawer.ids.container.children):
            if scroll_element.text not in keep_scroll_items:
                self.ids.contentnavigationdrawer.ids.container.remove_widget(
                    self.ids.contentnavigationdrawer.ids.container.children[i]
                )
        self.ids.nav_drawer.set_state("close")


    def get_user_groups(self):
        groups = []
        group_path = self.ref.child('groups').get().keys()
        for group in group_path:
            try:
                if self.user.uid in self.ref.child('groups').child(f"{group}").child("group users").get().keys():
                    groups.append(group)
            except:
                print('User not present in this group')
        return groups

    def get_update_user_data(self, *args):
        self.avaliable_places_button = self.layout_user.children[2].text
        self.address_button = self.layout_user.children[1].text

        data_to_set = {
                "address": self.address_button,
                "avaliable places": self.avaliable_places_button
            }

        self.ref.child('groups').child(f'{self.group_screen}').child('users data').child(f"{self.user.uid}").set(data_to_set)
        self.update_data_table()
        self.change_screen(self.group_screen)

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
        group_path = self.ref.child('groups').child(f'{self.group_screen}').child('users data').get()
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



class LoginScreen(Screen):
    pass


class SignupScreen(Screen):
    pass


class InputScreen(Screen):
    pass


class ForgotPasswordScreen(Screen):
    pass


class LoadingScreen(Screen):
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
    sm.add_widget(LoadingScreen(name='loading'))


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
        self.app = Test.get_running_app()
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
        self.resetEmail = self.strng.get_screen('resetpassword').ids.reset_email.text
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
            #self.strng.get_screen('main').manager.current = 'main'
            self.root.current = 'main'

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