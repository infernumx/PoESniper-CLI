import PySimpleGUI as sg
from datetime import datetime

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

class GUI():
    def __init__(self, app):
        layout = [
            [sg.Text('Results', font=THEME_FONT, background_color="#2c2825")],
            [sg.Listbox(values=[], enable_events=True, size=(75, 15), key="_WHISPER_LIST_", background_color="#666666")],
            [sg.Button('Start', font=THEME_FONT), sg.Button('Send PM', font=THEME_FONT)],
            [sg.Text('Websocket Status', font=THEME_FONT, background_color="#2c2825")],
            [sg.Listbox(values=[], enable_events=True, size=(30, 10), key="_WEBSOCKET_STATUS_", background_color="#666666")]
        ]

        self.app = app

        self.results = []
        self.whispers = []

        sg.theme('SniperTheme')
        self.window = sg.Window('PoESniper', layout, icon="resources/favicon.ico", size=(600,400), default_element_size=(20,1))
        self.main()

    def add_item(self, item):
        self.results.insert(0, '{}: {}x {} -> {} Chaos profit'.format(
            datetime.now().strftime('%H:%M:%S'),
            item['count'],
            item['name'],
            item['profit']
        ))
        self.whispers.insert(0, item['whisper'])
        self.window.FindElement('_WHISPER_LIST_').Update(values=self.results)

    def main(self):
        while True:
            event, value = self.window.read()
            print(event, value)

            if event is None:
                break
            elif event == 'Start':
                self.app.start(self)

        self.window.close()