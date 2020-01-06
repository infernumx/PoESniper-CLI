import PySimpleGUI as sg
from datetime import datetime
from pynput.keyboard import Key, Controller
import pygetwindow as gw
import time

keyboard = Controller()

sg.LOOK_AND_FEEL_TABLE["SniperTheme"] = {
    "BACKGROUND": "#2c2825",
    "TEXT": ("#2c2825", "#2c2825"),
    "INPUT": "#2c2825",
    "TEXT_INPUT": "#2c2825",
    "SCROLL": "#2c2825",
    "BUTTON": ("abc", "#2c2825"),
    "PROGRESS": ("abc", "#2c2825"),
    "BORDER": 1,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0
}

THEME_FONT = ("MingLiU", 12)

sg.set_options(ttk_theme='clam')

class GUI():
    def __init__(self, app):
        layout = [
            # Row 1
            [
                sg.Text(
                    'Results',
                    font=THEME_FONT,
                    background_color="#2c2825"
                )
            ],
            # Row 2
            [
                sg.Listbox(
                    values=[],
                    enable_events=True,
                    size=(75, 15),
                    key="_WHISPER_LIST_",
                    background_color="#666666"
                )
            ],
            # Row 3
            [
                sg.Button(
                    'Start',
                    key='_TOGGLE_BUTTON_',
                    font=THEME_FONT
                ),
                sg.Button(
                    'Send PM',
                    key='_SEND_PM_',
                    font=THEME_FONT
                )
            ],
            # Row 4
            [
                sg.Text(
                    'Websockets Connected: 0',
                    key='_WEBSOCKET_CONNECTIONS_',
                    size=(50,1),
                    font=THEME_FONT,
                    background_color="#2c2825"
                )
            ]
        ]

        self.app = app

        self.results = []
        self.whispers = []
        self.unique_results = set()

        sg.theme('SniperTheme')
        self.window = sg.Window(
            'PoESniper',
            layout,
            icon="resources/favicon.ico",
            size=(600,400),
            default_element_size=(20,1)
        ).Finalize()

        self.main()

    def update_element(self, key, value):
        self.window[key].Update(value)

    def add_item(self, item):
        profit = str(item['profit'])
        profit = profit.ljust(6 - len(profit))
        buyout = str(item['full_cost'])
        buyout = buyout.ljust(6 - len(buyout))
        count = str(item['count'])
        count = count.ljust(6 - len(count))
        name = item['name'].rjust(30 - len(item['name']))
        result_str = '[{}] Profit: {:<4} Buyout: {:<4} x{:<2} {} | {}'.format(
            datetime.now().strftime('%H:%M:%S'),
            profit,
            buyout,
            count,
            name,
            item['seller']
        )

        if not result_str in self.unique_results:
            self.results.insert(0, result_str)
            self.unique_results.add(result_str)
            self.whispers.insert(0, item['whisper'])
            self.window['_WHISPER_LIST_'].Update(values=self.results)
            self.selected_whisper = self.whispers[0]

    def send_whisper(self, msg):
        titles = gw.getAllTitles()
        if 'Path of Exile' in titles:
            window = gw.getWindowsWithTitle('Path of Exile')[0]
            window.activate()
            time.sleep(0.1)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            keyboard.type(msg)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)

    def main(self):
        self.selected_whisper = None
        while True:
            event, value = self.window.read()
            # print(event, value)

            if event is None:
                break
            elif (event == '_TOGGLE_BUTTON_' and
                    self.window['_TOGGLE_BUTTON_'].get_text() == 'Start'):
                self.window['_TOGGLE_BUTTON_'].Update(text='Stop')
                self.app.start(self)
            elif (event == '_TOGGLE_BUTTON_' and
                    self.window['_TOGGLE_BUTTON_'].get_text() == 'Stop'):
                self.window['_TOGGLE_BUTTON_'].Update(text='Start')
                self.app.stop()
            elif event == '_WHISPER_LIST_':
                if len(value['_WHISPER_LIST_']) == 0:
                    continue

                result = value['_WHISPER_LIST_'][0]
                for i, res in enumerate(self.results):
                    if res == result:
                        self.selected_whisper = self.whispers[i]
                        break
            elif event == '_SEND_PM_':
                if self.selected_whisper:
                    self.send_whisper(self.selected_whisper)
                elif len(self.whispers) == 1:
                    self.send_whisper(self.whispers[0])

        self.window.close()
