from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox, font
from tkinter import ttk
import os
import re
import json
import sys
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

THEME_DIR = resource_path("themes")
SETTINGS_FILE = "settings.json"

def ensure_theme_dir():
    if not os.path.exists(THEME_DIR):
        os.makedirs(THEME_DIR)

def load_themes():
    ensure_theme_dir()
    themes = {}
    for fname in os.listdir(THEME_DIR):
        if fname.lower().endswith(".json"):
            with open(os.path.join(THEME_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                themes[data["name"]] = data
    return themes

def save_settings(selected_theme, font_size=13):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": selected_theme, "font_size": font_size}, f)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"theme": "Mocha", "font_size": 13}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"theme": "Mocha", "font_size": 13}

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

root = TkinterDnD.Tk()
root.title("Untitled - Solis Text Editor")
root.geometry("1100x770")
root.minsize(740, 500)

try:
    icon_img = tk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon_img)
except Exception as e:
    print("Couldn't load icon:", e)

themes = load_themes()
settings = load_settings()
current_theme_name = settings["theme"] if settings["theme"] in themes else list(themes.keys())[0]
font_size = settings.get("font_size", 13)
current_theme = themes[current_theme_name]

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
        background=theme["SCROLLBAR_BG"],
        troughcolor=theme["BG_COLOR"],
        bordercolor=theme["SCROLLBAR_BG"],
        arrowcolor=theme["FG_COLOR"],
        relief="flat",
        borderwidth=0,
        gripcount=0,
        lightcolor=theme["SCROLLBAR_BG"],
        darkcolor=theme["SCROLLBAR_BG"],
        padding=2,
        width=12
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=theme["SCROLLBAR_BG"],
        troughcolor=theme["BG_COLOR"],
        bordercolor=theme["SCROLLBAR_BG"],
        arrowcolor=theme["FG_COLOR"],
        relief="flat",
        borderwidth=0,
        gripcount=0,
        lightcolor=theme["SCROLLBAR_BG"],
        darkcolor=theme["SCROLLBAR_BG"],
        padding=2,
        width=12
    )
    style.map(
        "TScrollbar",
        background=[("active", theme["SCROLLBAR_FG"]), ("!active", theme["SCROLLBAR_BG"])]
    )
    style.configure("Custom.Treeview",
        background=theme["TREE_BG"], 
        foreground=theme["TREE_FG"], 
        fieldbackground=theme["TREE_BG"],
        bordercolor=theme["TREE_BG"],
        highlightthickness=0,
        rowheight=26,
        font=("Consolas", 12),
        padding=(6, 4)
    )
    style.map("Custom.Treeview", background=[("selected", theme["TREE_SEL_BG"])],
                               foreground=[("selected", theme["TREE_SEL_FG"])] )

def get_color(token, theme):
    while token is not Token and token is not None:
        key = str(token)
        if key in theme:
            return theme[key]
        token = token.parent
    return theme["FG_COLOR"]

def apply_theme(theme_name):
    global current_theme_name, current_theme
    theme = themes[theme_name]
    current_theme_name = theme_name
    current_theme = theme
    theme_menus_and_scrollbars(theme)
    root.configure(bg=theme["BG_COLOR"])
    main_frame.config(bg=theme["BG_COLOR"])
    if 'line_numbers' in globals() and 'text' in globals():
        line_numbers.config(
            bg=theme["LN_BG"],
            fg=theme["LN_FG"],
            font=line_number_font
        )
        text.config(
            bg=theme["BG_COLOR"],
            fg=theme["FG_COLOR"],
            insertbackground=theme["CURSOR_COLOR"],
            selectbackground=theme["SELECT_BG"],
            selectforeground=theme["FG_COLOR"],
            inactiveselectbackground=theme["SELECT_BG"],
            xscrollcommand=hscroll.set,
            yscrollcommand=lambda *args: (line_numbers.yview_moveto(text.yview()[0]), vscroll.set(*args))
        )
        # Update selection colors for all tags
        for tag in text.tag_names():
            text.tag_configure(tag, selectbackground=theme["SELECT_BG"],
                             selectforeground=theme["FG_COLOR"])
    explorer_frame.config(bg=theme["TREE_BG"])
    collapse_btn.config(bg=theme["TREE_BG"], fg=theme["TREE_FG"], activebackground=theme["TREE_SEL_BG"])
    expand_frame.config(bg=theme["TREE_BG"])
    expand_btn.config(bg=theme["TREE_BG"], fg=theme["TREE_FG"], activebackground=theme["TREE_SEL_BG"])
    open_btn.config(bg=theme["TREE_BG"], fg=theme["TREE_FG"], activebackground=theme["TREE_SEL_BG"], bd=0, relief="flat")
    filetree.config(style="Custom.Treeview")
    search_entry.config(
        bg=theme["TREE_BG"],
        fg=theme["TREE_FG"],
        insertbackground=theme["CURSOR_COLOR"],
        highlightbackground=theme["TREE_SEL_BG"],
        font=("Consolas", 11)
    )
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
    text.tag_configure("gdscript.operator", foreground=theme.get("gdscript.operator", "#f38ba8"))
    text.tag_configure("gdscript.annotation", foreground=theme.get("gdscript.annotation", "#f9e2af"))
    text.tag_configure("gdscript.type", foreground=theme.get("gdscript.type", "#cba6f7"))
    text.tag_configure("gdscript.signal", foreground=theme.get("gdscript.signal", "#a6e3a1"))
    text.tag_configure("gdscript.decorator", foreground=theme.get("gdscript.decorator", "#f9e2af"))
    text.tag_configure("gdscript.variable", foreground=theme.get("gdscript.variable", "#94e2d5"))
    text.tag_configure("gdscript.builtin_class", foreground=theme.get("gdscript.builtin_class", "#b4befe"))
    highlight_all()
    save_settings(current_theme_name, font_size)

code_font = font.Font(family="Consolas", size=font_size, weight="normal")
line_number_font = font.Font(family="Consolas", size=font_size, weight="normal")

def set_font_size(new_size):
    global font_size
    font_size = max(6, min(new_size, 60))
    code_font.configure(size=font_size)
    line_number_font.configure(size=font_size)
    text.configure(font=code_font)
    line_numbers.configure(font=line_number_font)
    update_line_numbers()
    save_settings(current_theme_name, font_size)

def zoom(event):
    if getattr(event, 'state', 0) & 0x0004:
        delta = 1 if getattr(event, "delta", 0) > 0 or getattr(event, "num", None) == 4 else -1
        set_font_size(font_size + delta)
        return "break"

def zoom_in(event=None): set_font_size(font_size + 1)
def zoom_out(event=None): set_font_size(font_size - 1)
def zoom_reset(event=None): set_font_size(13)

sidebar_collapsed = [False]

paned = tk.PanedWindow(root, orient="horizontal", sashwidth=6, sashrelief="flat", bg=current_theme["BG_COLOR"])
paned.pack(fill="both", expand=True)

explorer_frame = tk.Frame(paned, bg=current_theme["TREE_BG"], borderwidth=0, highlightthickness=0, padx=0, pady=0)

collapse_btn = tk.Button(
    explorer_frame, text="◀", command=lambda: collapse_sidebar(),
    relief="flat", font=("Consolas", 16, "bold"), bd=0, highlightthickness=0,
    bg=current_theme["TREE_BG"], fg=current_theme["TREE_FG"],
    activebackground=current_theme["TREE_SEL_BG"], padx=0, pady=0
)
collapse_btn.pack(side="left", fill="y")

expand_frame = tk.Frame(root, bg=current_theme["TREE_BG"], width=24)
expand_btn = tk.Button(
    expand_frame, text="▶", command=lambda: expand_sidebar(),
    relief="flat", font=("Consolas", 16, "bold"), bd=0, highlightthickness=0,
    bg=current_theme["TREE_BG"], fg=current_theme["TREE_FG"],
    activebackground=current_theme["TREE_SEL_BG"], padx=0, pady=0
)
expand_btn.pack(fill="both", expand=True)
expand_frame.place_forget()

def update_expand_frame_height(event=None):
    if sidebar_collapsed[0]:
        h = root.winfo_height()
        expand_frame.place(x=0, y=0, width=32, height=h)
        if 'line_numbers' in globals():
            line_numbers.pack_configure(padx=(32,0))  # Move right when collapsed
    else:
        expand_frame.place_forget()
        if 'line_numbers' in globals():
            line_numbers.pack_configure(padx=(0,0))  # Normal when expanded
root.bind("<Configure>", update_expand_frame_height)

# --- SEARCH BAR ADDED HERE ---
search_var = tk.StringVar()

# Create a frame to center the search bar and button
searchbar_frame = tk.Frame(
    explorer_frame,
    bg=current_theme["TREE_BG"],
    highlightbackground=current_theme["TREE_SEL_BG"],
    highlightthickness=0,
    bd=0
)
searchbar_frame.pack(side="top", fill="x", padx=32, pady=(18, 10))

search_entry = tk.Entry(
    searchbar_frame, textvariable=search_var,
    bg=current_theme["TREE_BG"], fg=current_theme["TREE_FG"],
    insertbackground=current_theme["CURSOR_COLOR"],
    highlightbackground=current_theme["TREE_SEL_BG"],
    highlightcolor=current_theme["TREE_SEL_BG"],
    relief="solid",
    font=("Consolas", 12),
    justify="center",
    bd=2,
    highlightthickness=1
)
search_entry.pack(side="top", fill="x", padx=6, pady=(0, 10), ipady=5)
search_entry.bind("<KeyRelease>", lambda e: search_tree())

open_btn = tk.Button(
    searchbar_frame, text="Open Folder", command=lambda: open_folder_dialog(),
    relief="flat", font=("Consolas", 11, "bold"),
    bg=current_theme["TREE_BG"], fg=current_theme["TREE_FG"],
    activebackground=current_theme["TREE_SEL_BG"], bd=0, highlightthickness=1,
    highlightbackground=current_theme["TREE_SEL_BG"],
    padx=8, pady=6,
    cursor="hand2"
)
open_btn.pack(side="top", fill="x", padx=6, pady=(0, 2))

def search_tree():
    query = search_var.get().strip().lower()
    filetree.delete(*filetree.get_children())
    if not opened_folder[0] or not os.path.exists(opened_folder[0]):
        return

    def insert_item_filtered(parent, abspath, force_open=False):
        name = os.path.basename(abspath)
        # Exclude .uid files
        if name.lower().endswith('.uid'):
            return
        match_query = query in name.lower()
        if os.path.isdir(abspath):
            children = []
            for child in sorted(os.listdir(abspath), key=lambda x: (not os.path.isdir(os.path.join(abspath, x)), x.lower())):
                children.append(os.path.join(abspath, child))
            matching_children = [c for c in children if match_query or query in os.path.basename(c).lower() or (os.path.isdir(c) and folder_contains_match(c, query))]
            if match_query or matching_children:
                # Open folder if searching and there is a match
                oid = filetree.insert(parent, "end", text=name, open=True, values=[abspath])
                for child in children:
                    if match_query or query in os.path.basename(child).lower() or (os.path.isdir(child) and folder_contains_match(child, query)):
                        insert_item_filtered(oid, child, force_open=True)
        else:
            if match_query:
                filetree.insert(parent, "end", text=name, values=[abspath])

    def folder_contains_match(folder, query):
        for root_, dirs, files in os.walk(folder):
            for f in files:
                # Exclude .uid files
                if f.lower().endswith('.uid'):
                    continue
                if query in f.lower():
                    return True
        return False

    insert_item_filtered("", opened_folder[0], force_open=True)

tree_scroll = ttk.Scrollbar(explorer_frame, orient="vertical")
filetree = ttk.Treeview(
    explorer_frame, yscrollcommand=tree_scroll.set, selectmode="browse", style="Custom.Treeview",
    show='tree', takefocus=0, padding=(4, 2)
)
tree_scroll.config(command=filetree.yview)
tree_scroll.pack(side="right", fill="y")
filetree.pack(side="left", fill="both", expand=True, padx=(2,0), pady=(0,0))
tree_scroll.lift(filetree)

main_frame = tk.Frame(paned, bg=current_theme["BG_COLOR"], borderwidth=0, highlightthickness=0)

def setup_main_frame_contents():
    for child in main_frame.winfo_children():
        child.destroy()
    global line_numbers, text, text_frame, vscroll, hscroll

    text_frame = tk.Frame(main_frame, bg=current_theme["BG_COLOR"], borderwidth=0, highlightthickness=0)
    text_frame.pack(fill="both", expand=1)

    line_numbers = tk.Text(
        text_frame, borderwidth=0, highlightthickness=0, relief='flat',
        width=5, padx=4, takefocus=0,
        background=current_theme["LN_BG"],
        foreground=current_theme["LN_FG"],
        font=line_number_font, state="disabled", wrap="none"
    )
    # Don't set padx here; handled in update_expand_frame_height
    line_numbers.pack(side="left", fill="y")

    text = tk.Text(
        text_frame, borderwidth=0, highlightthickness=0, relief='flat', insertwidth=2,
        undo=True, wrap="none", font=code_font,
        # Enable all standard bindings and selections
        exportselection=False,  # Prevent selection from being cleared when losing focus
        selectbackground=current_theme["SELECT_BG"],
        selectforeground=current_theme["FG_COLOR"],
        inactiveselectbackground=current_theme["SELECT_BG"]
    )
    text.pack(side="left", fill="both", expand=1, padx=0, pady=0)

    # Remove any existing tags that might interfere with selection
    for tag in text.tag_names():
        text.tag_configure(tag, selectbackground=current_theme["SELECT_BG"],
                         selectforeground=current_theme["FG_COLOR"])

    # Prevent focus events from clearing selection
    def keep_selection(event):
        return "break"
    
    text.bind("<FocusOut>", keep_selection)
    text.bind("<FocusIn>", keep_selection)

    # Standard selection bindings that work with arrow keys
    text.event_add('<<SelectAll>>', '<Control-a>')
    text.event_add('<<SelectPrevWord>>', '<Shift-Control-Left>')
    text.event_add('<<SelectNextWord>>', '<Shift-Control-Right>')
    text.event_add('<<SelectLineStart>>', '<Shift-Home>')
    text.event_add('<<SelectLineEnd>>', '<Shift-End>')
    text.event_add('<<SelectUp>>', '<Shift-Up>')
    text.event_add('<<SelectDown>>', '<Shift-Down>')
    text.event_add('<<SelectLeft>>', '<Shift-Left>')
    text.event_add('<<SelectRight>>', '<Shift-Right>')

    # Bind virtual events to do nothing, letting Tkinter handle them
    text.bind('<<SelectLeft>>', lambda e: None)
    text.bind('<<SelectRight>>', lambda e: None)
    text.bind('<<SelectUp>>', lambda e: None)
    text.bind('<<SelectDown>>', lambda e: None)
    text.bind('<<SelectPrevWord>>', lambda e: None)
    text.bind('<<SelectNextWord>>', lambda e: None)
    text.bind('<<SelectLineStart>>', lambda e: None)
    text.bind('<<SelectLineEnd>>', lambda e: None)
    text.bind('<<SelectAll>>', lambda e: "break")  # Special case to prevent double selection

    # Bind all shift+arrow key combinations for selection
    text.bind("<Shift-Left>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Right>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Up>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Down>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Control-Left>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Control-Right>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Control-Up>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Control-Down>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-Home>", lambda e: None)  # Let Tkinter handle it
    text.bind("<Shift-End>", lambda e: None)  # Let Tkinter handle it

    vscroll = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview, style='Vertical.TScrollbar')
    vscroll.pack(side="right", fill="y")
    hscroll = ttk.Scrollbar(root, orient="horizontal", command=text.xview, style='Horizontal.TScrollbar')
    hscroll.pack(side="bottom", fill="x")
    text.config(yscrollcommand=lambda *args: (line_numbers.yview_moveto(text.yview()[0]), vscroll.set),
                xscrollcommand=hscroll.set)

    # Don't bind <FocusIn> or <Key> to always_focus_code. Tkinter selection will now "just work".

    # Prevent line number text widget from taking focus:
    for seq in ("<Button-1>", "<B1-Motion>", "<MouseWheel>", "<Key>", "<Button-4>", "<Button-5>", "<Shift-MouseWheel>"):
        line_numbers.bind(seq, lambda e: "break")

    text.bind("<KeyRelease>", lambda e: (highlight_all(), update_line_numbers()))
    text.bind("<MouseWheel>", lambda e: update_line_numbers())
    text.bind("<Button-1>", lambda e: (highlight_all(), update_line_numbers()))
    text.bind("<Configure>", lambda e: update_line_numbers())
    text.bind("<Tab>", on_tab)
    text.bind("<Shift-Tab>", on_shift_tab)
    text.bind("<Return>", auto_indent)
    text.bind(">", html_auto_close_tag)
    text.bind("<Control-MouseWheel>", zoom)
    text.bind("<Control-Button-4>", zoom)
    text.bind("<Control-Button-5>", zoom)
    text.bind("<Control-Shift-MouseWheel>", zoom)
    text.bind("<Control-plus>", zoom_in)
    text.bind("<Control-minus>", zoom_out)
    text.bind("<Control-0>", zoom_reset)
    update_line_numbers()

def collapse_sidebar():
    if not sidebar_collapsed[0]:
        paned.forget(explorer_frame)
        sidebar_collapsed[0] = True
        update_expand_frame_height()
        if main_frame not in paned.panes():
            paned.add(main_frame)

def expand_sidebar():
    if sidebar_collapsed[0]:
        if explorer_frame not in paned.panes():
            for pane in paned.panes():
                paned.forget(pane)
            paned.add(explorer_frame, minsize=120)
            paned.add(main_frame)
        sidebar_collapsed[0] = False
        update_expand_frame_height()

def update_line_numbers(event=None):
    code = text.get("1.0", tk.END)
    lines = code.count('\n')
    numbers = "\n".join(str(i+1) for i in range(lines))
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)
    line_numbers.insert("1.0", numbers)
    line_numbers.config(state="disabled")
    line_numbers.yview_moveto(text.yview()[0])

def indent_line(line_num):
    """Helper function to indent a single line"""
    line_start = f"{line_num}.0"
    line_end = f"{line_num}.end"
    # Get current line text to check existing indentation
    line_text = text.get(line_start, line_end)
    # Calculate current indentation level
    current_indent = len(line_text) - len(line_text.lstrip())
    # Insert indentation at the start of the line
    text.insert(f"{line_num}.{current_indent}", "    ")
    return 4  # Return number of spaces added

def unindent_line(line_num):
    """Helper function to unindent a single line"""
    line_start = f"{line_num}.0"
    line_text = text.get(line_start, f"{line_num}.end")
    if line_text.startswith("    "):  # Exactly 4 spaces
        text.delete(line_start, f"{line_num}.4")
        return 4
    elif line_text.startswith("\t"):  # Tab character
        text.delete(line_start, f"{line_num}.1")
        return 1
    elif line_text.startswith(" "):  # Less than 4 spaces
        # Count leading spaces
        spaces = 0
        for char in line_text:
            if char == " ":
                spaces += 1
            else:
                break
        if spaces > 0:
            text.delete(line_start, f"{line_num}.{spaces}")
            return spaces
    return 0

def deindent_line(line_num):
    """Helper function to deindent a single line"""
    line_start = f"{line_num}.0"
    line_end = f"{line_num}.end"
    line_text = text.get(line_start, line_end)
    
    # Calculate current indentation level
    current_indent = len(line_text) - len(line_text.lstrip())
    
    if current_indent >= 4:
        # Remove up to 4 spaces from the beginning
        text.delete(f"{line_num}.0", f"{line_num}.4")
        return -4
    elif current_indent > 0:
        # Remove all existing indentation
        text.delete(f"{line_num}.0", f"{line_num}.{current_indent}")
        return -current_indent
    return 0

def on_tab(event):
    try:
        # Get selection bounds
        sel_start = text.index("sel.first")
        sel_end = text.index("sel.last")
        
        # Parse line and column numbers
        start_line = int(sel_start.split('.')[0])
        end_line = int(sel_end.split('.')[0])
        start_col = int(sel_start.split('.')[1])
        end_col = int(sel_end.split('.')[1])
        
        # Store original cursor position
        cursor_pos = text.index(tk.INSERT)
        
        # Check if selection ends at the start of a line
        selection_ends_at_line_start = end_col == 0
        if selection_ends_at_line_start and start_line != end_line:
            # Include the line in indentation but keep selection at start of next line
            actual_end_line = end_line - 1
            keep_end_line = end_line
        else:
            actual_end_line = end_line
            keep_end_line = end_line
        
        # Store original selection info
        had_full_line_selection = sel_start.endswith('.0') and (selection_ends_at_line_start or text.get(f"{actual_end_line}.0", sel_end).strip() == "")
        
        # For each line, store its current indentation level
        line_indents = {}
        for line in range(start_line, actual_end_line + 1):
            line_text = text.get(f"{line}.0", f"{line}.end")
            line_indents[line] = len(line_text) - len(line_text.lstrip())
        
        # Indent each line and track the total spaces added
        for line in range(start_line, actual_end_line + 1):
            spaces_added = indent_line(line)
            line_indents[line] += spaces_added
        
        # Adjust selection based on whether we had full lines or partial selection
        if had_full_line_selection:
            # If we had full lines selected, maintain full line selection including the last line
            new_sel_start = f"{start_line}.0"
            new_sel_end = f"{keep_end_line}.0"
        else:
            # Adjust selection bounds based on indentation changes
            new_start_col = start_col + (line_indents[start_line] - (len(text.get(f"{start_line}.0", sel_start)) - len(text.get(f"{start_line}.0", sel_start).lstrip())))
            if selection_ends_at_line_start:
                new_sel_end = f"{keep_end_line}.0"
            else:
                new_end_col = end_col + (line_indents[actual_end_line] - (len(text.get(f"{actual_end_line}.0", sel_end)) - len(text.get(f"{actual_end_line}.0", sel_end).lstrip())))
                new_sel_end = f"{actual_end_line}.{new_end_col}"
            new_sel_start = f"{start_line}.{new_start_col}"
        
        # Restore selection
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", new_sel_start, new_sel_end)
        text.mark_set(tk.INSERT, new_sel_end)
        
    except tk.TclError:
        # No selection, just indent current line
        line = text.index(tk.INSERT).split('.')[0]
        col = int(text.index(tk.INSERT).split('.')[1])
        # Get current line's indentation
        line_text = text.get(f"{line}.0", f"{line}.end")
        current_indent = len(line_text) - len(line_text.lstrip())
        # Indent the line and move cursor
        indent_line(line)
        # Move cursor over by 4 spaces while preserving its position relative to the text
        new_col = col + 4 if col >= current_indent else col
        text.mark_set(tk.INSERT, f"{line}.{new_col}")
    
    return "break"

def on_shift_tab(event):
    try:
        # Get selection bounds
        sel_start = text.index("sel.first")
        sel_end = text.index("sel.last")
        
        # Parse line and column numbers
        start_line = int(sel_start.split('.')[0])
        end_line = int(sel_end.split('.')[0])
        start_col = int(sel_start.split('.')[1])
        end_col = int(sel_end.split('.')[1])
        
        # Check if selection ends at the start of a line
        selection_ends_at_line_start = end_col == 0
        if selection_ends_at_line_start and start_line != end_line:
            # Include the line in indentation but keep selection at start of next line
            actual_end_line = end_line - 1
            keep_end_line = end_line
        else:
            actual_end_line = end_line
            keep_end_line = end_line
        
        # Store original selection info
        had_full_line_selection = sel_start.endswith('.0') and (selection_ends_at_line_start or text.get(f"{actual_end_line}.0", sel_end).strip() == "")
        
        # For each line, store its current indentation level
        line_indents = {}
        for line in range(start_line, actual_end_line + 1):
            line_text = text.get(f"{line}.0", f"{line}.end")
            line_indents[line] = len(line_text) - len(line_text.lstrip())
            
        # Deindent each line and track the spaces removed
        for line in range(start_line, actual_end_line + 1):
            spaces_removed = deindent_line(line)
            line_indents[line] += spaces_removed
            
        # Adjust selection based on whether we had full lines or partial selection
        if had_full_line_selection:
            # If we had full lines selected, maintain full line selection
            new_sel_start = f"{start_line}.0"
            new_sel_end = f"{keep_end_line}.0"
        else:
            # Adjust selection bounds based on indentation changes
            new_start_col = max(0, start_col + (line_indents[start_line] - (len(text.get(f"{start_line}.0", sel_start)) - len(text.get(f"{start_line}.0", sel_start).lstrip()))))
            if selection_ends_at_line_start:
                new_sel_end = f"{keep_end_line}.0"
            else:
                new_end_col = max(0, end_col + (line_indents[actual_end_line] - (len(text.get(f"{actual_end_line}.0", sel_end)) - len(text.get(f"{actual_endLine}.0", sel_end).lstrip()))))
                new_sel_end = f"{actual_end_line}.{new_end_col}"
            new_sel_start = f"{start_line}.{new_start_col}"
            
        # Restore selection
        text.tag_remove("sel", "1.0", "end")
        text.tag_add("sel", new_sel_start, new_sel_end)
        text.mark_set(tk.INSERT, new_sel_end)
        
    except tk.TclError:
        # No selection, just deindent current line
        line = text.index(tk.INSERT).split('.')[0]
        col = int(text.index(tk.INSERT).split('.')[1])
        # Get current line's indentation
        line_text = text.get(f"{line}.0", f"{line}.end")
        current_indent = len(line_text) - len(line_text.lstrip())
        # Deindent the line
        spaces_removed = deindent_line(line)
        # Move cursor while preserving its position relative to the text
        new_col = max(0, col + spaces_removed if col >= current_indent else col)
        text.mark_set(tk.INSERT, f"{line}.{new_col}")
        
    return "break"

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
    return "break"

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

def save_shortcut(event=None):
    save_file()
    return "break"
root.bind_all("<Control-s>", save_shortcut)
root.bind_all("<Command-s>", save_shortcut)

def open_folder_dialog():
    folder = filedialog.askdirectory()
    if folder:
        opened_folder[0] = folder
        load_tree(folder)

def load_tree(path):
    filetree.delete(*filetree.get_children())
    def insert_item(parent, abspath):
        name = os.path.basename(abspath)
        # Exclude .uid files
        if name.lower().endswith('.uid'):
            return
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

menubar = tk.Menu(root, bg=current_theme["MENU_BG"], fg=current_theme["MENU_FG"])
filemenu = tk.Menu(menubar, tearoff=0, bg=current_theme["MENU_BG"], fg=current_theme["MENU_FG"])
thememenu = tk.Menu(menubar, tearoff=0, bg=current_theme["MENU_BG"], fg=current_theme["MENU_FG"])
langmenu = tk.Menu(menubar, tearoff=0, bg=current_theme["MENU_BG"], fg=current_theme["MENU_FG"])

filemenu.add_command(label="New", command=lambda: new_file())
filemenu.add_command(label="Open...", command=lambda: open_file())
filemenu.add_command(label="Open Folder...", command=open_folder_dialog)
filemenu.add_command(label="Save As...", command=lambda: save_file())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=lambda: on_exit())

def select_theme(theme_name):
    apply_theme(theme_name)
    save_settings(theme_name, font_size)

for theme_name in themes:
    thememenu.add_command(label=theme_name, command=lambda t=theme_name: select_theme(t))

def import_theme_dialog():
    path = filedialog.askopenfilename(
        title="Import Theme",
        filetypes=[("Theme JSON files", "*.json")]
    )
    if not path:
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        out_path = os.path.join(THEME_DIR, os.path.basename(path))
        with open(out_path, "w", encoding="utf-8") as outf:
            json.dump(data, outf, indent=2)
        messagebox.showinfo("Theme Imported", f"Theme '{data['name']}' imported! Restart to use it.")
    except Exception as e:
        messagebox.showerror("Import Failed", f"Could not import theme: {e}")

thememenu.add_separator()
thememenu.add_command(label="Import Theme...", command=import_theme_dialog)

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

def open_file(filepath=None):
    if filepath is None:
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
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            text.insert(tk.END, file.read())
        root.title(f"{filepath} - Code Editor")
        current_filepath[0] = filepath
        highlight_all()
        update_line_numbers()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file:\n{e}")

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
    # Save current selection if any
    try:
        sel_start = text.index("sel.first")
        sel_end = text.index("sel.last")
        has_selection = True
    except tk.TclError:
        has_selection = False

    # Remove syntax highlighting tags but keep selection
    for tag in text.tag_names():
        if tag != "sel":
            text.tag_remove(tag, "1.0", "end")

    code = text.get("1.0", tk.END)
    index = "1.0"

    def index_add(idx, chars):
        line, col = map(int, idx.split('.'))
        col += chars
        return f"{line}.{col}"

    theme = current_theme
    if current_language == "gdscript":
        # Comments
        for match in re.finditer(r'#.*', code):
            text.tag_add("gdscript.comment", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Strings (single, double, triple)
        for match in re.finditer(r"('''.*?'''|\"\"\".*?\"\"\"|'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")", code, re.DOTALL):
            text.tag_add("gdscript.string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Numbers (int, float, binary, hex)
        for match in re.finditer(r'\b(?:0x[0-9A-Fa-f]+|0b[01]+|\d+(\.\d+)?([eE][+-]?\d+)?|\.\d+)\b', code):
            text.tag_add("gdscript.number", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Annotations / Decorators (@export, @onready, etc.)
        for match in re.finditer(r'@[a-zA-Z_]\w*', code):
            text.tag_add("gdscript.annotation", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Signals
        for match in re.finditer(r'^\s*signal\s+(\w+)', code, re.MULTILINE):
            text.tag_add("gdscript.signal", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")
        # Types (e.g. : int, : String, -> void)
        for match in re.finditer(r':\s*([A-Za-z_]\w*)', code):
            text.tag_add("gdscript.type", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")
        for match in re.finditer(r'->\s*([A-Za-z_]\w*)', code):
            text.tag_add("gdscript.type", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")
        # Builtin classes (Vector2, Node, etc.)
        BUILTIN_CLASSES = [
            "Vector2", "Vector3", "Node", "Node2D", "Sprite2D", "Sprite3D", "Color", "Dictionary", "Array",
            "SceneTree", "Resource", "Input", "String", "PoolStringArray", "Rect2", "Transform2D"
        ]
        for cls in BUILTIN_CLASSES:
            for match in re.finditer(rf'\b{cls}\b', code):
                text.tag_add("gdscript.builtin_class", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Builtin functions
        builtins = [
            "abs", "print", "str", "int", "float", "get_node", "queue_free", "get_tree", "yield", "await", "extends",
            "setget", "assert", "pass", "break", "continue", "is_instance_valid", "preload", "load", "range", "len"
        ]
        for builtin in builtins:
            for match in re.finditer(rf'\b{builtin}\b', code):
                text.tag_add("gdscript.builtin", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Keywords
        keywords = [
            "func", "var", "const", "enum", "class", "static", "extends", "onready", "export", "signal",
            "if", "elif", "else", "for", "while", "match", "in", "not", "and", "or", "return", "pass", "break", "continue",
            "true", "false", "null", "self", "tool", "remote", "master", "puppet", "remotesync", "mastersync", "puppetsync", "await"
        ]
        for kw in keywords:
            for match in re.finditer(rf'\b{kw}\b', code):
                text.tag_add("gdscript.keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Operators (common)
        for match in re.finditer(r'[\+\-\*/%=&|!<>~^]', code):
            text.tag_add("gdscript.operator", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        # Variables (simple: variable names before =, after var/const)
        for match in re.finditer(r'\b(var|const)\s+([A-Za-z_]\w*)', code):
            text.tag_add("gdscript.variable", f"1.0+{match.start(2)}c", f"1.0+{match.end(2)}c")
        # Function names
        for match in re.finditer(r'\bfunc\s+([A-Za-z_]\w*)', code):
            text.tag_add("gdscript.function", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")
        # Class names
        for match in re.finditer(r'\bclass\s+([A-Za-z_]\w*)', code):
            text.tag_add("gdscript.class", f"1.0+{match.start(1)}c", f"1.0+{match.end(1)}c")
        # Constants (UPPER_SNAKE_CASE)
        for match in re.finditer(r'\b[A-Z_]{2,}\b', code):
            text.tag_add("gdscript.constant", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
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
                key = str(t)
                if key in theme:
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
                key = str(t)
                if key in theme:
                    text.tag_add(str(t), index, next_index)
                    break
                t = t.parent
            index = next_index

def set_language(lexname):
    global current_language
    current_language = lexname
    highlight_all()

root.protocol("WM_DELETE_WINDOW", on_exit)

def launch_open_with_file():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            open_file(filepath)
            folder = os.path.dirname(filepath)
            if folder and os.path.isdir(folder):
                opened_folder[0] = folder
                load_tree(folder)
        else:
            messagebox.showwarning("File not found", f'File "{filepath}" does not exist.')

paned.add(explorer_frame, minsize=120)
paned.add(main_frame)
setup_main_frame_contents()

apply_theme(current_theme_name)
set_language(current_language)
highlight_all()
update_line_numbers()

launch_open_with_file()

def on_drop(event):
    files = root.tk.splitlist(event.data)
    for filepath in files:
        if os.path.isdir(filepath):
            opened_folder[0] = filepath
            load_tree(filepath)
            break
        elif os.path.isfile(filepath):
            open_file(filepath)
            break

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
