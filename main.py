import subprocess
import time
import threading

import requests
import pyperclip 
from pynput import keyboard
from config import MODEL, TOGGLE_HOTKEY

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_TEMPLATE = """Explain this in the fewest words possible. No intro, no labels, no restarting the input, just the meaning,
- if it's a word: give its meaning in 3-6 words.
- if it's a sentence: give the fist in one short line.
- if it's code: say what it does in one short phrase.

input: {text}
Answer:
"""

active = False
last_clipboard = ""

def notification(title , meessage):
    message = message.replace('\\')
