import os
import sys
import types
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if "FreeCAD" not in sys.modules:
    sys.modules["FreeCAD"] = types.SimpleNamespace(ActiveDocument=None)

from EletricaLogic.Settings import ProjectSettings


class TestProjectSettings(unittest.TestCase):
    def test_parse_voltage_plain_values(self):
        self.assertEqual(ProjectSettings.parse_voltage("220V"), 220.0)
        self.assertEqual(ProjectSettings.parse_voltage(380), 380.0)

    def test_parse_voltage_composite_values(self):
        self.assertEqual(ProjectSettings.parse_voltage("127/220V"), 220.0)
        self.assertEqual(ProjectSettings.parse_voltage("3F+N (380/220V)"), 220.0)

    def test_parse_voltage_medium_voltage(self):
        self.assertEqual(ProjectSettings.parse_voltage("13.8kV"), 13800.0)

    def test_format_voltage(self):
        self.assertEqual(ProjectSettings.format_voltage(220), "220V")
        self.assertEqual(ProjectSettings.format_voltage(13800), "13.8kV")


if __name__ == "__main__":
    unittest.main()
