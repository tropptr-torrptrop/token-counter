'''
    Token Counter v0.1
    Copyright (C) 2024  NickNau
    
    https://github.com/tropptr-torrptrop/token-counter

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


import tkinter as tk
from tkinter import ttk
import os
import sys
import json
from pathlib import Path
import tiktoken
from transformers import AutoTokenizer
from transformers import LlamaTokenizerFast
from transformers import GemmaTokenizerFast
from transformers import Qwen2TokenizerFast
import anthropic

CONFIG_FILE = 'tokenizer_config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        default_config = {'default_tokenizer': 'gpt-4'}
        save_config(default_config)
        return default_config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def get_tokenizer(name):
    if name.startswith('gpt'):
        return tiktoken.encoding_for_model(name)
    elif name == 'claude':
        return anthropic.Anthropic().get_tokenizer()
    elif name == 'llama':
        return LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")
    elif name == 'llama3':
        return AutoTokenizer.from_pretrained("Xenova/llama-3-tokenizer")
    elif name == 'gemma':
        return GemmaTokenizerFast.from_pretrained("Xenova/gemma-tokenizer")
    elif name == 'qwen':
        return Qwen2TokenizerFast.from_pretrained("Qwen/Qwen-tokenizer")
    else:
        raise ValueError(f"Unsupported tokenizer: {name}")

def is_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            return b'\0' in file.read(4096)
    except IOError:
        return True

def count_tokens(path, tokenizer_name):
    tokenizer = get_tokenizer(tokenizer_name)
    total_tokens = 0
    file_results = []

    if os.path.isfile(path):
        if is_binary(path):
            file_results.append((os.path.basename(path), 'Binary'))
        else:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    tokens = len(tokenizer.encode(content))
                    total_tokens = tokens
                    file_results.append((os.path.basename(path), tokens))
            except Exception:
                file_results.append((os.path.basename(path), 'Error'))
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, path)
                if is_binary(file_path):
                    file_results.append((relative_path, 'Binary'))
                else:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            tokens = len(tokenizer.encode(content))
                            total_tokens += tokens
                            file_results.append((relative_path, tokens))
                    except Exception:
                        file_results.append((relative_path, 'Error'))

    return total_tokens, file_results

class TokenizerApp:
    def __init__(self, master, path):
        self.master = master
        self.path = path
        self.config = load_config()

        master.title("Token Counter v0.1")
        x = (self.master.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.master.winfo_screenheight() // 2) - (300 // 2)
        self.master.geometry('500x300+{}+{}'.format(x, y))
        
        self.master.update_idletasks()

        self.token_count_var = tk.StringVar()
        self.token_count_entry = ttk.Entry(master, textvariable=self.token_count_var, font=("Arial", 20), justify='center')
        self.token_count_entry.pack(pady=20, padx=20, fill=tk.X)

        control_frame = ttk.Frame(master)
        control_frame.pack(pady=5, padx=20, fill=tk.X)

        self.copy_button = ttk.Button(control_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))

        self.tokenizer_var = tk.StringVar(value=self.config['default_tokenizer'])
        self.tokenizer_dropdown = ttk.Combobox(control_frame, textvariable=self.tokenizer_var, values=self.get_available_tokenizers())
        self.tokenizer_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.tokenizer_dropdown.bind("<<ComboboxSelected>>", self.update_token_count)

        list_frame = ttk.Frame(master)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_list = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set, columns=('File', 'Tokens'), show='headings')
        self.file_list.heading('File', text='File')
        self.file_list.heading('Tokens', text='Tokens')
        self.file_list.column('File', width=330)
        self.file_list.column('Tokens', width=50)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.file_list.yview)
        
        self.master.update_idletasks()

        self.update_token_count()

    def get_available_tokenizers(self):
        return ['gpt-4o', 'gpt-4', 'claude', 'llama', 'llama3', 'gemma', 'qwen']

    def update_token_count(self, event=None):
        tokenizer_name = self.tokenizer_var.get()
        token_count, file_results = count_tokens(self.path, tokenizer_name)
        self.token_count_var.set(str(token_count))

        for item in self.file_list.get_children():
            self.file_list.delete(item)

        for file_path, tokens in file_results:
            self.file_list.insert('', 'end', values=(file_path, tokens))

        self.config['default_tokenizer'] = tokenizer_name
        save_config(self.config)

    def copy_to_clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.token_count_var.get())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python token_counter.pyw <file_or_folder_path>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: The path '{path}' does not exist.")
        sys.exit(1)

    root = tk.Tk()
    app = TokenizerApp(root, path)
    root.mainloop()
    