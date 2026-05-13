import re
import os

file_path = r'c:\Users\joao.couto\AppData\Roaming\FreeCAD\v1-1\Mod\Eletrica\EletricaGui.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find class names and their icons
# Pattern: class (\w+):.*?GetResources.*?Pixmap.*?os.path.join\(ICON_DIR, '(.*?)'\)
pattern = re.compile(r'class (\w+):.*?GetResources.*?Pixmap.*?os\.path\.join\(ICON_DIR, \'(.*?)\'\)', re.DOTALL)

matches = pattern.findall(content)

icon_map = {}
for class_name, icon in matches:
    if icon not in icon_map:
        icon_map[icon] = []
    icon_map[icon].append(class_name)

print("Duplicates:")
for icon, classes in icon_map.items():
    if len(classes) > 1:
        print(f"Icon: {icon}")
        for c in classes:
            print(f"  - {c}")
