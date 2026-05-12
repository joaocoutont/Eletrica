# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui

# --- CLASSES DE NEGÓCIO E ORÇAMENTO ---
class SyncTitleBlock:
    """Sincroniza o carimbo da folha TechDraw"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Sincronizar Carimbo (Selo)',
            'ToolTip': 'Preenche automaticamente os dados do cliente e RT na folha'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Diagrams import UnifilarGenerator
        selection = FreeCADGui.Selection.getSelection()
        page = next((obj for obj in selection if obj.isDerivedFrom("TechDraw::DrawPage")), None)
        
        if not page:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione uma Folha TechDraw na árvore.")
            return
            
        UnifilarGenerator.sync_title_block(page)

class GenerateBudget:
    """Gera o orçamento financeiro do projeto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Orçamento (R$)',
            'ToolTip': 'Calcula o custo total de materiais do projeto'
        }

    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        from EletricaLogic.Budget import BudgetManager
        from PySide2 import QtWidgets
        
        bom_data = BOMManager.get_bom_data() 
        budget_text = BudgetManager.generate_budget_report(bom_data)
        
        QtWidgets.QMessageBox.information(None, "Orçamento de Materiais", budget_text)

# --- CLASSES DE INSERÇÃO ---
class InsertSocket:
    """Insere tomadas com presets de altura e deteccao de andar"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Tomada (TUG)',
            'ToolTip': 'Insere tomadas em alturas padronizadas (Baixa, Media, Alta)'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Library import LibraryManager
        import FreeCADGui
        
        heights = {"Baixa (0.30m)": 300, "Média (1.10m)": 1100, "Alta (2.10m)": 2100}
        pos, ok = QtWidgets.QInputDialog.getItem(None, "Altura da Tomada", "Selecione a Posicao:", list(heights.keys()), 0, False)
        if not ok: return
        z_offset = heights[pos]
        
        base_z = 0.0
        active_container = None
        selection = FreeCADGui.Selection.getSelection()
        for s in selection:
            if hasattr(s, "InList") and s.isDerivedFrom("App::Part"): 
                base_z = s.Placement.Base.z
                active_container = s
                break
        
        manager = LibraryManager()
        obj = manager.insert_component("Tomada_TUG.FCStd")
        if obj:
            obj.Placement.Base = FreeCAD.Vector(0, 0, base_z + z_offset)
            if active_container:
                active_container.addObject(obj)
            FreeCADGui.runCommand("Draft_Move")

class InsertSwitch:
    """Insere interruptores com definicao de tipo e comando"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Interruptor (Comando)',
            'ToolTip': 'Insere interruptores Simples, Paralelo ou Intermediário'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Lighting import LightingManager
        import FreeCADGui
        
        # 1. Escolher Tipo
        types = ["Simples", "Paralelo", "Intermediário", "Fotocélula", "Sensor de Presença (IR)"]
        stype, ok1 = QtWidgets.QInputDialog.getItem(None, "Interruptor / Sensor", "Tipo:", types, 0, False)
        
        # 2. Definir Letra de Comando
        cmd, ok2 = QtWidgets.QInputDialog.getText(None, "Comando", "Letra do Comando (ex: a, b, c):", text="a")
        
        if ok1 and ok2:
            stype_map = {
                "Simples": "Simples", "Paralelo": "Paralelo", "Intermediário": "Intermediario",
                "Fotocélula": "Fotocelula", "Sensor de Presença (IR)": "Sensor_IR"
            }
            stype_clean = stype_map.get(stype, "Simples")
            LightingManager.insert_switch(stype_clean, cmd)
            FreeCADGui.runCommand("Draft_Move")

class MergeSwitches:
    """Mescla interruptores selecionados em uma placa multitecla"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Mesclar p/ 2 ou 3 Teclas',
            'ToolTip': 'Transforma interruptores proximos em uma placa conjunta'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Lighting import LightingManager
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) < 2: return
        LightingManager.merge_switches(selection)

class InsertLight:
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Inserir Iluminação', 'ToolTip': 'Insere um ponto de luz'}
    def Activated(self):
        FreeCAD.Console.PrintMessage("Inserir Iluminação\n")

# --- CLASSES DE INFRAESTRUTURA ---
class CreateConduit:
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Criar Eletroduto', 'ToolTip': 'Converte linha em tubo'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        selection = FreeCADGui.Selection.getSelection()
        for obj in selection:
            if hasattr(obj, "Points"): ConduitManager.create_conduit(obj.Points)

class BIMifyEquipment:
    """Converte um objeto 3D qualquer em equipamento eletrico inteligente"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'BIMificar Objeto (Tornar Motor/Máquina)',
            'ToolTip': 'Injeta propriedades eletricas e de calculo em qualquer objeto 3D selecionado'
        }

    def Activated(self):
        from EletricaLogic.Equipment import EquipmentManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione o objeto 3D que deseja transformar.")
            return
            
        types = ["Motor Elétrico", "Máquina Industrial", "Ponte Rolante", "Transformador", "Painel Especial"]
        choice, ok = QtWidgets.QInputDialog.getItem(None, "BIMify", "Tipo de Equipamento:", types, 0, False)
        
        if ok:
            for obj in selection:
                EquipmentManager.bimify_equipment(obj, equipment_type=choice)
            
            QtWidgets.QMessageBox.information(None, "Sucesso", "Propriedades elétricas injetadas! Preencha os dados na aba 'Eletrica' do objeto.")

class CreateCableTray:
    def GetResources(self):
        return {'Pixmap': 'freecad', 'MenuText': 'Lançar Eletrocalha', 'ToolTip': 'Cria infra retangular'}
    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        from EletricaLogic.Fittings import FittingManager
        from PySide2 import QtWidgets
        
        materials = ["Aço Galvanizado", "Alumínio", "Aço Inox"]
        mat, ok1 = QtWidgets.QInputDialog.getItem(None, "Material", "Material:", materials, 0, False)
        types = ["Lisa", "Perfurada", "Aramada"]
        ctype, ok2 = QtWidgets.QInputDialog.getItem(None, "Tipo", "Tipo:", types, 1, False)
        supports = ["Teto (Trapézio)", "Teto (Tirante Central)", "Parede", "Nenhum"]
        sup, ok3 = QtWidgets.QInputDialog.getItem(None, "Suporte", "Suporte:", supports, 0, False)
        
        if ok1 and ok2 and ok3:
            FreeCADGui.runCommand("Draft_Wire")
            doc = FreeCAD.ActiveDocument
            last_wire = doc.Objects[-1]
            if hasattr(last_wire, "Points"):
                tray = ConduitManager.create_cable_tray(last_wire.Points, 200, 100)
                FittingManager.add_tray_fittings(tray)
                if sup != "Nenhum":
                    s_type = "Teto_Central" if "Central" in sup else ("Teto_Trapezio" if "Trapézio" in sup else "Parede")
                    FittingManager.add_tray_supports(tray, support_type=s_type)
                doc.removeObject(last_wire.Name)

# --- CLASSES DE CÁLCULO E DOCUMENTAÇÃO ---
class GenerateLoadSchedule:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Quadro de Cargas'}
    def Activated(self): 
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()

class RunProjectAudit:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Auditoria'}
    def Activated(self):
        from EletricaLogic.Auditor import ProjectAuditor
        from PySide2 import QtWidgets
        report = ProjectAuditor.run_full_audit()
        QtWidgets.QMessageBox.information(None, "Auditoria", str(report))

class GenerateUnifilar:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Diagrama Unifilar'}
    def Activated(self):
        from EletricaLogic.Diagrams import UnifilarGenerator
        selection = FreeCADGui.Selection.getSelection()
        panel = next((obj for obj in selection if hasattr(obj, "TipoBIM")), None)
        if panel: UnifilarGenerator.create_graphic_diagram(panel)

class ToggleDashboard:
    """Liga/Desliga o painel lateral de métricas"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Abrir/Fechar Dashboard',
            'ToolTip': 'Alterna a visualização das métricas em tempo real'
        }

    def Activated(self):
        from EletricaPanel import toggle_dashboard
        toggle_dashboard()

class CloneFloor:
    """Clona a rede eletrica de um andar para outro"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Replicar Redes (Andar Tipo)',
            'ToolTip': 'Copia toda a rede eletrica do andar selecionado para outro andar'
        }

    def Activated(self):
        from EletricaLogic.Automation import MultiStoreyManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) < 2:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione o ANDAR ORIGEM e depois o ANDAR DESTINO (BuildingParts).")
            return
            
        MultiStoreyManager.clone_electrical_to_floor(selection[0], selection[1])

class Generate3DWiring:
    """Gera os cabos fisicos 3D dentro da infraestrutura"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Fiação 3D (LOD 500)',
            'ToolTip': 'Desenha os cabos reais dentro dos eletrodutos'
        }

    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        import FreeCADGui
        selection = FreeCADGui.Selection.getSelection()
        for obj in selection:
            WiringManager.generate_3d_cables(obj)

class CreateIndustrialConnection:
    """Insere Sealtub e Prensa-Cabo no final da linha"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Finalizar p/ Motor (Sealtub/Prensa-Cabo)',
            'ToolTip': 'Converte o final da linha em flexível estanque e insere prensa-cabo'
        }

    def Activated(self):
        from EletricaLogic.Fittings import FittingManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione o eletroduto que chega ao motor.")
            return
            
        types = ["PG11", "PG13.5", "PG16", "PG21", "M20", "M25"]
        gland, ok = QtWidgets.QInputDialog.getItem(None, "Prensa-Cabo", "Selecione o Tamanho:", types, 2, False)
        
        if ok:
            for obj in selection:
                FittingManager.add_industrial_termination(obj, gland_type=gland)

class GenerateProjectQR:
    """Gera QR Code para Realidade Aumentada na prancha"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Link de Realidade Aumentada (QR)',
            'ToolTip': 'Cria um QR Code que leva ao modelo 3D no celular'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.AR import ARManager
        selection = FreeCADGui.Selection.getSelection()
        page = next((obj for obj in selection if obj.isDerivedFrom("TechDraw::DrawPage")), None)
        
        if not page:
            from PySide2 import QtWidgets
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione a Folha TechDraw para inserir o QR Code.")
            return
            
        link = ARManager.generate_project_qr_code(page)
        from PySide2 import QtWidgets
        QtWidgets.QMessageBox.information(None, "AR Ready", f"QR Code vinculado à folha!\nLink: {link}")

class InsertSmartDevice:
    """Insere dispositivos de casa inteligente"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Dispositivo Smart / IoT',
            'ToolTip': 'Insere sensores, cameras e hubs de automação'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.SmartHome import SmartHomeManager
        
        presets = SmartHomeManager.get_automation_presets()
        choice, ok = QtWidgets.QInputDialog.getItem(None, "Automação", "Selecione o dispositivo:", list(presets.keys()), 0, False)
        
        if ok:
            SmartHomeManager.insert_smart_device(choice)

class CheckSelectivity:
    """Verifica a coordenacao entre disjuntores"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Verificar Seletividade (Geral x Circuito)',
            'ToolTip': 'Avalia se o disjuntor geral nao vai cair junto com o do circuito'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Calculator import ElectricalCalculator
        
        up, ok1 = QtWidgets.QInputDialog.getInt(None, "Seletividade", "Corrente Disjuntor Geral (A):", 50, 10, 1000, 1)
        down, ok2 = QtWidgets.QInputDialog.getInt(None, "Seletividade", "Corrente Disjuntor Circuito (A):", 20, 10, 1000, 1)
        
        if ok1 and ok2:
            is_ok, msg = ElectricalCalculator.check_breaker_selectivity(up, down)
            QtWidgets.QMessageBox.information(None, "Análise de Seletividade", msg)

class CreatePanel:
    """Comando para criar um quadro de distribuicao ou comando industrial"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Criar Painel (QDC / CCM / CCA)',
            'ToolTip': 'Cria um painel inteligente com fluxo de Força e Comando'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Panels import PanelManager
        
        name, ok1 = QtWidgets.QInputDialog.getText(None, "Novo Painel", "Nome do Painel (ex: CCM-01):")
        if not ok1 or not name: return
        
        types = ["QDC (Distribuição)", "CCM (Motores)", "CCA (Automação)", "Medidores"]
        choice, ok2 = QtWidgets.QInputDialog.getItem(None, "Tipo de Painel", "Função do Painel:", types, 0, False)
        
        if ok2:
            PanelManager.create_panel(name, panel_type=choice)
            FreeCAD.Console.PrintMessage(f"Painel {name} tipo {choice} criado com sucesso.\n")

class GenerateCableSchedule:
    """Gera a lista de cabos industrial (De/Para)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Lista de Cabos (Cable Schedule)',
            'ToolTip': 'Cria uma planilha com Origem, Destino e Comprimento de todos os cabos'
        }

    def Activated(self):
        from EletricaLogic.CableSchedule import CableScheduleManager
        from PySide2 import QtWidgets
        import FreeCAD
        
        sheet_name = CableScheduleManager.export_to_spreadsheet()
        QtWidgets.QMessageBox.information(None, "Lista de Cabos", f"Lista de Cabos gerada com sucesso na planilha: {sheet_name}")

class ServiceEntranceWizard:
    """Assistente para definir o padrao de entrada conforme concessionaria"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Assistente de Padrão de Entrada (Concessionária)',
            'ToolTip': 'Define poste, caixa e disjuntor conforme normas brasileiras'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.ServiceEntrance import ServiceEntranceWizard
        import FreeCAD
        
        # 1. Escolher Concessionaria
        data = ServiceEntranceWizard.get_utilities_data()
        utilities = list(data.keys())
        choice, ok1 = QtWidgets.QInputDialog.getItem(None, "Padrão de Entrada", "Selecione a Concessionária:", utilities, 0, False)
        
        if not ok1: return
        
        # 2. Definir Carga (Tentar obter do projeto ou perguntar)
        kw, ok2 = QtWidgets.QInputDialog.getDouble(None, "Carga", "Carga Instalada Total (kW):", 15.0, 1.0, 500.0, 1)
        
        if ok2:
            obj = ServiceEntranceWizard.create_entrance_point(choice, kw)
            res = ServiceEntranceWizard.recommend_entrance(choice, kw)
            msg = f"Recomendação para {choice}:\n\n"
            msg += f"- Categoria: {res['fase']}\n"
            msg += f"- Disjuntor: {res['disjuntor']}\n"
            msg += f"- Cabo: {res['cabo']}\n"
            msg += f"- Caixa: {res['caixa']}\n"
            QtWidgets.QMessageBox.information(None, "Padrão Definido", msg)

class InsertSubstation:
    """Ferramenta para dimensionar e inserir uma subestacao particular"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Dimensionar Subestação Particular (Aérea/Abrigada)',
            'ToolTip': 'Sugere o tipo de subestacao e protecao com base no kVA'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Substation import SubstationManager
        
        # 1. Escolher Potencia
        kva, ok1 = QtWidgets.QInputDialog.getInt(None, "Subestação MT", "Potência do Transformador (kVA):", 112, 15, 5000, 1)
        if not ok1: return
        
        # 2. Escolher Tensão
        voltages = ["13.8 kV", "34.5 kV"]
        v_choice, ok2 = QtWidgets.QInputDialog.getItem(None, "Tensão Primária", "Média Tensão (MT):", voltages, 0, False)
        
        if ok1 and ok2:
            v_val = 34.5 if "34" in v_choice else 13.8
            SubstationManager.create_substation_bim(kva, voltage_kv=v_val)
            res = SubstationManager.dimension_substation(kva, voltage_kv=v_val)
            
            msg = f"Dimensionamento de Média Tensão ({v_val}kV):\n\n"
            msg += f"- Tipo: {res['Tipo']}\n"
            msg += f"- Estrutura: {res['Estrutura']}\n"
            msg += f"- Proteção: {res['Protecao']}\n"
            msg += f"- Dica: {res['Nota']}\n"
            QtWidgets.QMessageBox.information(None, "Subestação de MT Definida", msg)

# --- REGISTRO DE COMANDOS ---
cmds = {
    'Eletrica_InsertSocket': InsertSocket(),
    'Eletrica_InsertLight': InsertLight(),
    'Eletrica_InsertSwitch': InsertSwitch(),
    'Eletrica_MergeSwitches': MergeSwitches(),
    'Eletrica_CreateConduit': CreateConduit(),
    'Eletrica_CreateCableTray': CreateCableTray(),
    'Eletrica_GenerateLoadSchedule': GenerateLoadSchedule(),
    'Eletrica_GenerateCableSchedule': GenerateCableSchedule(),
    'Eletrica_RunProjectAudit': RunProjectAudit(),
    'Eletrica_GenerateUnifilar': GenerateUnifilar(),
    'Eletrica_SyncTitleBlock': SyncTitleBlock(),
    'Eletrica_GenerateBudget': GenerateBudget(),
    'Eletrica_BIMifyEquipment': BIMifyEquipment(),
    'Eletrica_GenerateProjectQR': GenerateProjectQR(),
    'Eletrica_ServiceEntranceWizard': ServiceEntranceWizard(),
    'Eletrica_InsertSubstation': InsertSubstation(),
    'Eletrica_InsertSmartDevice': InsertSmartDevice(),
    'Eletrica_CheckSelectivity': CheckSelectivity(),
    'Eletrica_CreatePanel': CreatePanel(),
    'Eletrica_CreateIndustrialConnection': CreateIndustrialConnection(),
    'Eletrica_ToggleDashboard': ToggleDashboard(),
    'Eletrica_CloneFloor': CloneFloor(),
    'Eletrica_Generate3DWiring': Generate3DWiring()
}

for name, obj in cmds.items():
    FreeCADGui.addCommand(name, obj)

# (Outros comandos simplificados para manter o arquivo funcional)
class Placeholder:
    def GetResources(self): return {'Pixmap': 'freecad', 'MenuText': 'Comando'}
    def Activated(self): pass

extra_cmds = [
    'Eletrica_OpenSettings', 'Eletrica_AnalyzeSpaceLighting', 'Eletrica_BalancePhases',
    'Eletrica_CalculateWiring', 'Eletrica_PrepareIFC', 'Eletrica_GenerateTags',
    'Eletrica_CheckConduitFill', 'Eletrica_GenerateBOM', 'Eletrica_GenerateWireSymbols',
    'Eletrica_GroundingCalculator', 'Eletrica_SPDAGui', 'Eletrica_SPDARiskWizard',
    'Eletrica_InsertTUE', 'Eletrica_ServiceEntranceWizard', 'Eletrica_CreatePanel', 'Eletrica_InsertServiceEntrance', 'Eletrica_AutoConnectSequence',
    'Eletrica_AutoConnectCeiling', 'Eletrica_ApplyHeatmap', 'Eletrica_AssignCircuitToConduit',
    'Eletrica_ClearConduitCircuits', 'Eletrica_GenerateReport', 'Eletrica_SolarEstimate',
    'Eletrica_GeneratePanelLabels', 'Eletrica_CreateExposedConduit', 'Eletrica_GenerateRiseFallSymbols',
    'Eletrica_AnnotateCircuits', 'Eletrica_ManageBoxes'
]

for name in extra_cmds:
    if name not in cmds:
        FreeCADGui.addCommand(name, Placeholder())
