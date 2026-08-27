import subprocess
import time
import threading

import requests
import pyperclip
from pynput import keyboard
from config import MODEL, TOGGLE_HOTKEY

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT_TEMPLATE = """Translate the French input into natural English. Translate the sentence as a whole — do not summarize, interpret, or explain its meaning. Output ONLY the English translation, nothing else.

Watch for reflexive verbs (se plaire, se lever, s'appeler, etc.) — translate them as their actual English meaning, not word-by-word.

Examples:
input: hier
output: yesterday

input: aujourd'hui
output: today

input: Tu te plais ici.
output: You like it here.

input: Elle s'appelle Marie.
output: Her name is Marie.

input: Il se lève tôt.
output: He gets up early.

input: {anstext}
output:"""


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