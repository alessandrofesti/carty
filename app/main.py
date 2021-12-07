from kivy.clock import Clock

from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton

from kivy.properties import ObjectProperty
from kivymd.uix.textfield import MDTextField
import weakref
from kivymd.uix.button import MDIconButton

from kivy.properties import StringProperty, ListProperty

from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.button.button import MDRectangleFlatIconButton

from kivy.uix.screenmanager import ScreenManager, Screen

import requests
import yaml
import json
from kivymd.uix.list import OneLineListItem
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar.progressbar import MDProgressBar

# buildozer -v android clean

from kivy.clock import mainthread
import threading

from functions import load_kv
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.banner.banner import MDBanner

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

# Get total memory used
# import os, psutil
# process = psutil.Process(os.getpid())
# print(process.memory_info().rss)  # in bytes

# Ortools debugging: gdb -ex r --args python main.py

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, auth
from kivy.metrics import dp
import pandas as pd
from multiprocessing import Process

# TODO:
#   Forgot password? check che utente sia reinserito in tutti i gruppi
#   Cambia tutte le f strings con doppio apice in caso di inserimento stringa con l'apostrofo
#   aggiungi possibilità di modificare indirizzo di destinazione
#   pulsante run_siulation nell'app che non funziona una seconda volta senza logout
#   se run attiva impossibile iniziarne una nuova

from kivy.uix.gridlayout import GridLayout
import json
import pdb

import model
from model import get_distance_matrix, main

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
        # self.on_pre_enter_funcs()
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
        # self.dialog_button = Test.dialog_button
        self.cloclose_username_dialog = Test.close_username_dialog
        self.dialog = None

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
        self.add_logout_in_scrollview()
        self.add_delete_account_in_scrollview()

    # USAGE
    def usage_main(self, child):
        self.group_screen = child.text
        self.table = self.get_data_table()
        self.general_layout = self.ids.screen_manager.get_screen(f'{self.group_screen}').children[0]
        self.layout_user = self.ids.screen_manager.get_screen(f'Add user -- {self.group_screen}').children[0]
        print(f'current group_screen is {self.group_screen}')

    def change_screen_scrollview(self, child):
        self.usage_main(child=child)
        self.ids.screen_manager.current = child.text
        self.ids.nav_drawer.set_state("close")

    def mycallback_scroll(self, *args):
        for child in self.ids.contentnavigationdrawer.ids.container.children:
            if child.text in self.user_groups:
                child.bind(on_press=self.change_screen_scrollview)

    def add_logout_in_scrollview(self):
        self.ids.contentnavigationdrawer.ids.container.add_widget(
            OneLineListItem(text="Logout",
                            on_press=self.get_login_screen)
        )

    def get_login_screen(self, *args):
        self.remove_screens()
        self.manager.current = 'login'

    def add_delete_account_in_scrollview(self):
        self.ids.contentnavigationdrawer.ids.container.add_widget(
            OneLineListItem(text="Delete Account",
                            on_press=self.delete_account_remove_data)
        )

    def delete_account_remove_data(self, *args):
        self.dialog_button(two_alternatives=True,
                           text_button='GO BACK',
                           text_button2="YES, I'M SURE",
                           dialog_title='Are you sure?',
                           dialog_text='If you delete your account you will loose all your data',
                           action_button2='self.delete_account_and_data')

    def delete_account_and_data(self, *args):
        self.cancel_user_data_from_group_in_db(group_list=self.user_groups)
        self.remove_screens()
        self.dialog_button(two_alternatives=False,
                           text_button='OK',
                           text_button2="",
                           dialog_title='Profile deleted',
                           dialog_text="So sad you're leaving :( ",
                           action_button2='')
        self.app.DeleteAccount()

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
        city_address_data = MDTextField(
            halign="center",
            size_hint_x=0.6,
            size_hint_y=0.1,
            hint_text="Your city of departure",
            pos_hint={'top': 0.65, 'center_x': 0.5},
            mode="line"
        )
        self.layout_user.add_widget(city_address_data)
        self.ids['address_button'] = weakref.ref(city_address_data)
        address_data = MDTextField(
            halign="center",
            size_hint_x=0.6,
            size_hint_y=0.1,
            hint_text="Your address of departure",
            pos_hint={'top': 0.55, 'center_x': 0.5},
            mode="line"
        )
        self.layout_user.add_widget(address_data)
        self.ids['address_button'] = weakref.ref(address_data)
        add_data_button = MDFillRoundFlatButton(
            text="OK",
            size_hint_x=5,
            size_hint_y=5,
            size=(0.7, 0.05),
            pos_hint={'top': 0.4, 'center_x': 0.5},
            on_release=self.get_update_user_data
        )
        self.layout_user.add_widget(add_data_button)
        self.ids['add_data_button'] = weakref.ref(add_data_button)

    def create_group_data_to_layout(self):
        self.layout = MDFloatLayout(
            size=(self.width,
                  self.height)
        )
        self.ids.screen_manager.get_screen(f'{self.group_screen}').add_widget(self.layout)
        # Add listitems data
        self.create_info_onelinelistitems()

        # Add data table
        self.table = self.get_data_table()
        # self.table.bind(on_check_press=self.on_check_press)
        self.layout.add_widget(self.table)

    def get_info_group(self):
        self.pass_path = self.ref.child('groups').child(f"{self.group_screen}").child("admin").get()
        self.group_pass_join = self.pass_path['password']
        self.destination_address = self.pass_path['destination address']
        self.destination_city = self.pass_path['destination city']

    def create_info_onelinelistitems(self):
        self.get_info_group()
        # Add password and destination labels
        self.pass_label = OneLineListItem(text=f"Group password: [b]{self.group_pass_join}[/b]",
                                          pos_hint={'top': 1, 'center_x': 0.5})
        self.dest_label = OneLineListItem(
            text=f"Group destination: [b]{self.destination_address} ({self.destination_city})[/b]",
            pos_hint={'top': 0.9, 'center_x': 0.5})

        # Add button to modify group destination
        self.changedestinationbutton = MDIconButton(
            icon="account-edit",
            pos_hint={'top': 0.9, 'center_x': 0.95},
            on_press=self.go_to_modify_screen
        )
        self.layout.add_widget(self.pass_label, index=0)
        self.layout.add_widget(self.dest_label, index=0)
        self.layout.add_widget(self.changedestinationbutton, index=0)

    def go_to_modify_screen(self, *args):
        self.ids.screen_manager.current = 'screen modify group destination'

    def modify_group_destination(self, *args):
        self.new_group_destination_address = self.ids.screen_manager.get_screen('screen modify group destination').children[0].children[2].text
        self.new_group_destination_city = self.ids.screen_manager.get_screen('screen modify group destination').children[0].children[1].text
        self.ref.child('groups').child(f'{self.group_screen}').child('admin').child("destination address").set(self.new_group_destination_address)
        self.ref.child('groups').child(f'{self.group_screen}').child('admin').child("destination city").set(self.new_group_destination_city)
        self.ids.screen_manager.get_screen(self.group_screen).children[-1].children[5].text = f'Group destination: [b]{self.new_group_destination_address} ({self.new_group_destination_city})[/b]'
        self.ids.screen_manager.current = f'{self.group_screen}'

    def create_run_data_buttons(self, *args):
        self.layout.add_widget(
            MDFillRoundFlatButton(
                text="Add your data",
                line_color=(1, 0, 1, 1),
                pos_hint={'top': 0.1, 'center_x': 0.3},
                on_press=lambda x: self.change_screen(f'Add user -- {self.group_screen}')
            )
        )
        # Add Run button
        self.layout.add_widget(
            MDFillRoundFlatButton(
                text="Run simulation",
                line_color=(1, 0, 1, 1),
                pos_hint={'top': 0.1, 'center_x': 0.5},
                on_release=self.run_simulation
            )
        )
        # Add Run button
        self.layout.add_widget(
            MDFillRoundFlatButton(
                text="Leave group",
                line_color=(1, 0, 1, 1),
                pos_hint={'top': 0.1, 'center_x': 0.7},
                on_press=self.leave_group
            )
        )

    def datatable_to_df(self):
        df_cols = [i[0] for i in self.table.column_data]
        if len(self.table.row_data) > 0:
            df_tot = pd.DataFrame(self.table_run, columns=df_cols)
        else:
            df_tot = pd.DataFrame(columns=df_cols)

        return df_tot

    def create_banner(self):
        '''
        This function creates the banner visible if the model doesn't find a solution or if there are problems with the input data
        '''
        self.banner_no_solution = MDBanner(
            text=["[b]ALERT: Problem not solvable[/b]",
                  "  - select all the people you want to include",
                  "  - check if there are enough places for those who need them"],
            type="three-line",
            icon="account-alert",
            vertical_pad=self.ids.toolbar.height,
            over_widget=self.ids.screen_manager.get_screen(f"{self.group_screen}").children[-1].children[-1],
            closing_time=0.15
            )
        self.ids.screen_manager.get_screen(f"{self.group_screen}").add_widget(self.banner_no_solution)

    def create_run_spinner(self):
        '''
        This function creates the spinner visible while the model is running
        '''
        self.loading_spinner=MDSpinner(
              size_hint=[None, None],
              size=[dp(48), dp(48)],
              pos_hint={'center_x': .5, 'center_y': .5},
              active=False)
        self.ids.screen_manager.get_screen(f"{self.group_screen}").add_widget(self.loading_spinner)

    @mainthread
    def callback_spinner_run(self, *args):
        '''
        The spinner works only if the thread1, which is the run pipeline of the model, works as well
        '''
        print(f'thread is alive: {self.thread1.is_alive()}')
        if self.thread1.is_alive() == True:
            print(f'--- Spinner is active: {self.ids.screen_manager.get_screen(f"{self.group_screen}").children[0].active} ---')
            self.ids.screen_manager.get_screen(f"{self.group_screen}").children[0].active = True
        else:
            self.ids.screen_manager.get_screen(f"{self.group_screen}").children[0].active = False

    def callback_model_run(self, *args):
        '''
        This callback function runs the pipeline_output if the thread of the running pipeline has finished.
        Finishing the model thread brings the output pipeline on the main thread so that the graphic can be shown (not feasable outside the main thread)
        '''
        print(f'--- Model thread is alive: {self.thread1.is_alive()} ---')
        print(f'--- Callback already called: {self.model_called } ---')
        if self.thread1.is_alive() == False and self.model_called == False:
            self.pipeline_output_model()
            self.model_called = True

    def run_simulation(self, *args):
        '''
        the simulation is composed of:
        - creating banner to show if simulation has problems
        - creating a new thread to show the loading spinner while the model is running using a clock scheduled to run every second
        - Another clock checks if the run has finished so the output part (not feasable aoutside the main thread) can be done
        - the self.model_called = False prevents the clock from running repeatetly the model
        '''
        self.create_banner()
        self.create_run_spinner()

        self.thread1 = threading.Thread(target=(self.pipeline_run_model),
                                        name="run_thread")
        self.thread1.start()
        self.event_spinnder_run = Clock.schedule_interval(self.callback_spinner_run, timeout=1.0)
        self.event_spinnder_run()

        # To not call the model multiple times using the clock
        self.model_called = False
        self.event_model_run = Clock.schedule_interval(self.callback_model_run, timeout=1.0)
        self.event_model_run()

    def drop_clock_events(self, *args):
        '''
        drop clock events once the run has finished
        '''
        self.event_spinnder_run.cancel()
        self.event_model_run.cancel()

    def pipeline_run_model(self, *args):
        '''
        The pipeline_run creates the table from the input data and runs the model calling the AWS lambda function
        '''
        self.get_run_datatable()

        # Run model
        if self.input_data != {}:
            self.run_model()

    def pipeline_output_model(self, *args):
        '''
        the pipeline_output gets the results from the model, creates the output table and print it on a new output scren
        '''
        if self.shifts == {}:
            print('problem not solved')
            self.banner_no_solution.show()
            self.drop_clock_events()
        else:
            print('problem solved')
            self.output_table_d = self.get_run_datatable_todisplay()
            self.create_output_screen()
            self.add_output_table_toscreen()
            self.drop_clock_events()
            self.get_output_screen()

    def get_run_datatable(self, *args):
        '''
        This finction returns the input data if correctly inserted, otherwise an empty dict
        '''
        self.table_run = self.table.get_row_checks()
        if self.table_run == []:
            self.banner_no_solution.show()
        else:
            self.df_run_simulation = self.datatable_to_df()
            self.df_run_simulation['avaliable places'] = self.df_run_simulation['avaliable places'].astype(int)

            if len(self.df_run_simulation) > 0:
                # Get input data
                self.input_data = {
                    "Name": list(self.df_run_simulation.user),
                    "demands": [1 if ap == 0 else 0 for ap in self.df_run_simulation['avaliable places']],
                    "free_places": list(self.df_run_simulation['avaliable places']),
                    "address": list(self.df_run_simulation['address']),
                    "city": list(self.df_run_simulation['city'])
                }

                # Update info with destination data
                self.get_info_group()
                self.input_data['Name'].append('destination')
                self.input_data['demands'].append(1)
                self.input_data['free_places'].append(0)
                self.input_data['address'].append(self.destination_address)
                self.input_data['city'].append(self.destination_city)
            else:
                self.input_data = {}

    def run_model(self, *args):
        '''
        Funtion to call the AWS lambda function: it returns an empty dict if not feasable
        '''
        try:
            r = requests.get('https://5z5t5ge610.execute-api.us-east-2.amazonaws.com//get_shifts',
                             params=self.input_data
                             )
            self.shifts, self.df_geocoded = r.json()
            self.df_geocoded = pd.DataFrame(self.df_geocoded)
        except:
            self.shifts = {}

    def get_output_screen(self, *args):
        self.change_screen(f"Output screen -- {self.group_screen}")

    def get_run_datatable_todisplay(self):
        '''
        This function transforms the model output into the MDDataTable to display on the output screen
        '''
        self.output_table_final = pd.DataFrame()
        self.df_geocoded_f = self.df_geocoded.loc[self.df_geocoded['lat'] != 'cannot geocode'].reset_index(drop=True)

        for index, shift in enumerate(list(self.shifts.keys())[:-1]): # questo perchè non voglio considerare anche la total distance che è l'ultimo elemento della lista
            df_trip = pd.DataFrame(self.shifts[shift], columns=['trip_order'])
            self.output_table_name = [self.df_geocoded_f['Name'][index] for index in df_trip['trip_order']]
            self.output_table_address = [self.df_geocoded_f['Address'][index] for index in df_trip['trip_order']]

            self.output_table_f = pd.DataFrame({
                'order': self.output_table_name,
                'address': self.output_table_address
            })

            self.output_table_f['order'] = self.output_table_f['order'].astype(str)
            self.output_table_f = self.output_table_f.reset_index()
            self.output_table_f['car'] = index
            self.output_table_f = self.output_table_f[['car', 'index', 'order', 'address']] #Distance
            self.output_table_f.columns = ['Car', 'Shift', 'Pick order', 'address'] #Total distance
            self.output_table_final = pd.concat([self.output_table_final, self.output_table_f],
                                                axis=0,
                                                ignore_index=True)

        # Create data table
        column_data = list(self.output_table_final.columns)
        column_data = [(x, dp(60)) for x in column_data]
        row_data = self.output_table_final.to_records(index=False)

        self.output_table_d = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            check=False,
            use_pagination=True,
            rows_num=len(self.output_table_final) + 3,
            pos_hint={'top': 0.7, 'center_x': 0.5}
        )

        del self.output_table_final, self.output_table_f

        return self.output_table_d

    def create_output_screen(self):
        '''
        This function creates a new output screen for the run model, if another run has been implemented before
        it drops the previous one
        '''
        self.output_screen = Screen(name=f"Output screen -- {self.group_screen}")

        # Remove output screen if previously created
        if self.output_screen.name in self.ids.screen_manager.screen_names:
            self.ids.screen_manager.remove_widget(self.ids.screen_manager.get_screen(self.output_screen.name))

        # Create new output screen
        self.ids.screen_manager.add_widget(self.output_screen)
        self.ids.screen_manager.ids[f"{self.output_screen}"] = weakref.ref(self.output_screen)

    def add_output_table_toscreen(self):
        '''
        This function appends the final output table to the output screen previously created
        '''
        # Function to create the output layout to show the output data table
        self.layout_output = MDFloatLayout(
            size=(self.width,
                  self.height)
        )
        onelistitem_output_screen = OneLineListItem(text=f"Group: [b]{self.group_screen}[/b]",
                                                    pos_hint={'top': 1, 'center_x': 0.5})
        self.layout_output.add_widget(onelistitem_output_screen)
        onelistitem_output_destination = OneLineListItem(
            text=f"Group destination: [b]{self.destination_address} ({self.destination_city})[/b]",
            pos_hint={'top': 0.9, 'center_x': 0.5})
        self.layout_output.add_widget(onelistitem_output_destination)
        onelistitem_users_not_geocoded = OneLineListItem(
            text=f"Users not geocoded: [b]{str(self.shifts['users_not_geocoded'])}[/b]",
            pos_hint={'top': 0.8, 'center_x': 0.5})
        self.layout_output.add_widget(onelistitem_users_not_geocoded)

        self.ids.screen_manager.get_screen(f'Output screen -- {self.group_screen}').add_widget(self.layout_output)
        self.layout_output.add_widget(self.output_table_d)

    def remove_screen_after_run(self):
        '''
        This function removes the output screen after leaving it
        '''
        #
        self.ids.screen_manager.get_screen(f'Output screen -- {self.output_screen}').on_leave(
            self.ids.screen_manager.remove_widget(self.ids.screen_manager.get_screen(f'Output screen -- {self.output_screen}'))
        )

    def join_existing_group(self, *args):
        self.join_group_name = self.ids.join_group_name.text
        self.join_group_password = self.ids.join_group_password.text
        join_path = self.ref.child('groups').get()

        if self.join_group_name in join_path.keys():
            if self.user.uid in join_path[self.join_group_name]['group users'].keys():
                self.dialog_button(two_alternatives=False,
                                   text_button='Retry',
                                   text_button2='',
                                   dialog_title=f'join not succeed',
                                   dialog_text='user already joined the group',
                                   action_button2='')
            elif self.join_group_password != str(join_path[self.join_group_name]['admin']['password']):
                self.dialog_button(two_alternatives=False,
                                   text_button='Retry',
                                   text_button2='',
                                   dialog_title=f'join not succeed',
                                   dialog_text='wrong password',
                                   action_button2='')
            else:
                self.dialog_button(two_alternatives=False,
                                   text_button='OK',
                                   text_button2='',
                                   dialog_title=f'join succeed',
                                   dialog_text=f'Joined group {self.join_group_name}',
                                   action_button2='')

                self.ref.child('groups').child(f"{self.join_group_name}").child('group users').update(
                    {f"{self.user.uid}": True}
                )

                self.remove_screens()
                self.on_pre_enter()
                self.update_user_groups()
        else:
            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title=f'join not succeed',
                               dialog_text=f'{self.join_group_name} does not exists',
                               action_button2='')

    def cancel_user_data_from_group_in_db(self, group_list: list):
        for group in group_list:
            self.ref.child('groups').child(group).child('group users').child(f'{self.user.uid}').delete()
            if self.user.uid in self.ref.child('groups').child(group).child('users data').get().keys():
                self.ref.child('groups').child(group).child('users data').child(f'{self.user.uid}').delete()

    def leave_group(self, *args):
        self.cancel_user_data_from_group_in_db(group_list=[self.group_screen])
        self.remove_screens()
        self.on_pre_enter()
        self.dialog_button(two_alternatives=False,
                           text_button='OK',
                           text_button2='',
                           dialog_title=f'Succeed',
                           dialog_text=f'Group deleted',
                           action_button2='')

    def create_new_group(self):
        self.group_name = self.ids.group_name.text
        self.group_password = self.ids.group_password.text
        self.group_destination_city = self.ids.group_destination_city.text
        self.group_destination_address = self.ids.group_destination_address.text
        self.user_departure_city = self.ids.user_departure_city.text
        self.user_departure_address = self.ids.user_departure_address.text
        self.user_n_avaliable_places = self.ids.user_n_avaliable_places.text

        data_to_set = {
            f"{self.group_name}": {
                "admin": {
                    "password": self.group_password,
                    "destination city": self.group_destination_city,
                    "destination address": self.group_destination_address
                },
                "group users": {
                    "admin": True,
                    f"{self.user.uid}": True
                },
                "users data": {
                    "admin": {
                        "address": "casa",
                        "avaliable places": 0
                    },
                    f"{self.user.uid}": {
                        "city": self.user_departure_city,
                        "address": self.user_departure_address,
                        "avaliable places": self.user_n_avaliable_places  # TODO: check toint
                    }
                }
            }
        }

        if not self.group_name in self.ref.child('groups').get().keys():
            self.ref.child('groups').update(data_to_set)
            self.remove_screens()
            self.on_pre_enter()
            self.dialog_button(two_alternatives=False,
                               text_button='OK',
                               text_button2='',
                               dialog_title='Group created',
                               dialog_text='Share the group password with your friends to let them join the group',
                               action_button2='')

            self.update_user_groups()
        else:
            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title='Group name already exists',
                               dialog_text='A group with the same name already exists, choose another name',
                               action_button2='')

    def update_user_groups(self):
        self.user_groups = self.get_user_groups()

    def remove_screens(self):
        keep_groups = ['scr add group', 'screen join group'] #'screen profile',
        # Drop dynaically created screens
        for screen in self.ids.screen_manager.screen_names:
            if screen not in keep_groups:
                self.ids.screen_manager.remove_widget(self.ids.screen_manager.get_screen(screen))
        # Drop dynaically created lists in scrollview
        keep_scroll_items = ['Join existing group'] # 'Profile'
        widgets_toremove = []
        for i, scroll_element in enumerate(self.ids.contentnavigationdrawer.ids.container.children):
            if scroll_element.text not in keep_scroll_items:
                widgets_toremove.append(scroll_element)

        self.ids.contentnavigationdrawer.ids.container.clear_widgets(widgets_toremove)
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
        self.avaliable_places_button = self.layout_user.children[3].text
        self.city_button = self.layout_user.children[2].text
        self.address_button = self.layout_user.children[1].text

        data_to_set = {
            "city": self.city_button,
            "address": self.address_button,
            "avaliable places": self.avaliable_places_button
        }

        self.group_screen_updated = self.group_screen
        self.ref.child('groups').child(f'{self.group_screen}').child('users data').child(f"{self.user.uid}").set(
            data_to_set)
        self.remove_screens()
        self.on_pre_enter()
        # GO back to the previous screen
        self.group_screen = self.group_screen_updated
        self.change_screen(self.group_screen)

    def get_user(self):
        return auth.get_user_by_email(self.parent.get_screen('login').ids.login_email.text)

    def get_main_screen(self, scrren_name: str):
        self.parent.current = scrren_name
        self.ids.nav_drawer.set_state("close")

    def change_screen(self, scrren_name: str):
        self.ids.screen_manager.current = scrren_name
        self.ids.nav_drawer.set_state("close")

    def get_group_data(self):
        group_path = self.ref.child('groups').child(f'{self.group_screen}').child('users data').get()
        df_list = []
        for uid in group_path.keys():
            if uid != "admin":
                user = auth.get_user(uid)
                username = user.display_name
                dict_grpup = group_path[uid]
                dict_grpup.update({
                    "user": username
                })
                df = pd.DataFrame.from_dict(dict_grpup, orient='index')
                df_list.append(df)

        try:
            df_group = pd.concat(df_list, axis=1).T.reset_index(drop=True)
            df_group = df_group[['user', "city", "address", "avaliable places"]]
        except:
            df_group = pd.DataFrame(columns=['user', "city", "address", "avaliable places"])

        return df_group

    def get_data_table(self):
        df_group = self.get_group_data()
        column_data = list(df_group.columns)
        column_data = [(x, dp(60)) for x in column_data]
        row_data = df_group.to_records(index=False)
        table = MDDataTable(
            column_data=column_data,
            row_data=row_data,
            check=True,
            use_pagination=True,
            rows_num=len(df_group) + 3,
            pos_hint={'top': 0.8, 'center_x': 0.5}
        )
        return table

    def dialog_button(self,
                      two_alternatives: bool,
                      text_button: str,
                      text_button2: str,
                      dialog_title: str,
                      dialog_text: str,
                      action_button2: str):

        if self.dialog:
            self.dialog = None
        if two_alternatives is True:
            if not self.dialog:
                self.dialog = MDDialog(title=dialog_title,
                                       text=dialog_text,
                                       buttons=[MDFlatButton(text=text_button,
                                                             on_release=self.close_username_dialog),
                                                MDFlatButton(text=text_button2,
                                                             on_press=eval(action_button2),
                                                             on_release=self.close_username_dialog)
                                                ]
                                       )
                self.dialog.open()
        else:
            if not self.dialog:
                self.dialog = MDDialog(title=dialog_title,
                                       text=dialog_text,
                                       buttons=[MDFlatButton(text=text_button,
                                                             on_release=self.close_username_dialog)
                                                ]
                                       )
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
    sm.add_widget(LoadingScreen(name='loading'))
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
        self.app = Test.get_running_app()
        self.dialog = None
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

    def DeleteAccount(self, *args):
        payload = json.dumps({
            "idToken": self.idToken
        })
        r = requests.post(self.requests_delete_account.format(self.web_apk),
                          params={"key": self.web_apk},
                          data=payload)
        if 'error' in r.json().keys():
            error_dict = {'status': 'error', 'message': r.json()['error']['message']}
            self.dialog_button(two_alternatives=False,
                               text_button='OK',
                               text_button2='',
                               dialog_title=error_dict['status'],
                               dialog_text=error_dict['message'],
                               action_button2='')
        else:
            self.root.current = 'login'

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
            self.dialog_button(two_alternatives=False,
                               text_button='OK',
                               text_button2='',
                               dialog_title="Reset email",
                               dialog_text=f"Email sent to {self.resetEmail}",
                               action_button2='')
            return r.json()

    add_ScreenManager()

    def signup(self):
        self.signupEmail = self.strng.get_screen('signup').ids.signup_email.text
        self.signupUsername = self.strng.get_screen('signup').ids.signup_username.text
        self.signupPassword = self.strng.get_screen('signup').ids.signup_password.text

        if (len(self.signupEmail.split()) == 0
                or len(self.signupPassword.split()) == 0
                or len(self.signupUsername.split()) == 0):

            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title="Invalid input",
                               dialog_text='Please Enter a valid Input',
                               action_button2='')

        elif len(self.signupUsername.split()) > 1:

            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title="Invalid Username",
                               dialog_text='Please enter username without space',
                               action_button2='')

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
                self.dialog_button(two_alternatives=False,
                                   text_button='Retry',
                                   text_button2='',
                                   dialog_title="Error",
                                   dialog_text=f'{r.json()["error"]["message"]}',
                                   action_button2='')

            if 'idToken' in r.json().keys():
                self.idToken = r.json()['idToken']
                self.VerifyEmail()
                self.dialog_button(two_alternatives=False,
                                   text_button='OK',
                                   text_button2='',
                                   dialog_title="Succeed",
                                   dialog_text='We sent you a verification email',
                                   action_button2='')
                self.strng.get_screen('login').manager.current = 'login'

    def login(self):
        self.loginEmail = self.strng.get_screen('login').ids.login_email.text
        self.loginPassword = self.strng.get_screen('login').ids.login_password.text
        self.login_check = False

        try:
            self.user = auth.get_user_by_email(self.loginEmail)
        except:
            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title="Error",
                               dialog_text='Email not recognized',
                               action_button2='')

        details = {
            'email': self.loginEmail,
            'password': self.loginPassword,
            'returnSecureToken': True
        }

        r = requests.post(self.requests_signin.format(self.web_apk),
                          data=details)

        if 'error' in r.json().keys():
            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title="Error",
                               dialog_text=f'{r.json()["error"]["message"]}',
                               action_button2='')

        elif 'idToken' in r.json().keys() and not self.user.email_verified:
            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title="Error",
                               dialog_text='Your email has not been verified',
                               action_button2='')

        elif 'idToken' in r.json().keys() and self.user.email_verified:
            self.login_check = True
            self.idToken = r.json()['idToken']
            # self.strng.get_screen('main').manager.current = 'main'
            self.root.current = 'main'

        else:
            self.dialog_button(two_alternatives=False,
                               text_button='Retry',
                               text_button2='',
                               dialog_title="Error",
                               dialog_text='Unknown error',
                               action_button2='')

    def dialog_button(self,
                      two_alternatives: bool,
                      text_button: str,
                      text_button2: str,
                      dialog_title: str,
                      dialog_text: str,
                      action_button2: str):

        if two_alternatives is True:
            self.dialog = MDDialog(title=dialog_title,
                                   text=dialog_text,
                                   buttons=[MDFlatButton(text=text_button,
                                                         on_release=self.close_username_dialog),
                                            MDFlatButton(text=text_button2,
                                                         on_release=eval(action_button2))
                                            ]
                                   )
            self.dialog.open()
        else:
            self.dialog = MDDialog(title=dialog_title,
                                   text=dialog_text,
                                   buttons=[MDFlatButton(text=text_button,
                                                         on_release=self.close_username_dialog)
                                            ]
                                   )
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
