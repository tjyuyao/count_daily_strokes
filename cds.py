import os
import shelve
import time, datetime, pytz
import PySimpleGUI as sg
from typing import Dict, Tuple
from psgtray import SystemTray
from dataclasses import dataclass
from pathlib import Path
from pynput import mouse, keyboard
from math import sqrt, fabs
import tkinter

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.axes import Axes

matplotlib.use('TkAgg')


@dataclass
class Model:
    num_keystrokes: int = 0
    num_mouse_clicks: int = 0
    length_mouse_track: float = 0.
    prev_mouse_loc: Tuple[int, int] = None
    time_tick: float = 0.
    move_period: float = 0.1


def get_icon():
    return b'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'


class Controller:

    def __init__(self) -> None:
        
        self._init_model()
        
        menu = ['', ['Exit']]

        layout = [
            [sg.Text('Recent 7 Days Trend')],
            [sg.TabGroup([
                [sg.Tab("Key Strokes", [[sg.Canvas(key='-CANVAS-K-')]])],
                [sg.Tab("Mouse Clicks", [[sg.Canvas(key='-CANVAS-M-')]])],
                [sg.Tab("Mouse Tracks", [[sg.Canvas(key='-CANVAS-L-')]])],
            ])]
        ]

        self.window = sg.Window('Daily Stroke Counter', layout, finalize=True, enable_close_attempted_event=True)
        self.window.hide()
        self.window_visible = False

        self.tray = SystemTray(menu, single_click_events=False, window=self.window, tooltip='---', icon=get_icon(), key='-TRAY-')
        
        self.figures = {k: matplotlib.figure.Figure(figsize=(5, 4), dpi=100) for k in "KML"}
        self.plts: Dict[str, Axes] = {k:f.add_subplot(111) for k, f in self.figures.items()}
        self.tkcanvas = {k:self._init_canvas(figure=f, canvas=self.window[f'-CANVAS-{k}-'].TKCanvas) for k, f in self.figures.items()}

        self.dpi = self.window.TKroot.winfo_fpixels('1i') / 2.54 * 100

    def _update_stat(self, init=False):
        self.todate = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).date().strftime("%Y-%m-%d")
        if self.todate not in self.db_file:
            stat = Model()
            stat.time_tick = time.time()
            self.db_file[self.todate] = stat
            self.stat = self.db_file[self.todate]
        elif init:
            self.stat = self.db_file[self.todate]

    def _init_model(self):
        db_loc = Path.home() / ".daily_stroke_counter"
        db_loc.mkdir(parents=True, exist_ok=True)
        db_path = db_loc / "database"
        self.db_file = shelve.open(str(db_path), writeback=True)
        self._update_stat(init=True)

    @staticmethod
    def _init_canvas(figure, canvas):
        tkcanvas = FigureCanvasTkAgg(figure, canvas)
        tkcanvas.draw()
        tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        return tkcanvas
    
    def run(self):
        while True:
            event, values = self.window.read(timeout=1000)

            self.sync()

            if event == self.tray.key:
                event = values[event]

            if event in ('Show Window', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self.window.un_hide()
                self.window.bring_to_front()
                self.window_visible = True

            elif event in ('Hide Window', sg.WIN_CLOSE_ATTEMPTED_EVENT):
                self.window.hide()
                self.tray.show_icon()
                self.window_visible = False

            if event in (sg.WIN_CLOSED, 'Exit'):
                break

        self.db_file.close()
        self.tray.close()
        self.window.close()

    def sync(self):
        text = f"K:{self.stat.num_keystrokes}\nM:{self.stat.num_mouse_clicks}\nL:{self.stat.length_mouse_track:.0f} m"
        self.tray.set_tooltip(text)
        self.db_file[self.todate] = self.stat
        self.db_file.sync()
        self._update_stat()

        if self.window_visible:
            self.draw()

    def draw(self):
        dates = sorted(self.db_file.keys())
        dates = dates[-7:]
        idate = np.arange(len(dates))
        data = dict(K=[], M=[], L=[])
        for date in dates:
            stat: Model = self.db_file[date]
            data['K'].append(stat.num_keystrokes)
            data['M'].append(stat.num_mouse_clicks)
            data['L'].append(stat.length_mouse_track)
        colors = dict(
            K="blue",
            M="purple",
            L="orange",
        )
        for k in "KML":
            plt = self.plts[k]
            yaxis = np.array(data[k])
            plt.cla()
            plt.set_xticks(idate, dates)
            plt.plot(idate, yaxis, marker='o', color=colors[k])
            self.tkcanvas[k].draw()


ctrl = Controller()


def on_move(nx, ny):
    now = time.time()
    if ctrl.stat.prev_mouse_loc is not None and \
        now - ctrl.stat.time_tick > ctrl.stat.move_period:
        px, py = ctrl.stat.prev_mouse_loc
        ctrl.stat.length_mouse_track += sqrt((px-nx)*(px-nx) + (py-ny)*(py-ny)) / ctrl.dpi
        ctrl.stat.time_tick = now
    ctrl.stat.prev_mouse_loc = (nx, ny)


def on_click(x, y, button, pressed):
    if not pressed:
        ctrl.stat.num_mouse_clicks += 1


def on_scroll(x, y, dx, dy):
    ctrl.stat.num_mouse_clicks += (fabs(dx) + fabs(dy))


def on_press(key):
    ctrl.stat.num_keystrokes += 1


keyboard_listener = keyboard.Listener(
    on_press=on_press)


mouse_listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)


keyboard_listener.start()
mouse_listener.start()
ctrl.run()
keyboard_listener.stop()
mouse_listener.stop()
keyboard_listener.join()
mouse_listener.join()
