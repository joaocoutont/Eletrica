import os
import shutil

import FreeCAD as App


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SWITCH_DIR = os.path.join(BASE_DIR, "Library", "3D", "Interruptores")
FILES = [
    "Cx_4x2_S1-.FCStd",
    "Cx_4x2_S2.FCStd",
    "Cx_4x2_S3-.FCStd",
]


def rotate_shape_objects(doc):
    changed = 0
    for obj in list(doc.Objects):
        try:
            shape = getattr(obj, "Shape", None)
            if not shape or shape.isNull():
                continue
            shape = shape.copy()
            center = shape.BoundBox.Center
            shape.rotate(center, App.Vector(0, 0, 1), 180)
            obj.Shape = shape
            changed += 1
        except Exception as exc:
            App.Console.PrintWarning(
                "[Eletrica] Nao foi possivel rotacionar {}: {}\n".format(
                    getattr(obj, "Name", "<obj>"), exc
                )
            )
    return changed


def main():
    for fname in FILES:
        path = os.path.join(SWITCH_DIR, fname)
        if not os.path.exists(path):
            App.Console.PrintWarning("[Eletrica] Arquivo nao encontrado: {}\n".format(path))
            continue

        backup = path + ".orientacao_original.FCBak"
        if not os.path.exists(backup):
            shutil.copy2(path, backup)

        doc = App.openDocument(path, True, True)
        try:
            changed = rotate_shape_objects(doc)
            if changed:
                doc.saveAs(path)
                App.Console.PrintMessage(
                    "[Eletrica] {} rotacionado em 180 graus ({} shape objects).\n".format(
                        fname, changed
                    )
                )
            else:
                App.Console.PrintWarning("[Eletrica] Nenhuma Shape encontrada em {}.\n".format(fname))
        finally:
            App.closeDocument(doc.Name)


if __name__ == "__main__":
    main()
