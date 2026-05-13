import os

def find_file(filename, search_path):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

search_paths = [
    r"C:\Program Files\FreeCAD 1.1",
    os.path.join(os.environ["APPDATA"], "FreeCAD")
]

targets = ["BIM_IfcExplorer.svg", "Arch_Reference.svg", "Arch_Site.svg", "Arch_Building.svg"]

found = {}
for target in targets:
    for path in search_paths:
        if os.path.exists(path):
            result = find_file(target, path)
            if result:
                found[target] = result
                break

for name, path in found.items():
    print(f"FOUND: {name} at {path}")
