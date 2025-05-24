import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
import os
import re

from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

icon_url = "https://docs.solislang.org/Black%20Swav%20Folder%20Logo%20(1).png"
icon_path = "icon.png"
if not os.path.exists(icon_path):
    try:
        import requests
        r = requests.get(icon_url)
        with open(icon_path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        print("Could not download icon:", e)

root = tk.Tk()
root.title("Untitled - Code Editor")
root.geometry("1100x770")
root.minsize(740, 500)

try:
    icon_img = tk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon_img)
except Exception as e:
    print("Couldn't load icon:", e)

catppuccin = {
    "Mocha": {
        "BG_COLOR": "#1e1e2e",
        "LN_BG": "#181825",
        "FG_COLOR": "#cdd6f4",
        "LN_FG": "#7f849c",
        "SELECT_BG": "#585b70",
        "CURSOR_COLOR": "#f5e0dc",
        "MENU_BG": "#181825",
        "MENU_FG": "#cdd6f4",
        "SCROLLBAR_BG": "#181825",
        "SCROLLBAR_FG": "#585b70",
        "TREE_BG": "#181825",
        "TREE_FG": "#cdd6f4",
        "TREE_SEL_BG": "#585b70",
        "TREE_SEL_FG": "#cdd6f4",
        Token.Keyword: "#cba6f7",
        Token.Name.Builtin: "#f38ba8",
        Token.Name.Function: "#89b4fa",
        Token.Name.Class: "#94e2d5",
        Token.Name.Decorator: "#f9e2af",
        Token.Name.Constant: "#89dceb",
        Token.Name.Namespace: "#94e2d5",
        Token.Name.Exception: "#f38ba8",
        Token.Name.Attribute: "#f9e2af",
        Token.Name.Label: "#cba6f7",
        Token.Name.Tag: "#b4befe",
        Token.Name.Variable: "#f5e0dc",
        Token.Literal.Number: "#fab387",
        Token.Literal.String: "#a6e3a1",
        Token.String: "#a6e3a1",
        Token.Operator: "#f9e2af",
        Token.Punctuation: "#cdd6f4",
        Token.Comment: "#6c7086",
        Token.Text: "#cdd6f4",
        "html.tag": "#b4befe",
        "html.attr": "#f9e2af",
        "html.value": "#a6e3a1",
        "html.comment": "#6c7086",
        "gdscript.keyword": "#cba6f7",
        "gdscript.builtin": "#f38ba8",
        "gdscript.function": "#89b4fa",
        "gdscript.class": "#94e2d5",
        "gdscript.constant": "#fab387",
        "gdscript.string": "#a6e3a1",
        "gdscript.number": "#fab387",
        "gdscript.comment": "#6c7086",
    },
}

current_theme = "Mocha"
current_language = "python"
current_filepath = [None]
opened_folder = [None]

LANGUAGES = {
    "Python":      ("python", ".py"),
    "GDScript":    ("gdscript", ".gd"),
    "HTML":        ("html", ".html"),
}

PYGMENTS_TAGS = [
    Token.Keyword,
    Token.Name.Builtin,
    Token.Name.Function,
    Token.Name.Class,
    Token.Name.Decorator,
    Token.Name.Constant,
    Token.Name.Namespace,
    Token.Name.Exception,
    Token.Name.Attribute,
    Token.Name.Label,
    Token.Name.Tag,
    Token.Name.Variable,
    Token.Literal.Number,
    Token.Literal.String,
    Token.String,
    Token.Operator,
    Token.Punctuation,
    Token.Comment,
    Token.Text,
]

def theme_menus_and_scrollbars(theme):
    root.option_add("*Menu.background", theme["MENU_BG"])
    root.option_add("*Menu.foreground", theme["MENU_FG"])
    root.option_add("*Menu.activeBackground", theme["SCROLLBAR_FG"])
    root.option_add("*Menu.activeForeground", theme["MENU_FG"])
    root.option_add("*Menu.relief", "flat")
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background=theme["SCROLLBAR_BG"],
        troughcolor=theme["BG_COLOR"],
        bordercolor=theme["SCROLLBAR_BG"],
        arrowcolor=theme["FG_COLOR"]
    )
    style.configure(
        "Horizontal.TScrollbar",
        gripcount=0,
        background=theme["SCROLLBAR_BG"],
        troughcolor=theme["BG_COLOR"],
        bordercolor=theme["SCROLLBAR_BG"],
        arrowcolor=theme["FG_COLOR"]
    )
    style.map(
        "TScrollbar",
        background=[("active", theme["SCROLLBAR_FG"]), ("!active", theme["SCROLLBAR_BG"])]
    )
    # File tree style
    style.configure("Custom.Treeview",
        background=theme["TREE_BG"], 
        foreground=theme["TREE_FG"], 
        fieldbackground=theme["TREE_BG"],
        bordercolor=theme["TREE_BG"],
        highlightthickness=0,
        rowheight=21,
        font=("Consolas", 11)
    )
    style.map("Custom.Treeview", background=[("selected", theme["TREE_SEL_BG"])],
                               foreground=[("selected", theme["TREE_SEL_FG"])])

def get_color(token, theme):
    while token is not Token and token is not None:
        if token in theme:
            return theme[token]
        token = token.parent
    return theme["FG_COLOR"]

def apply_theme(theme_name):
    global current_theme
    theme = catppuccin[theme_name]
    current_theme = theme_name
    theme_menus_and_scrollbars(theme)
    root.configure(bg=theme["BG_COLOR"])
    main_frame.config(bg=theme["BG_COLOR"])
    text.config(
        bg=theme["BG_COLOR"],
        fg=theme["FG_COLOR"],
        insertbackground=theme["CURSOR_COLOR"],
        selectbackground=theme["SELECT_BG"],
        selectforeground=theme["FG_COLOR"],
        xscrollcommand=hscroll.set,
        yscrollcommand=lambda *args: (line_numbers.yview_moveto(text.yview()[0]), vscroll.set(*args))
    )
    line_numbers.config(
        bg=theme["LN_BG"],
        fg=theme["LN_FG"],
        font=line_number_font
    )
    explorer_frame.config(bg=theme["TREE_BG"])
    open_btn.config(bg=theme["TREE_BG"], fg=theme["TREE_FG"], activebackground=theme["TREE_SEL_BG"], bd=0, relief="flat")
    collapse_btn.config(bg=theme["TREE_BG"], fg=theme["TREE_FG"], activebackground=theme["TREE_SEL_BG"], bd=0, relief="flat")
    reopen_btn.config(bg=theme["TREE_BG"], fg=theme["TREE_FG"], activebackground=theme["TREE_SEL_BG"], bd=0, relief="flat")
    filetree.config(style="Custom.Treeview")
    menubar.config(bg=theme["MENU_BG"], fg=theme["MENU_FG"])
    filemenu.config(bg=theme["MENU_BG"], fg=theme["MENU_FG"])
    thememenu.config(bg=theme["MENU_BG"], fg=theme["MENU_FG"])
    langmenu.config(bg=theme["MENU_BG"], fg=theme["MENU_FG"])
    for tag in PYGMENTS_TAGS:
        color = get_color(tag, theme)
        text.tag_configure(str(tag), foreground=color)
    text.tag_configure("html.tag", foreground=theme["html.tag"])
    text.tag_configure("html.attr", foreground=theme["html.attr"])
    text.tag_configure("html.value", foreground=theme["html.value"])
    text.tag_configure("html.comment", foreground=theme["html.comment"])
    text.tag_configure("gdscript.keyword", foreground=theme["gdscript.keyword"])
    text.tag_configure("gdscript.builtin", foreground=theme["gdscript.builtin"])
    text.tag_configure("gdscript.function", foreground=theme["gdscript.function"])
    text.tag_configure("gdscript.class", foreground=theme["gdscript.class"])
    text.tag_configure("gdscript.constant", foreground=theme["gdscript.constant"])
    text.tag_configure("gdscript.string", foreground=theme["gdscript.string"])
    text.tag_configure("gdscript.number", foreground=theme["gdscript.number"])
    text.tag_configure("gdscript.comment", foreground=theme["gdscript.comment"])
    highlight_all()

code_font = font.Font(family="Consolas", size=12)
line_number_font = font.Font(family="Consolas", size=12)
font_size = [12]

def set_font_size(new_size):
    font_size[0] = max(6, min(new_size, 60))
    code_font.configure(size=font_size[0])
    line_number_font.configure(size=font_size[0])
    text.configure(font=code_font)
    line_numbers.configure(font=line_number_font)
    update_line_numbers()

def zoom(event):
    if getattr(event, 'state', 0) & 0x0004:
        delta = 1 if getattr(event, "delta", 0) > 0 or getattr(event, "num", None) == 4 else -1
        set_font_size(font_size[0] + delta)
        return "break"

def zoom_in(event=None): set_font_size(font_size[0] + 1)
def zoom_out(event=None): set_font_size(font_size[0] - 1)
def zoom_reset(event=None): set_font_size(12)

explorer_width = 190
explorer_frame = tk.Frame(root, width=explorer_width, bg=catppuccin[current_theme]["TREE_BG"])
explorer_frame.pack(side="left", fill="y")
explorer_frame.pack_propagate(False)

collapse_btn = tk.Button(explorer_frame, text="⮜", width=2, command=lambda: toggle_explorer(), relief="flat", bd=0,
                         font=("Segoe UI", 10), bg=catppuccin[current_theme]["TREE_BG"], fg=catppuccin[current_theme]["TREE_FG"],
                         activebackground=catppuccin[current_theme]["TREE_SEL_BG"], highlightthickness=0)
collapse_btn.pack(side="top", anchor="w", padx=3, pady=(5,0))

open_btn = tk.Button(explorer_frame, text="Open Folder", command=lambda: open_folder_dialog(),
                     relief="flat", font=("Consolas", 11),
                     bg=catppuccin[current_theme]["TREE_BG"], fg=catppuccin[current_theme]["TREE_FG"],
                     activebackground=catppuccin[current_theme]["TREE_SEL_BG"], bd=0, highlightthickness=0)
open_btn.pack(side="top", anchor="w", padx=8, pady=(4,4))

tree_scroll = ttk.Scrollbar(explorer_frame, orient="vertical")
filetree = ttk.Treeview(explorer_frame, yscrollcommand=tree_scroll.set, selectmode="browse", style="Custom.Treeview")
tree_scroll.config(command=filetree.yview)
tree_scroll.pack(side="right", fill="y")
filetree.pack(side="left", fill="both", expand=True, padx=(2,0), pady=(0,0))
tree_scroll.lift(filetree)

def open_folder_dialog():
    folder = filedialog.askdirectory()
    if folder:
        opened_folder[0] = folder
        load_tree(folder)

def load_tree(path):
    filetree.delete(*filetree.get_children())
    def insert_item(parent, abspath):
        name = os.path.basename(abspath)
        if os.path.isdir(abspath):
            oid = filetree.insert(parent, "end", text=name, open=False, values=[abspath])
            try:
                for child in sorted(os.listdir(abspath), key=lambda x: (not os.path.isdir(os.path.join(abspath, x)), x.lower())):
                    insert_item(oid, os.path.join(abspath, child))
            except PermissionError:
                pass
        else:
            filetree.insert(parent, "end", text=name, values=[abspath])
    insert_item("", path)

def open_tree_file(event):
    item = filetree.selection()
    if not item:
        return
    abspath = filetree.item(item, "values")[0]
    if os.path.isdir(abspath):
        filetree.item(item, open=not filetree.item(item, "open"))
    else:
        with open(abspath, "r", encoding="utf-8") as file:
            text.delete(1.0, tk.END)
            text.insert(tk.END, file.read())
        root.title(f"{abspath} - Code Editor")
        current_filepath[0] = abspath
        ext = os.path.splitext(abspath)[-1]
        for lang, (lexname, l_ext) in LANGUAGES.items():
            if l_ext == ext:
                set_language(lexname)
                break
        highlight_all()
        update_line_numbers()

filetree.bind("<Double-1>", open_tree_file)
filetree.bind("<Return>", open_tree_file)

explorer_open = [True]

def toggle_explorer():
    if explorer_open[0]:
        explorer_frame.pack_forget()
        explorer_open[0] = False
        reopen_btn.place(x=0, y=0, width=22, height=40)
    else:
        explorer_frame.pack(side="left", fill="y")
        explorer_open[0] = True
        reopen_btn.place_forget()

# This thin floating bar (left edge) re-opens explorer
reopen_btn = tk.Button(root, text="⮞", command=lambda: toggle_explorer(), bd=0, relief="flat",
                       font=("Segoe UI", 10), bg=catppuccin[current_theme]["TREE_BG"],
                       fg=catppuccin[current_theme]["TREE_FG"], activebackground=catppuccin[current_theme]["TREE_SEL_BG"],
                       highlightthickness=0)
reopen_btn.place_forget()

main_frame = tk.Frame(root, bg=catppuccin[current_theme]["BG_COLOR"])
main_frame.pack(side="left", fill="both", expand=True)

line_numbers = tk.Text(
    main_frame, width=6, padx=4, takefocus=0, border=0,
    background=catppuccin[current_theme]["LN_BG"],
    foreground=catppuccin[current_theme]["LN_FG"],
    font=line_number_font,
    state="disabled",
    highlightthickness=0,
    wrap="none"
)
line_numbers.pack(side="left", fill="y")

text_frame = tk.Frame(main_frame, bg=catppuccin[current_theme]["BG_COLOR"])
text_frame.pack(side="right", fill="both", expand=1)
text = tk.Text(
    text_frame,
    undo=True,
    wrap="none",
    font=code_font,
    borderwidth=0,
    relief="flat"
)
text.pack(fill="both", expand=1, padx=0, pady=0)
text.config(highlightthickness=0)

vscroll = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
vscroll.pack(side="right", fill="y")
hscroll = ttk.Scrollbar(text_frame, orient="horizontal", command=text.xview)
hscroll.pack(side="bottom", fill="x")
text.config(yscrollcommand=lambda *args: (line_numbers.yview_moveto(text.yview()[0]), vscroll.set(*args)),
            xscrollcommand=hscroll.set)

def always_focus_code(event=None):
    text.focus_set()
for widget in (root, text, line_numbers, vscroll, hscroll):
    widget.bind("<FocusIn>", always_focus_code)
for seq in ("<ButtonRelease-1>", "<Button-1>", "<KeyRelease>", "<Key>", "<Configure>"):
    text.bind(seq, always_focus_code)

def ignore_event(event):
    text.focus_set()
    return "break"
for seq in ("<Button-1>", "<B1-Motion>", "<MouseWheel>", "<Key>", "<Button-4>", "<Button-5>", "<Shift-MouseWheel>"):
    line_numbers.bind(seq, ignore_event)

def update_line_numbers(event=None):
    code = text.get("1.0", tk.END)
    lines = code.count('\n')
    numbers = "\n".join(str(i+1) for i in range(lines))
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)
    line_numbers.insert("1.0", numbers)
    line_numbers.config(state="disabled")
    line_numbers.yview_moveto(text.yview()[0])

text.bind("<KeyRelease>", lambda e: (highlight_all(), update_line_numbers()))
text.bind("<MouseWheel>", lambda e: update_line_numbers())
text.bind("<Button-1>", lambda e: (highlight_all(), update_line_numbers()))
text.bind("<Configure>", lambda e: update_line_numbers())

def on_tab(event):
    try:
        sel_start = text.index("sel.first")
        sel_end = text.index("sel.last")
        start_line = int(sel_start.split('.')[0])
        end_line = int(sel_end.split('.')[0])
        if text.compare(f"{end_line}.0", "==", sel_end):
            end_line -= 1
        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            text.insert(line_start, "    ")
        text.focus_set()
        return "break"
    except tk.TclError:
        text.insert(tk.INSERT, "    ")
        text.focus_set()
        return "break"

def on_shift_tab(event):
    try:
        sel_start = text.index("sel.first")
        sel_end = text.index("sel.last")
        start_line = int(sel_start.split('.')[0])
        end_line = int(sel_end.split('.')[0])
        if text.compare(f"{end_line}.0", "==", sel_end):
            end_line -= 1
        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            line_end = f"{line}.end"
            line_text = text.get(line_start, line_end)
            if line_text.startswith("    "):
                text.delete(line_start, f"{line_start}+4c")
            elif line_text.startswith("\t"):
                text.delete(line_start, f"{line_start}+1c")
        text.focus_set()
        return "break"
    except tk.TclError:
        text.focus_set()
        return "break"

text.bind("<Tab>", on_tab)
text.bind("<Shift-Tab>", on_shift_tab)

def is_auto_indent_language():
    return current_language in ("python", "gdscript", "javascript")

def auto_indent(event):
    cursor_index = text.index(tk.INSERT)
    current_line = int(cursor_index.split('.')[0])
    prev_line_idx = f"{current_line - 1}.0"
    prev_line = text.get(prev_line_idx, f"{prev_line_idx} lineend")
    indent = ""
    for c in prev_line:
        if c in (" ", "\t"):
            indent += c
        else:
            break
    extra_indent = ""
    if is_auto_indent_language():
        if prev_line.rstrip().endswith(":"):
            extra_indent = "    "
    text.insert(tk.INSERT, "\n" + indent + extra_indent)
    text.focus_set()
    return "break"

text.bind("<Return>", auto_indent)

def html_auto_close_tag(event):
    if current_language != "html":
        return
    cursor = text.index(tk.INSERT)
    prev = text.get(f"{cursor} -2c", cursor)
    if prev.endswith("<"):
        return
    match = re.match(r"<([a-zA-Z][\w\-]*)>$", text.get(f"{cursor} linestart", cursor))
    if match:
        tag = match.group(1)
        text.insert(cursor, f"</{tag}>")
        text.mark_set(tk.INSERT, cursor)
    else:
        last_tag = None
        line = text.get(f"{cursor} linestart", cursor)
        tag_match = re.findall(r"<([a-zA-Z][\w\-]*)[^>]*?>", line)
        if tag_match:
            last_tag = tag_match[-1]
        if prev == "</" and last_tag:
            text.insert(cursor, f"{last_tag}>")
            text.mark_set(tk.INSERT, cursor)
    return

text.bind(">", html_auto_close_tag)

text.bind("<Control-MouseWheel>", zoom)
text.bind("<Control-Button-4>", zoom)
text.bind("<Control-Button-5>", zoom)
text.bind("<Control-Shift-MouseWheel>", zoom)
text.bind("<Control-plus>", zoom_in)
text.bind("<Control-minus>", zoom_out)
text.bind("<Control-0>", zoom_reset)

def save_shortcut(event=None):
    save_file()
    return "break"
root.bind_all("<Control-s>", save_shortcut)
root.bind_all("<Command-s>", save_shortcut)

menubar = tk.Menu(root, bg=catppuccin[current_theme]["MENU_BG"], fg=catppuccin[current_theme]["MENU_FG"])
filemenu = tk.Menu(menubar, tearoff=0, bg=catppuccin[current_theme]["MENU_BG"], fg=catppuccin[current_theme]["MENU_FG"])
thememenu = tk.Menu(menubar, tearoff=0, bg=catppuccin[current_theme]["MENU_BG"], fg=catppuccin[current_theme]["MENU_FG"])
langmenu = tk.Menu(menubar, tearoff=0, bg=catppuccin[current_theme]["MENU_BG"], fg=catppuccin[current_theme]["MENU_FG"])

filemenu.add_command(label="New", command=lambda: new_file())
filemenu.add_command(label="Open...", command=lambda: open_file())
filemenu.add_command(label="Open Folder...", command=open_folder_dialog)
filemenu.add_command(label="Save As...", command=lambda: save_file())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=lambda: on_exit())

for theme in catppuccin.keys():
    thememenu.add_command(label=theme, command=lambda t=theme: apply_theme(t))

for lang, (lexname, ext) in LANGUAGES.items():
    langmenu.add_command(label=lang, command=lambda l=lexname: set_language(l))

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Themes", menu=thememenu)
menubar.add_cascade(label="Languages", menu=langmenu)
root.config(menu=menubar)

def new_file():
    text.delete(1.0, tk.END)
    root.title("Untitled - Code Editor")
    current_filepath[0] = None
    highlight_all()
    update_line_numbers()

def open_file():
    filepath = filedialog.askopenfilename(
        filetypes=[("All Files", "*.*")]
    )
    if not filepath:
        return
    ext = os.path.splitext(filepath)[-1]
    for lang, (lexname, l_ext) in LANGUAGES.items():
        if l_ext == ext:
            set_language(lexname)
            break
    text.delete(1.0, tk.END)
    with open(filepath, "r", encoding="utf-8") as file:
        text.insert(tk.END, file.read())
    root.title(f"{filepath} - Code Editor")
    current_filepath[0] = filepath
    highlight_all()
    update_line_numbers()

def save_file():
    if current_filepath[0]:
        filepath = current_filepath[0]
    else:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".*",
            filetypes=[("All Files", "*.*")]
        )
        if not filepath:
            return
        current_filepath[0] = filepath
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(text.get(1.0, tk.END))
    root.title(f"{filepath} - Code Editor")

def on_exit():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def highlight_all(event=None):
    for tag in text.tag_names():
        text.tag_remove(tag, "1.0", tk.END)
    code = text.get("1.0", tk.END)
    index = "1.0"

    def index_add(idx, chars):
        line, col = map(int, idx.split('.'))
        col += chars
        return f"{line}.{col}"

    theme = catppuccin[current_theme]
    if current_language == "gdscript":
        for match in re.finditer(r'#.*', code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("gdscript.comment", start, end)
        for match in re.finditer(r"('''.*?'''|\"\"\".*?\"\"\"|'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")", code, re.DOTALL):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("gdscript.string", start, end)
        for match in re.finditer(r"\b\d+(\.\d+)?\b", code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("gdscript.number", start, end)
        builtins = [
            "abs", "print", "str", "int", "float", "get_node", "queue_free", "get_tree", "yield", "await", "extends",
            "setget", "assert", "pass", "break", "continue", "is_instance_valid", "preload", "load", "range", "len"
        ]
        builtins_re = r"\b(" + "|".join(map(re.escape, builtins)) + r")\b"
        for match in re.finditer(builtins_re, code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("gdscript.builtin", start, end)
        keywords = [
            "func", "var", "const", "enum", "class", "static", "extends", "onready", "export", "signal",
            "if", "elif", "else", "for", "while", "match", "in", "not", "and", "or", "return", "pass", "break", "continue",
            "true", "false", "null", "self", "tool", "remote", "master", "puppet", "remotesync", "mastersync", "puppetsync", "await"
        ]
        kw_re = r"\b(" + "|".join(keywords) + r")\b"
        for match in re.finditer(kw_re, code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("gdscript.keyword", start, end)
        for match in re.finditer(r"\bfunc\s+(\w+)", code):
            start = "1.0 + {}c".format(match.start(1))
            end = "1.0 + {}c".format(match.end(1))
            text.tag_add("gdscript.function", start, end)
        for match in re.finditer(r"\bclass\s+(\w+)", code):
            start = "1.0 + {}c".format(match.start(1))
            end = "1.0 + {}c".format(match.end(1))
            text.tag_add("gdscript.class", start, end)
        for match in re.finditer(r"\b[A-Z_]{2,}\b", code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("gdscript.constant", start, end)
    elif current_language == "html":
        for match in re.finditer(r"<!--.*?-->", code, re.DOTALL):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("html.comment", start, end)
        for match in re.finditer(r"</?([a-zA-Z0-9\-]+)", code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("html.tag", start, end)
        for match in re.finditer(r"\s([a-zA-Z\-:]+)=", code):
            start = "1.0 + {}c".format(match.start(1))
            end = "1.0 + {}c".format(match.end(1))
            text.tag_add("html.attr", start, end)
        for match in re.finditer(r"=['\"](.*?)['\"]", code):
            start = "1.0 + {}c".format(match.start())
            end = "1.0 + {}c".format(match.end())
            text.tag_add("html.value", start, end)
        try:
            lexer = get_lexer_by_name("html")
        except Exception:
            lexer = get_lexer_by_name("python")
        pyg_index = "1.0"
        for ttype, value in lex(code, lexer):
            if value == '\n':
                line, col = map(int, pyg_index.split('.'))
                pyg_index = f"{line+1}.0"
                continue
            length = len(value)
            next_index = index_add(pyg_index, length)
            t = ttype
            while t is not Token and t is not None:
                if t in theme:
                    text.tag_add(str(t), pyg_index, next_index)
                    break
                t = t.parent
            pyg_index = next_index
    else:
        try:
            lexer = get_lexer_by_name(current_language)
        except Exception:
            lexer = get_lexer_by_name("python")
        for ttype, value in lex(code, lexer):
            if value == '\n':
                line, col = map(int, index.split('.'))
                index = f"{line+1}.0"
                continue
            length = len(value)
            next_index = index_add(index, length)
            t = ttype
            while t is not Token and t is not None:
                if t in theme:
                    text.tag_add(str(t), index, next_index)
                    break
                t = t.parent
            index = next_index

def set_language(lexname):
    global current_language
    current_language = lexname
    highlight_all()

root.protocol("WM_DELETE_WINDOW", on_exit)

apply_theme(current_theme)
set_language(current_language)
highlight_all()
update_line_numbers()

root.mainloop()
