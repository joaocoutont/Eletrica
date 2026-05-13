import unittest
import math
import sys
import os

# Adiciona o diretório raiz ao path para encontrar a EletricaLogic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from EletricaLogic.Calculator import ElectricalCalculator

class TestElectricalCalculator(unittest.TestCase):
    
    def test_calculate_current_monophase(self):
        # P = 1270VA, V = 127V, phases = 1 => I = 10A
        current = ElectricalCalculator.calculate_current(1270, 127, phases=1)
        self.assertAlmostEqual(current, 10.0)

    def test_calculate_current_triphase(self):
        # P = 3810VA, V = 220V, phases = 3 => I = P / (sqrt(3) * V)
        # I = 3810 / (1.732 * 220) = 3810 / 381.04 = ~9.998A
        current = ElectricalCalculator.calculate_current(3810.48, 220, phases=3)
        self.assertAlmostEqual(current, 10.0, places=2)

    def test_get_standard_wire_gauge_b1(self):
        # Para 20A no método B1, deve ser 2.5mm2 (suporta até 21A)
        self.assertEqual(ElectricalCalculator.get_standard_wire_gauge(20, method="B1"), 2.5)
        # Para 22A no método B1, deve ser 4.0mm2 (suporta até 28A)
        self.assertEqual(ElectricalCalculator.get_standard_wire_gauge(22, method="B1"), 4.0)

    def test_calculate_voltage_drop(self):
        # I = 10A, L = 20m, S = 2.5mm2, V = 127V, phases = 1 (k=2), material = Cu (rho=0.0172)
        # deltaV = (2 * 0.0172 * 20 * 10) / 2.5 = 2.752V
        # % = (2.752 / 127) * 100 = 2.1669%
        drop = ElectricalCalculator.calculate_voltage_drop(10, 20, 2.5, 127, phases=1)
        self.assertAlmostEqual(drop, 2.1669, places=4)

    def test_calculate_min_lighting_power(self):
        # Area = 5m2 => 100VA
        self.assertEqual(ElectricalCalculator.calculate_min_lighting_power(5.0), 100.0)
        # Area = 10m2 => 100VA (6m2) + 60VA (restante 4m2) = 160VA
        self.assertEqual(ElectricalCalculator.calculate_min_lighting_power(10.0), 160.0)
        # Area = 15m2 => 100VA (6m2) + 60VA (restante 4m2) + 0VA (sobra 5m2, mas precisa de 4m2 inteiros) = 160VA
        # Wait, 15 - 6 = 9. 9 / 4 = 2.25. floor(2.25) = 2. So 100 + 2*60 = 220VA.
        self.assertEqual(ElectricalCalculator.calculate_min_lighting_power(15.0), 220.0)

    def test_calculate_demand(self):
        # Residencial: 10kVA * 0.6 = 6kVA
        self.assertEqual(ElectricalCalculator.calculate_demand(10000, "Residencial"), 6.0)
        # Industrial: 10kVA * 0.85 = 8.5kVA
        self.assertEqual(ElectricalCalculator.calculate_demand(10000, "Industrial"), 8.5)

    def test_selectivity(self):
        # 32A upstream, 16A downstream => ratio 2.0 >= 1.6 => True
        is_selective, _ = ElectricalCalculator.check_breaker_selectivity(32, 16)
        self.assertTrue(is_selective)
        # 20A upstream, 16A downstream => ratio 1.25 < 1.6 => False
        is_selective, _ = ElectricalCalculator.check_breaker_selectivity(20, 16)
        self.assertFalse(is_selective)

if __name__ == "__main__":
    unittest.main()
