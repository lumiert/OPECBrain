import os
import time
import threading
from typing import Optional

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

import keyboard

from addbar import show_addbar
from history import show_history, stop_all_windows
"""Deprecated tray manager; replaced by Qt TrayApp in qt_app.py"""

