import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
from datetime import datetime

# Globale Variablen
canvas = None
entities = []
relations = []
toolbar_frame = None
entity_listbox = None
relation_listbox = None
selected_entity = None
selected_relation = None
drag_data = {"x": 0, "y": 0, "item": None}
canvas_frame = None
current_tool = "select"
DIAGRAM_DIR = "C:/LiteDBox/Diagrams"
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
GRID_SIZE = 20

# Design-Konstanten
STATUS_BG = "#E6EFF8"
CANVAS_BG = "#FFFFFF"

class Entity:
    def __init__(self, name, x, y, width=120, height=80):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.attributes = []
        self.methods = []
        self.canvas_id = None
        self.text_id = None
        self.attribute_ids = []
        self.method_ids = []

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "attributes": self.attributes,
            "methods": self.methods
        }

    @classmethod
    def from_dict(cls, data):
        entity = cls(data["name"], data["x"], data["y"], data["width"], data["height"])
        entity.attributes = data["attributes"]
        entity.methods = data["methods"]
        return entity

class Relation:
    def __init__(self, from_entity, to_entity, relation_type="association"):
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.type = relation_type  # association, inheritance, composition, aggregation
        self.canvas_line_id = None
        self.canvas_arrow_id = None
        self.canvas_text_id = None

    def to_dict(self):
        return {
            "from_entity": entities.index(self.from_entity),
            "to_entity": entities.index(self.to_entity),
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data, entities_list):
        return cls(
            entities_list[data["from_entity"]],
            entities_list[data["to_entity"]],
            data["type"]
        )

def init_uml_tab(parent_tab, bg, text_bg, text_fg, accent, accent_hover, header_bg, font, font_mono):
    global canvas, toolbar_frame, entity_listbox, relation_listbox, canvas_frame
    
    # Oberer Bereich mit den Werkzeugen
    toolbar_frame = tk.Frame(parent_tab, bg=header_bg, height=40)
    toolbar_frame.pack(fill="x", padx=5, pady=5)
    
    select_btn = tk.Button(toolbar_frame, text="Auswahl", bg=text_bg, fg=text_fg, 
                         relief="flat", font=font, command=lambda: select_tool("select"))
    select_btn.pack(side=tk.LEFT, padx=5)
    
    entity_btn = tk.Button(toolbar_frame, text="Entität", bg=text_bg, fg=text_fg, 
                        relief="flat", font=font, command=lambda: select_tool("entity"))
    entity_btn.pack(side=tk.LEFT, padx=5)
    
    relation_btn = tk.Button(toolbar_frame, text="Beziehung", bg=text_bg, fg=text_fg, 
                           relief="flat", font=font, command=lambda: select_tool("relation"))
    relation_btn.pack(side=tk.LEFT, padx=5)
    
    relation_type_label = tk.Label(toolbar_frame, text="Beziehungstyp:", bg=header_bg, fg=text_fg, font=font)
    relation_type_label.pack(side=tk.LEFT, padx=(15, 5))
    
    relation_type_var = tk.StringVar(value="association")
    relation_type_combo = ttk.Combobox(toolbar_frame, textvariable=relation_type_var, 
                                    values=["association", "inheritance", "composition", "aggregation"],
                                    width=15, font=font)
    relation_type_combo.pack(side=tk.LEFT, padx=5)
    
    save_btn = tk.Button(toolbar_frame, text="Speichern", bg=accent, fg="white", 
                       relief="flat", font=font, activebackground=accent_hover,
                       command=lambda: save_diagram())
    save_btn.pack(side=tk.RIGHT, padx=5)
    
    load_btn = tk.Button(toolbar_frame, text="Laden", bg=text_bg, fg=text_fg, 
                       relief="flat", font=font, command=lambda: load_diagram())
    load_btn.pack(side=tk.RIGHT, padx=5)
    
    export_btn = tk.Button(toolbar_frame, text="Exportieren", bg=text_bg, fg=text_fg, 
                         relief="flat", font=font, command=lambda: export_diagram())
    export_btn.pack(side=tk.RIGHT, padx=5)
    
    # Hauptbereich mit Canvas und Eigenschaften
    main_paned = ttk.PanedWindow(parent_tab, orient=tk.HORIZONTAL)
    main_paned.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Canvas-Frame
    canvas_frame = tk.Frame(main_paned, bg=bg)
    main_paned.add(canvas_frame, weight=3)
    
    canvas_scroll_y = ttk.Scrollbar(canvas_frame, orient="vertical")
    canvas_scroll_y.pack(side=tk.RIGHT, fill="y")
    
    canvas_scroll_x = ttk.Scrollbar(canvas_frame, orient="horizontal")
    canvas_scroll_x.pack(side=tk.BOTTOM, fill="x")
    
    canvas = tk.Canvas(canvas_frame, bg=CANVAS_BG, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                     xscrollcommand=canvas_scroll_x.set, yscrollcommand=canvas_scroll_y.set)
    canvas.pack(fill="both", expand=True)
    
    canvas_scroll_y.config(command=canvas.yview)
    canvas_scroll_x.config(command=canvas.xview)
    
    # Eigenschaften-Frame
    properties_frame = tk.Frame(main_paned, bg=bg, width=250)
    main_paned.add(properties_frame, weight=1)
    
    properties_notebook = ttk.Notebook(properties_frame)
    properties_notebook.pack(fill="both", expand=True)
    
    # Entitäten-Tab
    entities_tab = tk.Frame(properties_notebook, bg=bg)
    properties_notebook.add(entities_tab, text="Entitäten")
    
    entity_listbox_label = tk.Label(entities_tab, text="Entitäten:", bg=bg, fg=text_fg, font=font)
    entity_listbox_label.pack(anchor="w", padx=5, pady=(5, 0))
    
    entity_listbox = tk.Listbox(entities_tab, font=font, bg=text_bg, fg=text_fg, selectbackground=accent)
    entity_listbox.pack(fill="x", padx=5, pady=5)
    
    entity_btn_frame = tk.Frame(entities_tab, bg=bg)
    entity_btn_frame.pack(fill="x", padx=5, pady=5)
    
    add_attr_btn = tk.Button(entity_btn_frame, text="+ Attribut", bg=text_bg, fg=text_fg, 
                          relief="flat", font=font, command=lambda: add_attribute())
    add_attr_btn.pack(side=tk.LEFT, padx=5)
    
    add_method_btn = tk.Button(entity_btn_frame, text="+ Methode", bg=text_bg, fg=text_fg, 
                            relief="flat", font=font, command=lambda: add_method())
    add_method_btn.pack(side=tk.LEFT, padx=5)
    
    entity_properties_frame = tk.Frame(entities_tab, bg=bg)
    entity_properties_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    entity_properties_label = tk.Label(entity_properties_frame, text="Eigenschaften:", bg=bg, fg=text_fg, font=font)
    entity_properties_label.pack(anchor="w")
    
    entity_properties_text = scrolledtext.ScrolledText(entity_properties_frame, height=10, font=font_mono, 
                                                    bg=text_bg, fg=text_fg, wrap=tk.WORD)
    entity_properties_text.pack(fill="both", expand=True, pady=5)
    
    update_entity_btn = tk.Button(entity_properties_frame, text="Aktualisieren", bg=accent, fg="white", 
                               relief="flat", font=font, activebackground=accent_hover,
                               command=lambda: update_entity_properties(entity_properties_text.get("1.0", tk.END)))
    update_entity_btn.pack(anchor="e", pady=5)
    
    # Beziehungen-Tab
    relations_tab = tk.Frame(properties_notebook, bg=bg)
    properties_notebook.add(relations_tab, text="Beziehungen")
    
    relation_listbox_label = tk.Label(relations_tab, text="Beziehungen:", bg=bg, fg=text_fg, font=font)
    relation_listbox_label.pack(anchor="w", padx=5, pady=(5, 0))
    
    relation_listbox = tk.Listbox(relations_tab, font=font, bg=text_bg, fg=text_fg, selectbackground=accent)
    relation_listbox.pack(fill="x", padx=5, pady=5)
    
    relation_type_frame = tk.Frame(relations_tab, bg=bg)
    relation_type_frame.pack(fill="x", padx=5, pady=5)
    
    relation_type_change_label = tk.Label(relation_type_frame, text="Beziehungstyp:", bg=bg, fg=text_fg, font=font)
    relation_type_change_label.pack(side=tk.LEFT)
    
    relation_type_change_var = tk.StringVar(value="association")
    relation_type_change_combo = ttk.Combobox(relation_type_frame, textvariable=relation_type_change_var, 
                                            values=["association", "inheritance", "composition", "aggregation"],
                                            width=15, font=font)
    relation_type_change_combo.pack(side=tk.LEFT, padx=5)
    
    update_relation_btn = tk.Button(relation_type_frame, text="Aktualisieren", bg=accent, fg="white", 
                                  relief="flat", font=font, activebackground=accent_hover,
                                  command=lambda: update_relation_type(relation_type_change_var.get()))
    update_relation_btn.pack(side=tk.LEFT, padx=5)
    
    # Canvas-Events
    canvas.bind("<Button-1>", on_canvas_click)
    canvas.bind("<B1-Motion>", on_canvas_drag)
    canvas.bind("<ButtonRelease-1>", on_canvas_release)
    
    # Listbox-Events
    entity_listbox.bind("<<ListboxSelect>>", on_entity_select)
    relation_listbox.bind("<<ListboxSelect>>", on_relation_select)
    
    # Erstellen des Rasters für das Canvas
    draw_grid()
    
    # Setze die Scrollregion des Canvas
    canvas.config(scrollregion=(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT))

def select_tool(tool):
    global current_tool
    current_tool = tool

def on_canvas_click(event):
    global selected_entity, selected_relation, drag_data
    
    # Canvas-Koordinaten berechnen
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    
    if current_tool == "select":
        # Prüfen, ob eine Entität angeklickt wurde
        for entity in entities:
            if x >= entity.x and x <= entity.x + entity.width and y >= entity.y and y <= entity.y + entity.height:
                selected_entity = entity
                selected_relation = None
                update_entity_listbox()
                drag_data = {"x": x, "y": y, "item": entity}
                return
        
        # Prüfen, ob eine Beziehung angeklickt wurde
        for relation in relations:
            # Vereinfachte Erkennung - könnte verbessert werden
            from_x = relation.from_entity.x + relation.from_entity.width / 2
            from_y = relation.from_entity.y + relation.from_entity.height / 2
            to_x = relation.to_entity.x + relation.to_entity.width / 2
            to_y = relation.to_entity.y + relation.to_entity.height / 2
            
            # Prüfen, ob der Klick nahe der Linie ist
            if is_point_near_line(x, y, from_x, from_y, to_x, to_y, 10):
                selected_relation = relation
                selected_entity = None
                update_relation_listbox()
                return
                
        # Nichts ausgewählt
        selected_entity = None
        selected_relation = None
        update_entity_listbox()
        update_relation_listbox()
    
    elif current_tool == "entity":
        # Neue Entität erstellen
        name = simpledialog.askstring("Neue Entität", "Name der Entität:")
        if name:
            # Runde die Position auf Rastergröße
            x = round(x / GRID_SIZE) * GRID_SIZE
            y = round(y / GRID_SIZE) * GRID_SIZE
            
            entity = Entity(name, x, y)
            entities.append(entity)
            draw_entity(entity)
            update_entity_listbox()
    
    elif current_tool == "relation":
        # Erste Entität für Beziehung auswählen
        for entity in entities:
            if x >= entity.x and x <= entity.x + entity.width and y >= entity.y and y <= entity.y + entity.height:
                selected_entity = entity
                update_entity_listbox()
                current_tool = "relation_second"
                return
    
    elif current_tool == "relation_second":
        # Zweite Entität für Beziehung auswählen
        for entity in entities:
            if x >= entity.x and x <= entity.x + entity.width and y >= entity.y and y <= entity.y + entity.height:
                if entity != selected_entity:
                    relation_type = simpledialog.askstring("Beziehungstyp", 
                                                     "Typ der Beziehung (association, inheritance, composition, aggregation):",
                                                     initialvalue="association")
                    
                    if relation_type not in ["association", "inheritance", "composition", "aggregation"]:
                        relation_type = "association"
                    
                    relation = Relation(selected_entity, entity, relation_type)
                    relations.append(relation)
                    draw_relation(relation)
                    update_relation_listbox()
                    
                    # Zurück zum Auswahlwerkzeug
                    current_tool = "select"
                    selected_entity = None
                return

def on_canvas_drag(event):
    global drag_data
    if current_tool == "select" and drag_data["item"] is not None:
        # Canvas-Koordinaten berechnen
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        
        # Berechnung der Verschiebung
        dx = x - drag_data["x"]
        dy = y - drag_data["y"]
        
        # Aktualisieren des Elements
        entity = drag_data["item"]
        
        # Runde die neue Position auf das Raster
        new_x = round((entity.x + dx) / GRID_SIZE) * GRID_SIZE
        new_y = round((entity.y + dy) / GRID_SIZE) * GRID_SIZE
        
        # Verschieben der Entität
        entity.x = new_x
        entity.y = new_y
        
        # Neuzeichnen der Entität
        redraw_all()
        
        # Aktualisieren der Drag-Daten
        drag_data["x"] = x
        drag_data["y"] = y