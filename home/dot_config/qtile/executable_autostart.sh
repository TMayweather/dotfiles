#!/bin/bash
lxpolkit &

COLORSCHEME=Dracula 

#set background
feh --bg-fill ~/.config/wallpapers/new-zealand.jpg

# set monitors
xrandr --output HDMI-0 --primary
xrandr --output HDMI-0 --auto --output HDMI-1-2 --auto --output HDMI-1-1 --auto

xrandr --output HDMI-1-2 --left-of HDMI-0
xrandr --output HDMI-1-1 --right-of HDMI-0


