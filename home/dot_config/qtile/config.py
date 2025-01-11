# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import socket
import subprocess
import psutil
import json
import asyncio
from libqtile import hook
from libqtile import qtile
from typing import List
from libqtile import bar, layout, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen, ScratchPad, DropDown, KeyChord
from libqtile.lazy import lazy
from libqtile.widget import Spacer, Backlight
from libqtile.widget.image import Image
from libqtile.dgroups import simple_key_binder
from pathlib import Path
from qtile_extras import widget
from qtile_extras.widget import WiFiIcon
from qtile_extras.widget.decorations import PowerLineDecoration, RectDecoration
from subprocess import Popen

import colors

mod = "mod4"
alt = "mod1"
terminal = "kitty"

# powerline = {
#     "decorations": [
#         PowerLineDecoration(path='arrow_right')
#     ]
# }

decor_layout = {
    "decorations": [
        RectDecoration(radius=8,
        filled=True, clip=True, padding_y=2)
    ],
}

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.

    #Monadtall
    Key([mod, "control"], "j", lazy.layout.grow_main(), desc="Grow main window"),
    Key([mod, "control"], "k", lazy.layout.grow(), desc="Grow other window"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Switch focus of monitors
    Key([mod], "period", lazy.next_screen(), desc='Move focus to next monitor'),
    Key([mod], "comma", lazy.prev_screen(), desc='Move focus to prev monitor'),
    # Switch focus to specific monitor (out of three)
    Key([mod], "i", lazy.to_screen(2)),
    Key([mod], "o", lazy.to_screen(0)),
    Key([mod], "p", lazy.to_screen(1)),

    # Special keys volume control
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%")),
    Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")),
    # Use playerctl for media player controls
    Key([], "XF86AudioPlay", lazy.spawn("playerctl play-pause")),
    Key([], "XF86AudioNext", lazy.spawn("playerctl next")),
    Key([], "XF86AudioPrev", lazy.spawn("playerctl previous")),



    # Toggle between split and unsplit sides of stack
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawn("rofi -show drun"), desc="Spawn Rofi"),
    Key([mod], "l", lazy.spawn("betterlockscreen -l"), desc="Lock screen"),


    KeyChord([mod], "x", [
        Key([], "t", lazy.spawn("thunar")),
        Key([], "v", lazy.spawn("vivaldi")),
        Key([], "c", lazy.spawn("code")),
    ])
]


# Create labels for groups and assign them a default layout.
groups = []

group_names = ["1", "2", "3", "4", "5","6","7","8","9"]

group_labels = ["󰅱", "", "", "󰙯", "","󱃾","","",""]
#group_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

group_layouts = ["max", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall","max","max","treetab"]

# Add group names, labels, and default layouts to the groups object.
for i in range(len(group_names)):
    groups.append(
        Group(
            name=group_names[i],
            layout=group_layouts[i].lower(),
            label=group_labels[i],
        ))

# Add group specific keybindings
for i in groups:
    keys.extend([
        Key([mod], i.name, lazy.group[i.name].toscreen(), desc="Mod + number to move to that group."),
        Key([alt], "Tab", lazy.screen.next_group(), desc="Move to next group."),
        Key([alt, "shift"], "Tab", lazy.screen.prev_group(), desc="Move to previous group."),
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name), desc="Move focused window to new group."),
    ])



#Define scratchpads
groups.append(ScratchPad("0",[
   DropDown("cider", "cider", match=Match(wm_class=['cider']), width=0.6, height=0.6, x=0.2, y=0.1, opacity=1, on_focus_lost_hide=True ),
   DropDown("discord", "discord", match=Match(wm_class=['discord']), width=0.6, height=0.6, x=0.3, y=0.1, opacity=1, on_focus_lost_hide=False ),
   DropDown("slack", "slack", match=Match(wm_class=['slack']), width=0.8, height=0.8, x=0.1, y=0.1, opacity=1, on_focus_lost_hide=True ),
   DropDown("terminal", "kitty --class=scratch", width=0.4, height=0.4, x=0.3, y=0.1, opacity=1, on_focus_lost_hide=False ),
   DropDown("obsidian", "obsidian", match=Match(wm_class=['obsidian']) , x=0.3, y=0.1, width=0.6, height=0.6, on_focus_lost_hide=True ),
]))

keys.extend([
   Key([mod], 'F7', lazy.group["0"].dropdown_toggle("cider")),
   Key([mod], 'F8', lazy.group["0"].dropdown_toggle("discord")),
   Key([mod], 'F9', lazy.group["0"].dropdown_toggle("obsidian")),
   Key([mod], 'F11', lazy.group["0"].dropdown_toggle("terminal")),
])



colors = colors.Dracula

layout_theme = {
        "margin":5,
        "border_width": 4,
        "border_focus": colors[8],
        "border_normal": colors[0],
    }


layouts = [
    layout.Max(**layout_theme),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    layout.MonadTall(**layout_theme),
    layout.MonadWide(**layout_theme),
    # layout.RatioTile(),
    # layout.Tile(),
    layout.TreeTab(**layout_theme),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

Key([mod], "equal",
        lazy.layout.grow().when(layout=["monadtall", "monadwide"]),
        desc="Grow window to the left"
    ),
Key([mod], "minus",
        lazy.layout.shrink().when(layout=["monadtall", "monadwide"]),
        desc="Grow window to the right"
    ),

widget_defaults = dict(
    font="Fira Code Nerd Font",
    fontsize=13,
    background=colors[0],
    foreground = colors[0]
)
extension_defaults = widget_defaults.copy()

def init_widgets_list():
    widgets_list = [
        widget.GroupBox(
            fontsize = 16,
            icon_size = 12,
            margin_y = 3,
            margin_x = 4,
            padding_y = 6,
            padding_x = 6,
            borderwidth = 2,
            disable_drag = True,
            active = colors[6],
            inactive = colors[2],
            hide_unused = False,
            rounded = False,
            highlight_method = "line",
            highlight_color = [colors[1], colors[1]],
            this_current_screen_border = colors[10],
            this_screen_border = colors[4],
            other_screen_border = colors[10],
            other_current_screen_border = colors[10],
            urgent_alert_method = "line",
            urgent_border = colors[3],
            urgent_text = colors[1],
            foreground = colors[1],
            background = colors[0],
            use_mouse_wheel = False
        ),
        widget.CurrentLayout(font="JetBrains Mono Nerd Font Bold", font_size = 20, foreground = colors[8], background = colors[0]),
        widget.Spacer(length = 10),
        widget.WindowName(
            font = "Fira Code Nerd Font Semi Bold", 
            font_size = 14,
            foreground = colors[9],
            background = colors[0],
            max_chars = 20,
            padding = 5,
            width = 100   
        ),
        widget.Spacer(length = 10),
        widget.Mpris2(name = "Cider Player",
            format = '󰝚 {xesam:title} - {xesam:album} - {xesam:artist} 󰝚',
            font = "JetBrains Mono Nerd Font Bold",
            fontsize = 12,
            foreground = colors[4],
            background = colors[0],
            max_chars = 50,
            width = 175,
            scroll_chars=50,
            stopped_text = 'Cider Player'
            ),
        widget.Spacer(length = bar.STRETCH),
        # widget.StatusNotifier(
        #     background = colors[0],
        #     foreground = colors[1],
        #     icon_theme = "Dracula",
        #     icon_size = 14,

        # ),
        
        widget.Systray(
            background = colors[0],
            padding = 3,
        ),
        widget.Pomodoro(
            forground = colors[6],
            background = colors[0],
            padding = 10,
            color_break = colors[9],
            color_active = colors[4],
            notifications_on = True,
            prefix_break = "Break",
            prefix_long_break = "Long Break",
            prefix_paused = "Paused",
            font = "JetBrains Mono Nerd Font Bold",
            fontsize = 14,
            num_pomodori = 2,
            width = 150
        ),
        widget.Spacer(length = bar.STRETCH),
        widget.CheckUpdates(
            font = "Fira Code Nerd Font",
            display_format = 'Updates: {updates}',
            fmt ='',
            colour_have_updates = colors[8],
            foreground = colors[8],
            background = colors[0],
            padding = 5,
            distro = 'Arch',                            
            no_update_string ='No updates',
            update_interval =36000,
            ),
        widget.Sep(linewidth = 5),
        widget.CPU(
            font = "Fira Code Nerd Semi Bold Font",
            update_interval = 1.0,
            format = '  {load_percent}%',
            foreground = colors[9],
            background = colors[0],
            margin_x = -5,
            padding_x = 2,
            width = 65,
            **decor_layout
        ),
        widget.Sep(linewidth = 5),
        widget.Memory(
            font = "Fira Code Nerd Semi Bold Font",
            foreground = colors[8],
            background = colors[0],
            format = '󰍛  {MemUsed: .0f}{mm} /{MemTotal:.0f}{mm}',
            measure_mem='G',
            padding_x = 4,
            **decor_layout
        ),
        widget.Sep(linewidth = 5),

        widget.Net(
            font = "Fira Code Nerd Semi Bold Font",
            foreground = colors[6],
            background = colors[0],
            interface = 'wlan0',
            margin = 5,
            format='    {down:.0f}{down_suffix} ↓↑ {up:.0f}{up_suffix} ',
#            width = 100,
            prefix = 'M',
            **decor_layout
        ),
        widget.Sep(linewidth = 5),
        widget.OpenWeather(
             app_key = "bc1845b0fde582381563d9e74f5aca7b",
             cityid = "4612862",
             format = '  {main_temp}° {humidity}% ',
             metric = False,
             update_interval = 1800,
             font = "Fira Code Nerd Font",
             fontsize = 12,
             foreground = colors[4],
             background = colors[0],
             **decor_layout

         ),
        widget.Sep(linewidth = 5),
        widget.Clock(format='   %A %m/%d %I:%M%p',
                     font = "Fira Code Nerd Semi Bold Font",
                     fontsize = 13,
                     foreground = colors[7],
                     background = colors[0],
                     padding_x = 5,
                     **decor_layout
                     ),
        widget.Sep(linewidth = 5),
        widget.QuickExit(
            countdown_start = 7,
            # fontshadow = None, # 'shadow'
            default_text = '',
            # countdown_format = '<span foreground="' + colors[1] + '">{}</span>',``
            padding = 8,
            background = colors[6],
            mouse_callbacks = {
                'Button1':
                lazy.spawn("rofi -show power-menu -modi power-menu:~/.local/bin/rofi-power-menu"),
            },
        ),    
    ]

    return widgets_list

def init_widgets_screen1():
    widgets_screen1 = init_widgets_list()
    return widgets_screen1 

def init_widgets_screen2():
    widgets_screen2 = init_widgets_list()
    del widgets_screen2[4::]
    return widgets_screen2


def init_screens():
    return [Screen(top=bar.Bar(widgets=init_widgets_screen1(), size=21, background=colors[0], margin=0, opacity=0.8)),
            Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=19, background=colors[0], margin=0, opacity=0.8)),
            Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=22, background=colors[0], margin=0, opacity=0.8))]

if __name__ in ["config", "__main__"]:
    screens = init_screens()
    widgets_list = init_widgets_list()
    widgets_screen1 = init_widgets_screen1()
    widgets_screen2 = init_widgets_screen2()

# Group Screen Assignments
# groups[0].screen = 0
# groups[1].screen = 2
# groups[2].screen = 1

# screens[0].groups =[1]
# screens[1].groups =[3]
# screens[2].groups =[2]


# Define group assignments for applications
@hook.subscribe.client_new
def assign_applications(client):
    wm_class = client.window.get_wm_class()

    if wm_class:
        wm_class = wm_class[0].lower()

        if wm_class in ["code", "steam"]:
            client.togroup("1")

        elif wm_class in ["kitty", "thunderbird"]:
            client.togroup("2")

        elif wm_class in ["discord", "slack"]:
            client.togroup("4")

        elif wm_class in ["obsidian"]:
            client.togroup("5")

        elif wm_class in ["vivaldi", "thunar"]:
            client.togroup("3")

        elif wm_class in ["1password"]:
            client.togroup("6")
        
        elif wm_class in ["java-lang-Thread"]:
            client.togroup("7")

        elif wm_class in ["figma-linux"]:
            client.togroup("8")


@lazy.function
def minimize_all(qtile):
    for win in qtile.current_group.windows:
        if hasattr(win, "toggle_minimize"):
            win.toggle_minimize()



# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ],
    border_focus = colors[6],
)

@hook.subscribe.client_new
def floating_dialogs(window):
    if "File Dialog" in window.window.get_name():
        window.floating = True
        window.place(
            x=0, y=0, width=screen.width, height=screen.height
        )
        
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = False

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser('~')
    subprocess.call([home + '/.config/qtile/autostart.sh'])
    qtile.cmd_to_screen("1", groups=["3"])

#    qtile.cmd_spawn("flatpak run com.discordapp.Discord")

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "qtile"
