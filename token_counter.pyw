'''
    Token Counter v0.3
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
import anthropic
from transformers import AutoTokenizer, LlamaTokenizerFast, GemmaTokenizerFast, Qwen2TokenizerFast

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'tokenizer_config.json')

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
    # elif name == 'claude':
    #     return anthropic.Anthropic().get_tokenizer()
    elif name == 'llama':
        return LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")
    elif name == 'llama3':
        return AutoTokenizer.from_pretrained("Xenova/llama-3-tokenizer")
    elif name == 'gemma':
        return GemmaTokenizerFast.from_pretrained("Xenova/gemma-tokenizer")
    elif name == 'qwen':
        return Qwen2TokenizerFast.from_pretrained("Qwen/Qwen-tokenizer")
    
    raise ValueError(f"Unsupported tokenizer: {name}")

def get_available_tokenizers():
    return ['gpt-4o', 'gpt-4', 'claude', 'llama', 'llama3', 'gemma', 'qwen']


def is_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            return b'\0' in file.read(4096)
    except IOError:
        return True

def process_file(file_path, tokenizer, base_path=None):
    relative_path = os.path.relpath(file_path, base_path) if base_path else os.path.basename(file_path)
    
    if is_binary(file_path):
        return 0, [(relative_path, 'Binary')]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            tokens = len(tokenizer.encode(content))
            return tokens, [(relative_path, tokens)]
    except Exception:
        return 0, [(relative_path, 'Error')]

def count_tokens(path, tokenizer_name):
    tokenizer = get_tokenizer(tokenizer_name)
    total_tokens = 0
    file_results = []

    if os.path.isfile(path):
        tokens, results = process_file(path, tokenizer)
        total_tokens += tokens
        file_results.extend(results)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                tokens, results = process_file(file_path, tokenizer, path)
                total_tokens += tokens
                file_results.extend(results)

    return total_tokens, file_results
    

class TokenizerApp:
    def __init__(self, master, path):
        self.master = master
        self.path = path
        self.config = load_config()
        self.excluded_paths = set()  # In-memory exclusion list
        self.token_cache = {}  # Cache for token counts

        master.title("Token Counter v0.3")
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
        self.tokenizer_dropdown = ttk.Combobox(control_frame, textvariable=self.tokenizer_var, values=get_available_tokenizers())
        self.tokenizer_dropdown.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.tokenizer_dropdown.bind("<<ComboboxSelected>>", self.reset_token_counts)

        # Add Calculate Tokens button
        self.calc_button = ttk.Button(control_frame, text="Calculate Tokens", command=self.calculate_tokens)
        self.calc_button.pack(side=tk.LEFT, padx=(10, 0))

        list_frame = ttk.Frame(master)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_tree = ttk.Treeview(list_frame, yscrollcommand=scrollbar.set, columns=('Tokens',), show='tree headings')
        self.file_tree.heading('#0', text='File/Folder')
        self.file_tree.heading('Tokens', text='Tokens')
        self.file_tree.column('#0', width=330)
        self.file_tree.column('Tokens', width=50)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.file_tree.yview)
        
        # Add right-click context menu for remove
        self.menu = tk.Menu(self.master, tearoff=0)
        self.menu.add_command(label="Remove", command=self.exclude_selected_item)
        self.file_tree.bind("<Button-3>", self.show_context_menu)  # Windows/Linux
        self.file_tree.bind("<Button-2>", self.show_context_menu)  # macOS
        self.file_tree.bind("<<TreeviewOpen>>", self.on_open)
        # Remove double-click token counting logic
        # self.file_tree.bind("<Double-1>", self.on_expand)
        # self.file_tree.bind("<ButtonRelease-1>", self.on_select)
        
        self.master.update_idletasks()

        self.populate_tree_lazy('', self.path, is_root=True)
        self.reset_token_counts()

    def populate_tree_lazy(self, parent, path, is_root=False):
        # Only add the immediate children for lazy loading, and add a dummy child for expandable folders
        if os.path.isdir(path):
            if is_root:
                node_id = self.file_tree.insert(parent, 'end', text=os.path.basename(path), values=(""), open=False, tags=(path,))
            else:
                node_id = parent
            try:
                entries = [e for e in sorted(os.listdir(path)) if os.path.join(path, e) not in self.excluded_paths]
                for entry in entries:
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        child_id = self.file_tree.insert(node_id, 'end', text=entry, values=(""), tags=(full_path,))
                        # Add dummy child if this folder has children
                        try:
                            if any(os.path.join(full_path, c) not in self.excluded_paths for c in os.listdir(full_path)):
                                self.file_tree.insert(child_id, 'end')
                        except Exception:
                            pass
                    else:
                        self.file_tree.insert(node_id, 'end', text=entry, values=(""), tags=(full_path,))
            except Exception:
                pass
        else:
            if path not in self.excluded_paths:
                self.file_tree.insert(parent, 'end', text=os.path.basename(path), values=(""), tags=(path,))

    def on_open(self, event):
        # When a folder is expanded, populate its children if not already populated
        item = self.file_tree.focus()
        if not item:
            return
        path = self.file_tree.item(item, 'tags')[0]
        # If the first child is a dummy, delete it and populate real children
        children = self.file_tree.get_children(item)
        if children:
            first_child = children[0]
            if not self.file_tree.item(first_child, 'tags'):
                self.file_tree.delete(first_child)
                self.populate_tree_lazy(item, path, is_root=False)
        # After populating, update token columns from cache
        self.update_tree_tokens(item)

    def on_expand(self, event):
        # When a folder is double-clicked, expand and populate its children if not already populated
        item = self.file_tree.focus()
        if not item:
            return
        path = self.file_tree.item(item, 'tags')[0]
        if os.path.isdir(path):
            # If already populated, skip
            if self.file_tree.get_children(item):
                return
            self.populate_tree_lazy(item, path)
        # On expand or select, update token count for this node
        self.update_token_for_node(item)

    def on_select(self, event):
        # On select, update token count for the selected node
        item = self.file_tree.focus()
        if item:
            self.update_token_for_node(item)

    def update_token_for_node(self, item):
        path = self.file_tree.item(item, 'tags')[0]
        tokenizer = get_tokenizer(self.tokenizer_var.get())
        if path in self.token_cache:
            tokens = self.token_cache[path]
        else:
            tokens = self.count_tokens_path(path, tokenizer)
            self.token_cache[path] = tokens
        self.file_tree.set(item, 'Tokens', tokens)

    def count_tokens_path(self, path, tokenizer):
        # Count tokens for a file or folder, skipping excluded paths
        if path in self.excluded_paths:
            return 0
        if os.path.isfile(path):
            tokens, _ = process_file(path, tokenizer)
            return tokens
        elif os.path.isdir(path):
            total = 0
            try:
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if full_path in self.excluded_paths:
                        continue
                    total += self.count_tokens_path(full_path, tokenizer)
            except Exception:
                pass
            return total
        return 0

    def update_token_count(self, event=None):
        tokenizer_name = self.tokenizer_var.get()
        tokenizer = get_tokenizer(tokenizer_name)
        self.token_cache.clear()
        total_tokens = self.count_tokens_path(self.path, tokenizer)
        self.token_count_var.set(str(total_tokens))
        # Optionally, update visible tokens in the tree
        for item in self.file_tree.get_children():
            self.update_token_for_node(item)
        self.config['default_tokenizer'] = tokenizer_name
        save_config(self.config)

    def reset_token_counts(self, event=None):
        self.token_count_var.set('')
        self.token_cache.clear()
        # Clear tree and repopulate
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.populate_tree_lazy('', self.path, is_root=True)
        # Clear token counts in the tree
        def clear_tokens(item):
            self.file_tree.set(item, 'Tokens', '')
            for child in self.file_tree.get_children(item):
                clear_tokens(child)
        for item in self.file_tree.get_children():
            clear_tokens(item)
        self.config['default_tokenizer'] = self.tokenizer_var.get()
        save_config(self.config)

    def calculate_tokens(self):
        tokenizer_name = self.tokenizer_var.get()
        tokenizer = get_tokenizer(tokenizer_name)
        self.token_cache.clear()
        # Recursively traverse the filesystem for all non-excluded files/folders
        def count_tokens_path(path):
            if path in self.excluded_paths:
                return 0
            if os.path.isfile(path):
                tokens, _ = process_file(path, tokenizer)
                self.token_cache[path] = tokens
                return tokens
            elif os.path.isdir(path):
                subtotal = 0
                try:
                    for entry in os.listdir(path):
                        full_path = os.path.join(path, entry)
                        subtotal += count_tokens_path(full_path)
                except Exception:
                    pass
                self.token_cache[path] = subtotal
                return subtotal
            return 0
        total_tokens = count_tokens_path(self.path)
        self.token_count_var.set(str(total_tokens))
        # Update visible tree nodes' token columns
        for item in self.file_tree.get_children():
            self.update_tree_tokens(item)
        self.config['default_tokenizer'] = tokenizer_name
        save_config(self.config)

    def show_context_menu(self, event):
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def exclude_selected_item(self):
        selected = self.file_tree.selection()
        if not selected:
            return
        item = selected[0]
        tags = self.file_tree.item(item, 'tags')
        if not tags:
            return
        path = tags[0]
        self.excluded_paths.add(path)
        # Remove from tree
        self.file_tree.delete(item)
        # Do NOT update token count here; only update when Calculate Tokens is pressed

    def copy_to_clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.token_count_var.get())

    def update_tree_tokens(self, item):
        tags = self.file_tree.item(item, 'tags')
        if not tags:
            return
        path = tags[0]
        tokens = self.token_cache.get(path, '')
        self.file_tree.set(item, 'Tokens', tokens)
        for child in self.file_tree.get_children(item):
            self.update_tree_tokens(child)

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
    
