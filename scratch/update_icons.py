import re
import os

file_path = r'c:\Users\joao.couto\AppData\Roaming\FreeCAD\v1-1\Mod\Eletrica\EletricaGui.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Final exhaustive mapping (Safety, Selectivity, Busbar)
replacements = {
    'RunSafetyAudit': ('SafetyNR10.png', 'Segurança (NR-10)', 'Arco Elétrico'),
    'CheckSelectivity': ('SelectivityPro.png', 'Seletividade', 'Coordenação Amperimétrica'),
    'BusbarSizing': ('Busbar.png', 'Dimensionar Barramento', 'Cu / Al'),
    'RunProjectAudit': ('Audit.png', 'Auditoria Geral', 'Erros'),
}

for class_name, (icon, text, tooltip) in replacements.items():
    pattern = re.compile(rf'(class {class_name}.*?def GetResources\(self\):.*?return \{{)(.*?)(\}})', re.DOTALL)
    new_resources = f" 'Pixmap': os.path.join(ICON_DIR, '{icon}'), 'MenuText': '{text}', 'ToolTip': '{tooltip}' "
    content = pattern.sub(rf'\1{new_resources}\3', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Safety and Audit icons differentiated successfully.")
