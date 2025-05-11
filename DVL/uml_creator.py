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
    
    global entity_properties_frame
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
    
    global relation_type_frame
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

def on_canvas_release(event):
    global drag_data
    # Zurücksetzen der Drag-Daten
    drag_data = {"x": 0, "y": 0, "item": None}

def is_point_near_line(px, py, lx1, ly1, lx2, ly2, tolerance=5):
    # Berechnung der Distanz zwischen Punkt und Linie
    if lx2 - lx1 == 0:  # Vertikale Linie
        dist = abs(px - lx1)
    else:
        m = (ly2 - ly1) / (lx2 - lx1)
        b = ly1 - m * lx1
        dist = abs(py - (m * px + b)) / ((m ** 2 + 1) ** 0.5)
    
    # Prüfen, ob der Punkt im Bereich der Linie liegt
    min_x = min(lx1, lx2)
    max_x = max(lx1, lx2)
    min_y = min(ly1, ly2)
    max_y = max(ly1, ly2)
    
    if px < min_x - tolerance or px > max_x + tolerance or py < min_y - tolerance or py > max_y + tolerance:
        return False
    
    return dist <= tolerance

def draw_grid():
    # Raster zeichnen
    for x in range(0, CANVAS_WIDTH, GRID_SIZE):
        canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill="#EEEEEE")
    for y in range(0, CANVAS_HEIGHT, GRID_SIZE):
        canvas.create_line(0, y, CANVAS_WIDTH, y, fill="#EEEEEE")

def draw_entity(entity):
    # Löschen vorheriger Canvas-Elemente
    if entity.canvas_id:
        canvas.delete(entity.canvas_id)
    if entity.text_id:
        canvas.delete(entity.text_id)
    for attr_id in entity.attribute_ids:
        canvas.delete(attr_id)
    for method_id in entity.method_ids:
        canvas.delete(method_id)
    
    entity.attribute_ids = []
    entity.method_ids = []
    
    # Berechnung der tatsächlichen Höhe basierend auf der Anzahl der Attribute und Methoden
    header_height = 30
    attr_height = len(entity.attributes) * 20 if entity.attributes else 0
    method_height = len(entity.methods) * 20 if entity.methods else 0
    separator_height = 2
    
    min_height = header_height + 2 * separator_height
    if attr_height > 0:
        min_height += attr_height
    if method_height > 0:
        min_height += method_height
        
    entity.height = max(entity.height, min_height)
    
    # Rechteck für die Entität
    entity.canvas_id = canvas.create_rectangle(
        entity.x, entity.y, 
        entity.x + entity.width, entity.y + entity.height,
        fill="white", outline="black", width=2
    )
    
    # Titel der Entität
    entity.text_id = canvas.create_text(
        entity.x + entity.width / 2, entity.y + header_height / 2,
        text=entity.name, font=("Arial", 10, "bold")
    )
    
    # Trennlinie nach dem Titel
    canvas.create_line(
        entity.x, entity.y + header_height,
        entity.x + entity.width, entity.y + header_height,
        fill="black"
    )
    
    # Attribute anzeigen
    current_y = entity.y + header_height + 5
    for attr in entity.attributes:
        attr_id = canvas.create_text(
            entity.x + 10, current_y,
            text=attr, font=("Arial", 9),
            anchor="w"
        )
        entity.attribute_ids.append(attr_id)
        current_y += 20
    
    # Trennlinie nach den Attributen, wenn Methoden vorhanden sind
    if entity.methods:
        separator_y = entity.y + header_height + max(attr_height, 0) + separator_height
        line_id = canvas.create_line(
            entity.x, separator_y,
            entity.x + entity.width, separator_y,
            fill="black"
        )
        entity.attribute_ids.append(line_id)
        current_y = separator_y + 5
    
    # Methoden anzeigen
    for method in entity.methods:
        method_id = canvas.create_text(
            entity.x + 10, current_y,
            text=method, font=("Arial", 9),
            anchor="w"
        )
        entity.method_ids.append(method_id)
        current_y += 20

def draw_relation(relation):
    # Löschen vorheriger Canvas-Elemente
    if relation.canvas_line_id:
        canvas.delete(relation.canvas_line_id)
    if relation.canvas_arrow_id:
        canvas.delete(relation.canvas_arrow_id)
    if relation.canvas_text_id:
        canvas.delete(relation.canvas_text_id)
    
    # Berechnung der Start- und Endpunkte
    from_x = relation.from_entity.x + relation.from_entity.width / 2
    from_y = relation.from_entity.y + relation.from_entity.height / 2
    to_x = relation.to_entity.x + relation.to_entity.width / 2
    to_y = relation.to_entity.y + relation.to_entity.height / 2
    
    # Anpassung der Punkte an den Rand der Entitäten
    # Bestimmung der Schnittpunkte mit den Rändern
    from_x, from_y = calculate_border_point(
        from_x, from_y, 
        relation.from_entity.x, relation.from_entity.y,
        relation.from_entity.width, relation.from_entity.height,
        to_x, to_y
    )
    
    to_x, to_y = calculate_border_point(
        to_x, to_y, 
        relation.to_entity.x, relation.to_entity.y,
        relation.to_entity.width, relation.to_entity.height,
        from_x, from_y
    )
    
    # Zeichnen der Linie basierend auf dem Beziehungstyp
    if relation.type == "association":
        relation.canvas_line_id = canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill="black", arrow=tk.LAST, width=1.5
        )
    
    elif relation.type == "inheritance":
        # Normale Linie ohne Pfeil
        relation.canvas_line_id = canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill="black", width=1.5
        )
        
        # Berechnung der Richtung für das Dreieck
        dx = to_x - from_x
        dy = to_y - from_y
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return  # Verhindert Division durch Null
        
        # Normalisierung
        dx /= length
        dy /= length
        
        # Berechnung der Punkte für das Dreieck
        arrow_size = 12
        p1x = to_x
        p1y = to_y
        p2x = to_x - dx*arrow_size - dy*arrow_size/2
        p2y = to_y - dy*arrow_size + dx*arrow_size/2
        p3x = to_x - dx*arrow_size + dy*arrow_size/2
        p3y = to_y - dy*arrow_size - dx*arrow_size/2
        
        relation.canvas_arrow_id = canvas.create_polygon(
            p1x, p1y, p2x, p2y, p3x, p3y,
            fill="white", outline="black"
        )
    
    elif relation.type == "composition":
        relation.canvas_line_id = canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill="black", width=1.5
        )
        
        # Berechnung der Richtung für die Raute
        dx = from_x - to_x
        dy = from_y - to_y
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return  # Verhindert Division durch Null
        
        # Normalisierung
        dx /= length
        dy /= length
        
        # Berechnung der Punkte für die Raute
        diamond_size = 10
        p1x = to_x + dx*diamond_size
        p1y = to_y + dy*diamond_size
        p2x = to_x + dy*diamond_size/2
        p2y = to_y - dx*diamond_size/2
        p3x = to_x - dx*diamond_size
        p3y = to_y - dy*diamond_size
        p4x = to_x - dy*diamond_size/2
        p4y = to_y + dx*diamond_size/2
        
        relation.canvas_arrow_id = canvas.create_polygon(
            p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y,
            fill="black", outline="black"
        )
    
    elif relation.type == "aggregation":
        relation.canvas_line_id = canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill="black", width=1.5
        )
        
        # Berechnung der Richtung für die Raute
        dx = from_x - to_x
        dy = from_y - to_y
        length = (dx**2 + dy**2)**0.5
        if length == 0:
            return  # Verhindert Division durch Null
        
        # Normalisierung
        dx /= length
        dy /= length
        
        # Berechnung der Punkte für die Raute
        diamond_size = 10
        p1x = to_x + dx*diamond_size
        p1y = to_y + dy*diamond_size
        p2x = to_x + dy*diamond_size/2
        p2y = to_y - dx*diamond_size/2
        p3x = to_x - dx*diamond_size
        p3y = to_y - dy*diamond_size
        p4x = to_x - dy*diamond_size/2
        p4y = to_y + dx*diamond_size/2
        
        relation.canvas_arrow_id = canvas.create_polygon(
            p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y,
            fill="white", outline="black"
        )
    
    # Text für den Beziehungstyp
    mid_x = (from_x + to_x) / 2
    mid_y = (from_y + to_y) / 2
    relation.canvas_text_id = canvas.create_text(
        mid_x, mid_y - 10,
        text=relation.type,
        font=("Arial", 8),
        fill="blue"
    )

def calculate_border_point(center_x, center_y, rect_x, rect_y, rect_width, rect_height, target_x, target_y):
    """
    Berechnet den Schnittpunkt zwischen einer Linie und einem Rechteck.
    Die Linie geht vom Mittelpunkt des Rechtecks zum Zielpunkt.
    """
    
    # Berechnung der Richtung
    dx = target_x - center_x
    dy = target_y - center_y
    
    # Verhindere Division durch Null
    if dx == 0 and dy == 0:
        return center_x, center_y
    
    # Normalisierung der Richtung
    length = (dx**2 + dy**2)**0.5
    dx /= length
    dy /= length
    
    # Bestimmung der Schnittpunkte mit den Rändern
    if abs(dx) > abs(dy):
        # Horizontaler Schnittpunkt
        if dx > 0:
            x = rect_x + rect_width
        else:
            x = rect_x
        y = center_y + dy * (x - center_x) / dx
        
        # Prüfen, ob der Punkt innerhalb des Rechtecks liegt
        if y < rect_y or y > rect_y + rect_height:
            # Vertikaler Schnittpunkt
            if dy > 0:
                y = rect_y + rect_height
            else:
                y = rect_y
            x = center_x + dx * (y - center_y) / dy
    else:
        # Vertikaler Schnittpunkt
        if dy > 0:
            y = rect_y + rect_height
        else:
            y = rect_y
        x = center_x + dx * (y - center_y) / dy
        
        # Prüfen, ob der Punkt innerhalb des Rechtecks liegt
        if x < rect_x or x > rect_x + rect_width:
            # Horizontaler Schnittpunkt
            if dx > 0:
                x = rect_x + rect_width
            else:
                x = rect_x
            y = center_y + dy * (x - center_x) / dx
    
    return x, y

def redraw_all():
    """
    Zeichnet alle Entitäten und Beziehungen neu.
    Wird verwendet, wenn sich Positionen oder Eigenschaften geändert haben.
    """
    # Canvas leeren
    canvas.delete("all")
    
    # Raster neu zeichnen
    draw_grid()
    
    # Alle Entitäten neu zeichnen
    for entity in entities:
        draw_entity(entity)
    
    # Alle Beziehungen neu zeichnen
    for relation in relations:
        draw_relation(relation)

def update_entity_listbox():
    """
    Aktualisiert die Listbox mit den Entitäten und markiert die ausgewählte Entität.
    """
    entity_listbox.delete(0, tk.END)
    for i, entity in enumerate(entities):
        entity_listbox.insert(tk.END, entity.name)
        if entity == selected_entity:
            entity_listbox.selection_set(i)
    
    # Eigenschaften anzeigen, wenn eine Entität ausgewählt ist
    if selected_entity:
        properties_text = f"Name: {selected_entity.name}\n\n"
        properties_text += "Attribute:\n"
        for attr in selected_entity.attributes:
            properties_text += f"- {attr}\n"
        properties_text += "\nMethoden:\n"
        for method in selected_entity.methods:
            properties_text += f"- {method}\n"
        
        # Text im properties_text-Widget aktualisieren
        for widget in entity_properties_frame.winfo_children():
            if isinstance(widget, scrolledtext.ScrolledText):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", properties_text)
                break

def update_relation_listbox():
    """
    Aktualisiert die Listbox mit den Beziehungen und markiert die ausgewählte Beziehung.
    """
    relation_listbox.delete(0, tk.END)
    for i, relation in enumerate(relations):
        relation_name = f"{relation.from_entity.name} -> {relation.to_entity.name} ({relation.type})"
        relation_listbox.insert(tk.END, relation_name)
        if relation == selected_relation:
            relation_listbox.selection_set(i)
    
    # Beziehungstyp im Combobox setzen, wenn eine Beziehung ausgewählt ist
    if selected_relation:
        for widget in relation_type_frame.winfo_children():
            if isinstance(widget, ttk.Combobox):
                widget.set(selected_relation.type)
                break

def on_entity_select(event):
    """
    Wird aufgerufen, wenn eine Entität in der Listbox ausgewählt wird.
    """
    global selected_entity, selected_relation
    
    if not entity_listbox.curselection():
        return
    
    index = entity_listbox.curselection()[0]
    selected_entity = entities[index]
    selected_relation = None
    
    # Aktualisiere die Eigenschaften-Anzeige
    update_entity_listbox()
    update_relation_listbox()

def on_relation_select(event):
    """
    Wird aufgerufen, wenn eine Beziehung in der Listbox ausgewählt wird.
    """
    global selected_entity, selected_relation
    
    if not relation_listbox.curselection():
        return
    
    index = relation_listbox.curselection()[0]
    selected_relation = relations[index]
    selected_entity = None
    
    # Aktualisiere die Eigenschaften-Anzeige
    update_entity_listbox()
    update_relation_listbox()

def add_attribute():
    """
    Fügt ein Attribut zur ausgewählten Entität hinzu.
    """
    if not selected_entity:
        messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst eine Entität aus.")
        return
    
    attribute = simpledialog.askstring("Neues Attribut", "Name des Attributs:")
    if attribute:
        selected_entity.attributes.append(attribute)
        draw_entity(selected_entity)
        update_entity_listbox()

def add_method():
    """
    Fügt eine Methode zur ausgewählten Entität hinzu.
    """
    if not selected_entity:
        messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst eine Entität aus.")
        return
    
    method = simpledialog.askstring("Neue Methode", "Name der Methode:")
    if method:
        selected_entity.methods.append(method)
        draw_entity(selected_entity)
        update_entity_listbox()

def update_entity_properties(text_content):
    """
    Aktualisiert die Eigenschaften einer Entität basierend auf dem Text im Eigenschaften-Widget.
    """
    if not selected_entity:
        messagebox.showinfo("Hinweis", "Keine Entität ausgewählt.")
        return
    
    lines = text_content.strip().split("\n")
    
    # Name extrahieren
    name_line = lines[0] if lines else ""
    if name_line.startswith("Name: "):
        selected_entity.name = name_line.replace("Name: ", "").strip()
    
    # Attribute extrahieren
    attributes = []
    in_attributes = False
    for line in lines:
        if line.strip() == "Attribute:":
            in_attributes = True
            continue
        elif line.strip() == "Methoden:":
            in_attributes = False
            continue
        
        if in_attributes and line.strip().startswith("- "):
            attr = line.replace("- ", "").strip()
            if attr:
                attributes.append(attr)
    
    # Methoden extrahieren
    methods = []
    in_methods = False
    for line in lines:
        if line.strip() == "Methoden:":
            in_methods = True
            continue
        
        if in_methods and line.strip().startswith("- "):
            method = line.replace("- ", "").strip()
            if method:
                methods.append(method)
    
    # Aktualisieren der Entität
    selected_entity.attributes = attributes
    selected_entity.methods = methods
    
    # Neuzeichnen
    draw_entity(selected_entity)
    update_entity_listbox()

def update_relation_type(new_type):
    """
    Ändert den Typ einer ausgewählten Beziehung.
    """
    if not selected_relation:
        messagebox.showinfo("Hinweis", "Keine Beziehung ausgewählt.")
        return
    
    if new_type not in ["association", "inheritance", "composition", "aggregation"]:
        messagebox.showinfo("Hinweis", "Ungültiger Beziehungstyp.")
        return
    
    selected_relation.type = new_type
    draw_relation(selected_relation)
    update_relation_listbox()

def save_diagram():
    """
    Speichert das aktuelle Diagramm als JSON-Datei.
    """
    # Ordner erstellen, falls er nicht existiert
    if not os.path.exists(DIAGRAM_DIR):
        os.makedirs(DIAGRAM_DIR)
    
    # Dateinamen über Dialog abfragen
    file_path = filedialog.asksaveasfilename(
        initialdir=DIAGRAM_DIR,
        title="Diagramm speichern",
        defaultextension=".json",
        filetypes=[("JSON-Datei", "*.json")]
    )
    
    if not file_path:
        return
    
    # Daten in Dictionary umwandeln
    data = {
        "entities": [entity.to_dict() for entity in entities],
        "relations": [relation.to_dict() for relation in relations],
        "canvas_size": {
            "width": CANVAS_WIDTH,
            "height": CANVAS_HEIGHT
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Als JSON speichern
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    messagebox.showinfo("Speichern", f"Diagramm wurde gespeichert als:\n{file_path}")

def load_diagram():
    """
    Lädt ein gespeichertes Diagramm aus einer JSON-Datei.
    """
    global entities, relations
    
    # Datei über Dialog auswählen
    file_path = filedialog.askopenfilename(
        initialdir=DIAGRAM_DIR,
        title="Diagramm laden",
        filetypes=[("JSON-Datei", "*.json")]
    )
    
    if not file_path:
        return
    
    try:
        # JSON-Datei laden
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Listen leeren
        entities = []
        relations = []
        
        # Entitäten laden
        for entity_data in data["entities"]:
            entity = Entity.from_dict(entity_data)
            entities.append(entity)
        
        # Beziehungen laden
        for relation_data in data["relations"]:
            relation = Relation.from_dict(relation_data, entities)
            relations.append(relation)
        
        # Canvas-Größe aktualisieren, falls vorhanden
        if "canvas_size" in data:
            global CANVAS_WIDTH, CANVAS_HEIGHT
            CANVAS_WIDTH = data["canvas_size"]["width"]
            CANVAS_HEIGHT = data["canvas_size"]["height"]
            canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
            canvas.config(scrollregion=(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT))
        
        # Alles neu zeichnen
        redraw_all()
        update_entity_listbox()
        update_relation_listbox()
        
        messagebox.showinfo("Laden", f"Diagramm wurde geladen aus:\n{file_path}")
    
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Laden des Diagramms:\n{str(e)}")

def export_diagram():
    """
    Exportiert das aktuelle Diagramm als PNG-Bild.
    """
    # Dateinamen über Dialog abfragen
    file_path = filedialog.asksaveasfilename(
        initialdir=DIAGRAM_DIR,
        title="Diagramm exportieren",
        defaultextension=".png",
        filetypes=[("PNG-Bild", "*.png")]
    )
    
    if not file_path:
        return
    
    try:
        # Bestimme den tatsächlich benutzten Bereich des Canvas
        min_x = min((entity.x for entity in entities), default=0)
        min_y = min((entity.y for entity in entities), default=0)
        max_x = max((entity.x + entity.width for entity in entities), default=CANVAS_WIDTH)
        max_y = max((entity.y + entity.height for entity in entities), default=CANVAS_HEIGHT)
        
        # Füge einen Rand hinzu
        margin = 20
        min_x = max(0, min_x - margin)
        min_y = max(0, min_y - margin)
        max_x = min(CANVAS_WIDTH, max_x + margin)
        max_y = min(CANVAS_HEIGHT, max_y + margin)
        
        # Erstelle ein leeres Bild
        width = max_x - min_x
        height = max_y - min_y
        image = Image.new("RGB", (int(width), int(height)), "white")
        draw = ImageDraw.Draw(image)
        
        # Zeichne alle Entitäten
        for entity in entities:
            # Rechteck zeichnen
            draw.rectangle(
                (entity.x - min_x, entity.y - min_y, 
                 entity.x - min_x + entity.width, entity.y - min_y + entity.height),
                fill="white", outline="black", width=2
            )
            
            # Titel zeichnen
            font = ImageFont.truetype("arial.ttf", 10)
            title_width, title_height = draw.textsize(entity.name, font=font)
            draw.text(
                (entity.x - min_x + entity.width / 2 - title_width / 2, 
                 entity.y - min_y + 15 - title_height / 2),
                entity.name, fill="black", font=font
            )
            
            # Trennlinie nach dem Titel
            draw.line(
                (entity.x - min_x, entity.y - min_y + 30,
                 entity.x - min_x + entity.width, entity.y - min_y + 30),
                fill="black", width=1
            )
            
            # Attribute zeichnen
            y_offset = entity.y - min_y + 35
            for attr in entity.attributes:
                draw.text(
                    (entity.x - min_x + 10, y_offset),
                    attr, fill="black", font=font
                )
                y_offset += 20
            
            # Trennlinie vor den Methoden
            if entity.methods:
                draw.line(
                    (entity.x - min_x, y_offset,
                     entity.x - min_x + entity.width, y_offset),
                    fill="black", width=1
                )
                y_offset += 5
            
            # Methoden zeichnen
            for method in entity.methods:
                draw.text(
                    (entity.x - min_x + 10, y_offset),
                    method, fill="black", font=font
                )
                y_offset += 20
        
        # Zeichne alle Beziehungen
        for relation in relations:
            # Berechne Start- und Endpunkte
            from_x = relation.from_entity.x + relation.from_entity.width / 2 - min_x
            from_y = relation.from_entity.y + relation.from_entity.height / 2 - min_y
            to_x = relation.to_entity.x + relation.to_entity.width / 2 - min_x
            to_y = relation.to_entity.y + relation.to_entity.height / 2 - min_y
            
            # Schnittpunkte mit den Rändern berechnen
            from_x_adj, from_y_adj = calculate_border_point(
                from_x + min_x, from_y + min_y,
                relation.from_entity.x, relation.from_entity.y,
                relation.from_entity.width, relation.from_entity.height,
                to_x + min_x, to_y + min_y
            )
            from_x_adj -= min_x
            from_y_adj -= min_y
            
            to_x_adj, to_y_adj = calculate_border_point(
                to_x + min_x, to_y + min_y,
                relation.to_entity.x, relation.to_entity.y,
                relation.to_entity.width, relation.to_entity.height,
                from_x + min_x, from_y + min_y
            )
            to_x_adj -= min_x
            to_y_adj -= min_y
            
            # Linie zeichnen
            draw.line((from_x_adj, from_y_adj, to_x_adj, to_y_adj), fill="black", width=2)
            
            # Je nach Beziehungstyp entsprechende Enden zeichnen
            if relation.type == "association":
                # Pfeil zeichnen
                arrow_size = 10
                dx = to_x_adj - from_x_adj
                dy = to_y_adj - from_y_adj
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    dx /= length
                    dy /= length
                    draw.polygon(
                        [to_x_adj, to_y_adj,
                         to_x_adj - arrow_size*dx - arrow_size*dy/2,
                         to_y_adj - arrow_size*dy + arrow_size*dx/2,
                         to_x_adj - arrow_size*dx + arrow_size*dy/2,
                         to_y_adj - arrow_size*dy - arrow_size*dx/2],
                        fill="black"
                    )
            
            elif relation.type == "inheritance":
                # Dreieck für Vererbung
                arrow_size = 12
                dx = to_x_adj - from_x_adj
                dy = to_y_adj - from_y_adj
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    dx /= length
                    dy /= length
                    draw.polygon(
                        [to_x_adj, to_y_adj,
                         to_x_adj - arrow_size*dx - arrow_size*dy/2,
                         to_y_adj - arrow_size*dy + arrow_size*dx/2,
                         to_x_adj - arrow_size*dx + arrow_size*dy/2,
                         to_y_adj - arrow_size*dy - arrow_size*dx/2],
                        fill="white", outline="black"
                    )
            
            elif relation.type == "composition":
                # Gefüllte Raute für Komposition
                diamond_size = 10
                dx = to_x_adj - from_x_adj
                dy = to_y_adj - from_y_adj
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    dx /= length
                    dy /= length
                    draw.polygon(
                        [to_x_adj, to_y_adj,
                         to_x_adj - diamond_size*dx - diamond_size*dy/2,
                         to_y_adj - diamond_size*dy + diamond_size*dx/2,
                         to_x_adj - 2*diamond_size*dx,
                         to_y_adj - 2*diamond_size*dy,
                         to_x_adj - diamond_size*dx + diamond_size*dy/2,
                         to_y_adj - diamond_size*dy - diamond_size*dx/2],
                        fill="black", outline="black"
                    )
            
            elif relation.type == "aggregation":
                # Leere Raute für Aggregation
                diamond_size = 10
                dx = to_x_adj - from_x_adj
                dy = to_y_adj - from_y_adj
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    dx /= length
                    dy /= length
                    draw.polygon(
                        [to_x_adj, to_y_adj,
                         to_x_adj - diamond_size*dx - diamond_size*dy/2,
                         to_y_adj - diamond_size*dy + diamond_size*dx/2,
                         to_x_adj - 2*diamond_size*dx,
                         to_y_adj - 2*diamond_size*dy,
                         to_x_adj - diamond_size*dx + diamond_size*dy/2,
                         to_y_adj - diamond_size*dy - diamond_size*dx/2],
                        fill="white", outline="black"
                    )
            
            # Beziehungstyp als Text
            mid_x = (from_x_adj + to_x_adj) / 2
            mid_y = (from_y_adj + to_y_adj) / 2 - 10
            draw.text((mid_x, mid_y), relation.type, fill="blue", font=font)
        
        # Bild speichern
        image.save(file_path)
        messagebox.showinfo("Export", f"Diagramm wurde exportiert als:\n{file_path}")
    
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Exportieren des Diagramms:\n{str(e)}")

def main():
    """
    Hauptfunktion zum Starten der Anwendung.
    """
    root = tk.Tk()
    root.title("LiteDBox UML-Editor")
    root.geometry("1200x800")
    
    # Farben
    bg_color = "#F0F0F0"
    text_bg = "#FFFFFF"
    text_fg = "#000000"
    accent = "#007BFF"
    accent_hover = "#0069D9"
    header_bg = "#E6EFF8"
    
    # Schriftarten
    font = ("Arial", 10)
    font_mono = ("Courier New", 10)
    
    # Tabs erstellen
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    
    # UML-Tab
    uml_tab = tk.Frame(notebook, bg=bg_color)
    notebook.add(uml_tab, text="UML-Diagramm")
    
    # UML-Tab initialisieren
    init_uml_tab(uml_tab, bg_color, text_bg, text_fg, accent, accent_hover, header_bg, font, font_mono)
    
    # Programm starten
    root.mainloop()

if __name__ == "__main__":
    main()