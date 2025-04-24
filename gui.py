import tkinter as tk
from tkinter import ttk, scrolledtext
import litedbox_core as litedbox_core
import sys
import os

def resource_path(relative_path):
    """ Holt den richtigen Pfad - ob im Skript oder in der .exe """
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


litedbox_core.init()

BG = "#F0F0F0"
SIDEBAR_BG = "#E6EFF8" 
TEXT_BG = "#FFFFFF"
TEXT_FG = "#333333"
ACCENT = "#1A75CF"  
ACCENT_HOVER = "#0D66BE"
HEADER_BG = "#D5E4F3"  
TREE_SELECT = "#CCE4F7"
TREE_HOVER = "#E5F1FB"
TAB_BG = "#E9F2FB"  
TOOLBAR_BG = "#D5E4F3"  
STATUS_BG = "#E6EFF8"  
FONT = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 11)

EXECUTE_ICON = "▶"
DB_ICON = "📁"
TABLE_ICON = "🗃️"

root = tk.Tk()
root.title("LiteDBox SQL Studio")
root.iconbitmap(resource_path("logo.ico"))
root.geometry("1200x700")
root.configure(bg=BG)

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

sidebar = tk.Frame(root, width=250, bg=SIDEBAR_BG, relief="flat")
sidebar.grid(row=0, column=0, sticky="nsew")
sidebar.grid_propagate(False)

toolbar = tk.Frame(root, height=36, bg=TOOLBAR_BG, relief="flat")
toolbar.grid(row=0, column=1, sticky="new")

conn_button = tk.Button(toolbar, text="Connect", bg=TOOLBAR_BG, fg=TEXT_FG, 
                        relief="flat", font=("Segoe UI", 9),
                        activebackground=TREE_SELECT)
conn_button.pack(side=tk.LEFT, padx=(10, 5), pady=5)

refresh_button = tk.Button(toolbar, text="Refresh", bg=TOOLBAR_BG, fg=TEXT_FG, 
                          relief="flat", font=("Segoe UI", 9),
                          activebackground=TREE_SELECT)
refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

main_frame = tk.Frame(root, bg=BG)
main_frame.grid(row=0, column=1, sticky="nsew")
main_frame.grid_rowconfigure(2, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

sidebar_header = tk.Frame(sidebar, height=30, bg=HEADER_BG, relief="flat")
sidebar_header.pack(fill="x")

sidebar_title = tk.Label(sidebar_header, text="Navigator", bg=HEADER_BG, fg=TEXT_FG, font=("Segoe UI", 10, "bold"))
sidebar_title.pack(side=tk.LEFT, pady=5, padx=10)

tab_style = ttk.Style()
tab_style.configure('lefttab.TNotebook', tabposition='wn', background=SIDEBAR_BG)
tab_style.map('TNotebook.Tab', background=[('selected', TAB_BG), ('!selected', SIDEBAR_BG)])
tab_style.configure('TNotebook.Tab', background=SIDEBAR_BG, padding=[5, 2])

sidebar_tabs = ttk.Notebook(sidebar, style='lefttab.TNotebook')
sidebar_tabs.pack(fill="both", expand=True)

db_tab = tk.Frame(sidebar_tabs, bg=SIDEBAR_BG)
sidebar_tabs.add(db_tab, text="Connections")

db_frame = tk.Frame(db_tab, bg=SIDEBAR_BG)
db_frame.pack(fill="both", expand=True, padx=2, pady=2)

db_label = tk.Label(db_frame, text="Datenbanken", bg=SIDEBAR_BG, fg=TEXT_FG, font=("Segoe UI", 10, "bold"))
db_label.pack(pady=(10, 0), padx=10, anchor="w")

db_listbox = ttk.Treeview(db_frame, show="tree", selectmode="browse", style="Sidebar.Treeview")
db_listbox.pack(fill="both", expand=True, padx=5, pady=5)

table_frame = tk.Frame(db_frame, bg=SIDEBAR_BG)
table_frame.pack(fill="both", expand=True)

table_label = tk.Label(table_frame, text="Tabellen", bg=SIDEBAR_BG, fg=TEXT_FG, font=("Segoe UI", 10, "bold"))
table_label.pack(pady=(10, 0), padx=10, anchor="w")

table_listbox = ttk.Treeview(table_frame, show="tree", selectmode="browse", style="Sidebar.Treeview")
table_listbox.pack(fill="both", expand=True, padx=5, pady=5)

sql_header = tk.Frame(main_frame, height=30, bg=HEADER_BG, relief="flat")
sql_header.grid(row=0, column=0, sticky="new")

sql_label = tk.Label(sql_header, text="SQL Worksheet", bg=HEADER_BG, fg=TEXT_FG, font=("Segoe UI", 10, "bold"))
sql_label.pack(side=tk.LEFT, pady=5, padx=10)

entry_frame = tk.Frame(main_frame, bg=BG)
entry_frame.grid(row=1, column=0, sticky="new", padx=5, pady=5)

entry = scrolledtext.ScrolledText(entry_frame, height=8, font=FONT_MONO, bg=TEXT_BG, fg=TEXT_FG, 
                                 insertbackground="#000000", relief="solid", bd=1)
entry.pack(fill="both", expand=True)

button_frame = tk.Frame(main_frame, bg=BG)
button_frame.grid(row=1, column=0, sticky="se", padx=10, pady=(0, 5))

run_button = tk.Button(button_frame, text=f"{EXECUTE_ICON} Ausführen", bg=ACCENT, fg="white", 
                       font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5,
                       activebackground=ACCENT_HOVER, activeforeground="white",
                       command=lambda: run_sql())
run_button.pack(side=tk.RIGHT)

response_frame = tk.Frame(main_frame, bg=BG)
response_frame.grid(row=2, column=0, sticky="new")

response_label = tk.Label(response_frame, text="", anchor="w", bg=BG, fg="green", font=("Segoe UI", 9))
response_label.pack(fill="x", padx=10, pady=(0, 5))

results_notebook = ttk.Notebook(main_frame)
results_notebook.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))

tab_style.map('TNotebook.Tab', background=[('selected', TAB_BG)])
tab_style.configure('TNotebook.Tab', background=SIDEBAR_BG, padding=[5, 2])

results_tab = tk.Frame(results_notebook, bg=BG)
results_notebook.add(results_tab, text="Abfrageergebnisse")

tree_style = ttk.Style()
tree_style.theme_use("clam")
tree_style.configure("Treeview",
    background=TEXT_BG,
    foreground=TEXT_FG,
    fieldbackground=TEXT_BG,
    rowheight=22,
    font=FONT,
    bordercolor="#C4D5E8",  
    borderwidth=1
)

tree_style.configure("Treeview.Heading",
    background=HEADER_BG,
    foreground=TEXT_FG,
    font=("Segoe UI", 9, "bold"),
    relief="flat"
)

tree_style.map("Treeview", 
    background=[("selected", TREE_SELECT)],
    foreground=[("selected", "#000000")]
)

tree_style.configure("Sidebar.Treeview",
    background=SIDEBAR_BG,
    foreground=TEXT_FG,
    fieldbackground=SIDEBAR_BG,
    font=("Segoe UI", 9),
    rowheight=20,
    borderwidth=0
)

tree_style.map("Sidebar.Treeview",
    background=[("selected", TREE_SELECT)],
    foreground=[("selected", "#000000")]
)

tree_frame = tk.Frame(results_tab)
tree_frame.pack(fill="both", expand=True)

tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
tree_scroll_y.pack(side=tk.RIGHT, fill="y")

tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
tree_scroll_x.pack(side=tk.BOTTOM, fill="x")

tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree.pack(fill="both", expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

status_bar = tk.Frame(root, height=22, bg=STATUS_BG, relief="sunken", bd=1)
status_bar.grid(row=1, column=0, columnspan=2, sticky="sew")

status_label = tk.Label(status_bar, text="Bereit", bg=STATUS_BG, fg=TEXT_FG, anchor="w", font=("Segoe UI", 8))
status_label.pack(side=tk.LEFT, padx=10)

def refresh_sidebar():
    for item in db_listbox.get_children():
        db_listbox.delete(item)
    
    for db in os.listdir("C:/LiteDBox"):
        db_listbox.insert("", "end", text=f" {DB_ICON} {db}", values=(db,))

def show_tables(event):
    selected_items = db_listbox.selection()
    if selected_items:
        selected_item = selected_items[0]
        selected_db = db_listbox.item(selected_item)["values"][0]
        
        if selected_db:
            litedbox_core.use_database(selected_db)
            
            for item in table_listbox.get_children():
                table_listbox.delete(item)
            
            db_path = os.path.join("C:/LiteDBox", selected_db)
            for f in os.listdir(db_path):
                if f.endswith(".json"):
                    table_name = f.replace(".json", "")
                    table_listbox.insert("", "end", text=f" {TABLE_ICON} {table_name}", values=(table_name,))

def run_sql():
    statement = entry.get("1.0", tk.END).strip()
    status_label.config(text="SQL wird ausgeführt...")
    response = litedbox_core.handle_sql(statement, tree)
    response_label.config(text=response)
    status_label.config(text="Fertig")
    refresh_sidebar()

def insert_table_name(event):
    selected_items = table_listbox.selection()
    if selected_items:
        selected_item = selected_items[0]
        table_name = table_listbox.item(selected_item)["values"][0]
        entry.insert(tk.INSERT, table_name)

db_listbox.bind("<Double-1>", show_tables)
db_listbox.bind("<<TreeviewSelect>>", show_tables)
table_listbox.bind("<Double-1>", insert_table_name)

refresh_sidebar()

root.mainloop()
