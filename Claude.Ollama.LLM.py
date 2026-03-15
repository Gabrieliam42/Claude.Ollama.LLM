# Script Developer: Gabriel Mihai Sandu
# GitHub Profile: https://github.com/Gabrieliam42

import ctypes
import os
import re
import subprocess
import sys
import time

from ollama_path import resolve_ollama_executable

PREFERRED_MODELS = (
    "glm-4.7-flash:latest",
    "glm-4.7-flash:q8_0",
    "gpt-oss-20b:latest",
    "gpt-oss:20b",
    "qwen3-coder:latest",
    "devstral-small-2:24b",
    "devstral:24b",
    "qwen3.5:9b",
    "mistral-nemo:12b-instruct-2407-q8_0",
    "mistral-small:22b-instruct-2409-q6_K",
)


def run_as_admin(file_path, parameters=None, show_cmd=0):
    try:
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", file_path, parameters, None, show_cmd
        )
        return int(result) > 32
    except Exception:
        return False


def isolate_tk_environment():
    # PyInstaller injects Tcl/Tk env vars for the bundled runtime.
    if getattr(sys, "frozen", False):
        return

    for variable_name in ("TCL_LIBRARY", "TK_LIBRARY", "TCLLIBPATH"):
        os.environ.pop(variable_name, None)


def should_replace_model(existing_model, candidate_model, preferred_order):
    existing_is_latest = existing_model["name"].endswith(":latest")
    candidate_is_latest = candidate_model["name"].endswith(":latest")
    if candidate_is_latest != existing_is_latest:
        return candidate_is_latest

    existing_priority = preferred_order.get(existing_model["name"], len(preferred_order))
    candidate_priority = preferred_order.get(
        candidate_model["name"], len(preferred_order)
    )
    if candidate_priority != existing_priority:
        return candidate_priority < existing_priority

    return False


def model_supports_tools(ollama_executable, model_name):
    result = subprocess.run(
        [ollama_executable, "show", model_name, "-v"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    in_capabilities = False
    for line in result.stdout.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue

        if line.startswith("  ") and not line.startswith("    "):
            if stripped_line == "Capabilities":
                in_capabilities = True
                continue

            if in_capabilities:
                break

        if in_capabilities and stripped_line == "tools":
            return True

    return False


def get_available_models(ollama_executable):
    result = subprocess.run(
        [ollama_executable, "list"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )

    preferred_order = {
        model_name: index for index, model_name in enumerate(PREFERRED_MODELS)
    }
    models = []
    seen_names = set()
    seen_ids = {}
    for line in result.stdout.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue

        columns = re.split(r"\s{2,}", stripped_line)
        if not columns or columns[0] == "NAME":
            continue

        model_name = columns[0]
        if model_name in seen_names:
            continue

        if not model_supports_tools(ollama_executable, model_name):
            seen_names.add(model_name)
            continue

        model_id = columns[1] if len(columns) >= 2 else ""
        model_size = columns[2] if len(columns) >= 3 else ""
        model_entry = {
            "id": model_id,
            "name": model_name,
            "size": model_size,
            "display": f"{model_name}  [{model_size}]" if model_size else model_name,
        }

        if model_id and model_id in seen_ids:
            existing_index = seen_ids[model_id]
            if should_replace_model(models[existing_index], model_entry, preferred_order):
                models[existing_index] = model_entry
            seen_names.add(model_name)
            continue

        models.append(model_entry)
        seen_names.add(model_name)
        if model_id:
            seen_ids[model_id] = len(models) - 1

    if not models:
        raise RuntimeError("No Ollama models with tool support were found.")

    models.sort(
        key=lambda model: (
            0 if model["name"] in preferred_order else 1,
            preferred_order.get(model["name"], 0),
        )
    )

    return models


def prompt_for_model(model_entries):
    isolate_tk_environment()
    import tkinter as tk

    root = tk.Tk()
    root.title("Claude Model")
    root.configure(bg="#2b2b2b")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    model_name = None
    message_var = tk.StringVar(
        value="Select the Ollama model to use with `claude --model`:"
    )

    def submit(event=None):
        nonlocal model_name
        selection = listbox.curselection()
        if not selection:
            message_var.set("Select a model.")
            return
        model_name = model_entries[selection[0]]["name"]
        root.destroy()

    def cancel(event=None):
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", cancel)
    root.bind("<Return>", submit)
    root.bind("<Escape>", cancel)

    frame = tk.Frame(root, bg="#2b2b2b", padx=18, pady=18)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        textvariable=message_var,
        bg="#2b2b2b",
        fg="#ffffff",
        justify="left",
        wraplength=420,
    ).pack(anchor="w")

    list_frame = tk.Frame(
        frame,
        bg="#1f1f1f",
        highlightthickness=1,
        highlightbackground="#4a4a4a",
        highlightcolor="#7a7a7a",
    )
    list_frame.pack(fill="both", expand=True, pady=(12, 16))

    scrollbar = tk.Scrollbar(
        list_frame,
        bg="#2b2b2b",
        activebackground="#4a4a4a",
        troughcolor="#1f1f1f",
        relief="flat",
    )
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(
        list_frame,
        bg="#1f1f1f",
        fg="#ffffff",
        selectbackground="#4a4a4a",
        selectforeground="#ffffff",
        highlightthickness=0,
        activestyle="none",
        relief="flat",
        font=("Consolas", 10),
        width=60,
        height=min(max(len(model_entries), 6), 14),
        yscrollcommand=scrollbar.set,
    )
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    for model_entry in model_entries:
        listbox.insert("end", model_entry["display"])

    if model_entries:
        listbox.selection_set(0)
        listbox.activate(0)
        listbox.see(0)

    listbox.bind("<Double-Button-1>", submit)

    button_frame = tk.Frame(frame, bg="#2b2b2b")
    button_frame.pack(anchor="e")

    tk.Button(
        button_frame,
        text="Cancel",
        command=cancel,
        bg="#3a3a3a",
        fg="#ffffff",
        activebackground="#4a4a4a",
        activeforeground="#ffffff",
        relief="flat",
        bd=0,
        padx=14,
        pady=6,
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        button_frame,
        text="OK",
        command=submit,
        bg="#4a4a4a",
        fg="#ffffff",
        activebackground="#5a5a5a",
        activeforeground="#ffffff",
        relief="flat",
        bd=0,
        padx=18,
        pady=6,
    ).pack(side="left")

    root.update_idletasks()
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    root.geometry(f"+{position_x}+{position_y}")
    listbox.focus_set()

    root.mainloop()

    if not model_name or not model_name.strip():
        raise RuntimeError("No model was provided.")

    return model_name.strip()


if __name__ == "__main__":
    ollama_executable = resolve_ollama_executable()

    if not run_as_admin(ollama_executable, "serve"):
        raise RuntimeError("Failed to launch Ollama as administrator.")

    time.sleep(10)
    model_entries = get_available_models(ollama_executable)
    model_name = prompt_for_model(model_entries)
    env = os.environ.copy()
    env["OLLAMA_CLAUDE_MODEL"] = model_name

    subprocess.run(
        [
            "pwsh.exe",
            "-NoProfile",
            "-Command",
            '$env:ANTHROPIC_BASE_URL = "http://localhost:11434"; '
            '$env:ANTHROPIC_AUTH_TOKEN = "ollama"; '
            '$env:ANTHROPIC_API_KEY = ""; '
            'claude --model $env:OLLAMA_CLAUDE_MODEL',
        ],
        check=True,
        env=env,
    )
