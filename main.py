import subprocess
import time
import threading

import requests
import pyperclip
from pynput import keyboard
from config import MODEL, TOGGLE_HOTKEY

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_TEMPLATE = """Explain this in the fewest words possible. No intro, no labels, no restarting the input, just the meaning,
- if it's a word: give its meaning in fewest words.
- if it's a sentence: give the fist in one short line.
- if it's code: say what it does in one short phrase.
- if it's any other language: translate it into English.
input: {anstext}
Answer:
"""



active = False
last_clipboard = ""


def notify(title, message):
    message = message.replace('\\', '\\\\').replace('"', '\\"')
    title = title.replace('\\', '\\\\').replace('"', '\\"')
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])


def ask_ollama(text: str):
    prompt = PROMPT_TEMPLATE.format(anstext=text[:2000])
    try:
        resp = requests.post( 
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Is it running?"
    except Exception as e:
        return f"Error: {e}"


def clipboard_watcher():
    global last_clipboard
    while True:
        if active:
            try:
                current = pyperclip.paste()
            except Exception:
                current = ""

            if current and current != last_clipboard:
                last_clipboard = current
                explanation = ask_ollama(current)
                notify("Explanation", explanation)
        time.sleep(1)


def toggle_active():
    global active, last_clipboard
    active = not active
    if active:
        last_clipboard = pyperclip.paste()
        notify("Clipboard Explanation", "Activated")
    else:
        notify("Clipboard Explanation", "Deactivated")


def main():
    threading.Thread(target=clipboard_watcher, daemon=True).start()

    hotkey = keyboard.GlobalHotKeys({TOGGLE_HOTKEY: toggle_active})
    hotkey.start()

    print(f"Running. Press {TOGGLE_HOTKEY} to toggle.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()