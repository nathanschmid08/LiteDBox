import os
import json
import shutil

# Basisverzeichnis
BASE_PATH = "C:/LiteDBox"
current_db = None

# Initialisiere LiteDBox-Ordner
def init():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def create_database(name):
    db_path = os.path.join(BASE_PATH, name)
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        print(f"Datenbank '{name}' erstellt.")
    else:
        print(f"Datenbank '{name}' existiert bereits.")

def use_database(name):
    global current_db
    db_path = os.path.join(BASE_PATH, name)
    if os.path.exists(db_path):
        current_db = db_path
        print(f"Verbundene Datenbank: '{name}'")
    else:
        print(f"Datenbank '{name}' existiert nicht.")

def create_table(name, columns):
    if not current_db:
        return "Keine Datenbank ausgewählt."

    path = os.path.join(current_db, f"{name}.json")
    if os.path.exists(path):
        return f"Tabelle '{name}' existiert bereits."

    table_data = {
        "columns": columns,
        "data": []
    }

    try:
        with open(path, "w") as f:
            json.dump(table_data, f, indent=2)
        return f"Tabelle '{name}' erstellt mit Spalten: {', '.join(columns)}"
    except Exception as e:
        return f"Fehler beim Erstellen der Tabelle: {str(e)}"


def insert_into(table, values):
    if not current_db:
        print("Keine Datenbank ausgewählt.")
        return
    
    path = os.path.join(current_db, f"{table}.json")
    if not os.path.exists(path):
        print(f"Tabelle '{table}' existiert nicht.")
        return
    
    with open(path, "r") as f:
        content = json.load(f)
    
    columns = content["columns"]
    if len(values) != len(columns):
        print("Spaltenanzahl stimmt nicht mit Werten überein.")
        return

    cleaned_values = [v.strip().replace('"', '').replace("'", '') for v in values]
    row = dict(zip(columns, cleaned_values))
    content["data"].append(row)

    with open(path, "w") as f:
        json.dump(content, f, indent=2)

    print(f"Eintrag hinzugefügt: {row}")

def update_table(table, column, old_value, new_value):
    if not current_db:
        print("Keine Datenbank ausgewählt.")
        return
    
    path = os.path.join(current_db, f"{table}.json")
    if not os.path.exists(path):
        print(f"Tabelle '{table}' existiert nicht.")
        return

    with open(path, "r") as f:
        content = json.load(f)

    updated = 0
    for row in content["data"]:
        if row.get(column) == old_value:
            row[column] = new_value
            updated += 1

    with open(path, "w") as f:
        json.dump(content, f, indent=2)
    
    print(f"{updated} Einträge aktualisiert.")

def delete_from(table, column, value):
    if not current_db:
        return "Keine Datenbank ausgewählt."

    path = os.path.join(current_db, f"{table}.json")
    if not os.path.exists(path):
        return f"Tabelle '{table}' existiert nicht."

    with open(path, "r") as f:
        content = json.load(f)

    before = len(content["data"])
    content["data"] = [row for row in content["data"] if row.get(column) != value]
    after = len(content["data"])

    with open(path, "w") as f:
        json.dump(content, f, indent=2)

    return f"{before - after} Einträge gelöscht."

def drop_database(name):
    db_path = os.path.join(BASE_PATH, name)
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        print(f"Datenbank '{name}' gelöscht.")
    else:
        print(f"Datenbank '{name}' existiert nicht.")

def drop_table(name):
    if not current_db:
        print("Keine Datenbank ausgewählt.")
        return

    path = os.path.join(current_db, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        print(f"Tabelle '{name}' gelöscht.")
    else:
        print(f"Tabelle '{name}' existiert nicht.")

def select_from(table, column=None, value=None):
    if not current_db:
        return "Keine Datenbank ausgewählt."

    path = os.path.join(current_db, f"{table}.json")
    if not os.path.exists(path):
        return f"Tabelle '{table}' existiert nicht."

    with open(path, "r") as f:
        content = json.load(f)

    results = []
    for row in content["data"]:
        if column and value:
            if row.get(column) == value:
                results.append(row)
        else:
            results.append(row)

    return results

def drop_table(name):
    if not current_db:
        return "Keine Datenbank ausgewählt."
    
    path = os.path.join(current_db, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return f"Tabelle '{name}' wurde gelöscht."
    else:
        return f"Tabelle '{name}' existiert nicht."

def drop_database(name):
    db_path = os.path.join(BASE_PATH, name)
    global current_db
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        if current_db == db_path:
            current_db = None
        return f"Datenbank '{name}' wurde gelöscht."
    else:
        return f"Datenbank '{name}' existiert nicht."

def update_entry(table, condition_column, condition_value, new_value, set_column):
    if not current_db:
        return "Keine Datenbank ausgewählt."

    path = os.path.join(current_db, f"{table}.json")
    if not os.path.exists(path):
        return f"Tabelle '{table}' existiert nicht."

    with open(path, "r") as f:
        content = json.load(f)

    updated = 0
    for row in content["data"]:
        if row.get(condition_column) == condition_value:
            row[set_column] = new_value
            updated += 1

    with open(path, "w") as f:
        json.dump(content, f, indent=2)

    return f"{updated} Einträge aktualisiert."

def handle_sql(statement, tree=None):
    response = ""
    statement = statement.strip()

    if statement.lower().startswith("create database"):
        _, _, name = statement.partition("create database")
        response = create_database(name.strip())

    elif statement.lower().startswith("use"):
        _, _, name = statement.partition("use")
        response = use_database(name.strip())

    elif statement.lower().startswith("create table"):
        parts = statement.strip().split(maxsplit=2)
        if len(parts) < 3:
            response = "Syntax: create table <name> (spalte1, spalte2, ...)"
        else:
            rest = parts[2].strip().replace("(", "").replace(")", "").replace(",", " ")
            sub_parts = rest.split()
            name = sub_parts[0]
            cols = sub_parts[1:]
            response = create_table(name, cols)

    elif statement.lower().startswith("insert into"):
        parts = statement.strip().split("values")
        if len(parts) != 2:
            response = "Syntax: insert into <tabelle> values (wert1, wert2, ...)"
        else:
            table_part = parts[0].strip().split()
            value_part = parts[1].strip()
            table_name = table_part[2]
            value_part = value_part.replace("(", "").replace(")", "")
            values = [v.strip().strip('"').strip("'") for v in value_part.split(",")]
            response = insert_into(table_name, values)

    elif statement.lower().startswith("select"):
        parts = statement.strip().split()
        if len(parts) >= 4 and parts[1] == "*" and parts[2].lower() == "from":
            table_name = parts[3]
            if "where" in parts:
                where_index = parts.index("where")
                column = parts[where_index + 1]
                value = parts[where_index + 3].strip('"').strip("'")
                data = select_from(table_name, column, value)
            else:
                data = select_from(table_name)

            if tree:
                # TreeView aktualisieren
                tree.delete(*tree.get_children())
                if data:
                    tree["columns"] = list(data[0].keys())
                    tree["show"] = "headings"
                    for col in data[0].keys():
                        tree.heading(col, text=col)
                    for row in data:
                        tree.insert("", "end", values=list(row.values()))
                    response = f"{len(data)} Einträge gefunden."
                else:
                    response = "Keine Daten gefunden."
            else:
                response = data

        else:
            response = "Syntax: select * from <tabelle> [where <spalte> = <wert>]"

    elif statement.lower().startswith("update"):
        try:
            parts = statement.strip().split("set")
            table_name = parts[0].strip().split()[1].strip()
            set_part, where_part = parts[1].strip().split("where")
            set_column, new_value = set_part.strip().split("=")
            condition_column, condition_value = where_part.strip().split("=")
            new_value = new_value.strip().strip('"').strip("'")
            condition_value = condition_value.strip().strip('"').strip("'")

            response = update_entry(
                table_name,
                condition_column.strip(),
                condition_value,
                new_value,
                set_column.strip()
            )
        except Exception as e:
            response = f"Fehlerhafte Update-Syntax: {str(e)}"

    elif statement.lower().startswith("delete from"):
        try:
            parts = statement.strip().split("where")
            table_part = parts[0].strip().split()
            table_name = table_part[2]
            condition_column, condition_value = parts[1].strip().split("=")
            condition_value = condition_value.strip().strip('"').strip("'")
            response = delete_from(table_name, condition_column.strip(), condition_value)
        except Exception as e:
            response = f"Fehlerhafte Delete-Syntax: {str(e)}"

    elif statement.lower().startswith("drop table"):
        _, _, name = statement.partition("drop table")
        response = drop_table(name.strip())

    elif statement.lower().startswith("drop database"):
        _, _, name = statement.partition("drop database")
        response = drop_database(name.strip())

    else:
        response = "Unbekanntes Statement."

    return response
