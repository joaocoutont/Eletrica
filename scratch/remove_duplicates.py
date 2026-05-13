import re
import os

file_path = r'c:\Users\joao.couto\AppData\Roaming\FreeCAD\v1-1\Mod\Eletrica\EletricaGui.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Target classes to remove (simple versions)
# We know the line ranges from the previous view_file
# DimensionMotorStarter: 345-350
# CheckSelectivity: 357-362

# But I'll use a more robust regex-based approach to find and remove the SIMPLE versions
# Simple versions have only "QtWidgets.QMessageBox.information" in Activated

def is_simple_class(content):
    if "QtWidgets.QMessageBox.information" in content and "QtWidgets.QDialog()" not in content:
        return True
    return False

# Group file into classes
class_blocks = []
current_block = []
in_class = False

for line in lines:
    if line.startswith("class "):
        if current_block:
            class_blocks.append(current_block)
        current_block = [line]
        in_class = True
    elif in_class:
        current_block.append(line)
    else:
        # Top level lines
        class_blocks.append([line])

if current_block:
    class_blocks.append(current_block)

# Filter out simple duplicates
seen_classes = {}
final_blocks = []

for block in class_blocks:
    header = block[0]
    match = re.match(r'class (\w+)', header)
    if match:
        class_name = match.group(1)
        content = "".join(block)
        
        if class_name in seen_classes:
            # We have a duplicate. Keep the complex one.
            old_block = seen_classes[class_name]
            old_content = "".join(old_block)
            
            if is_simple_class(content) and not is_simple_class(old_content):
                # Current is simple, old is complex. Drop current.
                print(f"Dropping simple duplicate of {class_name}")
                continue
            elif not is_simple_class(content) and is_simple_class(old_content):
                # Current is complex, old is simple. Replace old.
                print(f"Replacing simple duplicate of {class_name} with complex version")
                # Remove old from final_blocks
                final_blocks.remove(old_block)
                final_blocks.append(block)
                seen_classes[class_name] = block
            else:
                # Both same complexity or both complex. Keep both (or wait, keep the second one?)
                # Actually, for this task, I'll keep the second one if both are complex.
                final_blocks.append(block)
        else:
            seen_classes[class_name] = block
            final_blocks.append(block)
    else:
        final_blocks.append(block)

with open(file_path, 'w', encoding='utf-8') as f:
    for block in final_blocks:
        f.writelines(block)

print("Duplicates removed successfully.")
