# Eletrica Workbench for FreeCAD 1.1 ⚡🏭
**The Professional Industrial Electrical Engineering Suite for BIM Workflows**

[![License: LGPL v2.1](https://img.shields.io/badge/License-LGPL%20v2.1-blue.svg)](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)
[![FreeCAD Version](https://img.shields.io/badge/FreeCAD-1.1-orange.svg)](https://www.freecad.org)

## 🇧🇷 Sobre o Projeto
O **Eletrica** é um workbench avançado para o FreeCAD 1.1, focado em transformar o processo de projeto elétrico em um fluxo BIM 7D completo. Desenvolvido para atender desde instalações residenciais até subestações industriais complexas, ele integra cálculos normativos (NBR 5410, 5419, 15751) com modelagem 3D inteligente e gestão de ativos.

## 🇺🇸 About the Project
**Eletrica** is an advanced workbench for FreeCAD 1.1, designed to transform the electrical design process into a full BIM 7D workflow. Built for everything from residential installations to complex industrial substations, it integrates regulatory calculations (IEC standards / NBR) with intelligent 3D modeling and asset management.

---

## 🚀 Principais Recursos / Key Features

### 🏗️ Industrial & High Voltage (MT/BT)
*   **Substation Wizard**: Full design of primary cabins and transformer sizing.
*   **Busbar Sizing**: Automated calculation for copper/aluminum bars in industrial panels.
*   **NBR 15751 Compliance**: Critical grounding analysis for substations (Touch/Step voltages).
*   **Arc Flash Analysis (IEEE 1584)**: Incident energy calculation and safety labeling (NR-10).

### 🤖 Automation & Industry 4.0 (IIoT)
*   **PLC & HMI Integration**: Insert smart controllers with metadata for MQTT, OPC UA, and Profinet.
*   **Network Topology**: Industrial communication protocols selection for IIoT interoperability.
*   **Motor Control Centers (CCM)**: Automated command diagram generation and starter sizing.

### 📐 BIM 7D & Documentation
*   **BIM Asset Management**: Automated QR Code generation for physical equipment maintenance.
*   **Smart Reports**: Professional HTML/PDF export for Grounding, BOM, and Load Schedules.
*   **TechDraw Integration**: Real-time synchronization of Title Blocks and Single-line diagrams.
*   **IFC4 Export**: Full Pset mapping for interoperability with Revit, Navisworks, and Archicad.

### ⚡ Protection & Safety
*   **SPDA (NBR 5419)**: Risk analysis wizard and automated 3D mesh generation.
*   **Circuit Audit**: Real-time verification of voltage drop, overcrowding, and selectivity.

---

## 📦 Instalação / Installation

1.  **Download**: Clone or download this repository.
2.  **Path**: Place the `Eletrica` folder into your FreeCAD User AppData directory:
    *   `%AppData%\FreeCAD\Mod\Eletrica` (Windows)
    *   `~/.local/share/FreeCAD/Mod/Eletrica` (Linux)
3.  **Restart**: Open FreeCAD and select the **Eletrica** workbench.

---

## 🛠️ Tecnologias / Tech Stack
*   **Core**: Python 3.x, FreeCAD API.
*   **GUI**: PySide (Qt), TechDraw SVG.
*   **BIM**: IFC4 Schema, OpenBIM standards.

---

## 📜 Licença / License
Distributed under the LGPL v2.1 License. See `LICENSE` for more information.

---
**Developed with ❤️ for the Electrical Engineering Community.**
