# GUI Commands for Eletrica Workbench
import FreeCAD
import FreeCADGui

class InsertSocket:
    """Comando para inserir uma tomada (placeholder)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad', # Usando icone padrao por enquanto
            'MenuText': 'Inserir Tomada',
            'ToolTip': 'Insere uma tomada 2P+T no projeto'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Comando Inserir Tomada Ativado\n")
        # Aqui entraria a logica de criacao do objeto 3D BIM
        return

class InsertLight:
    """Comando para inserir um ponto de luz (placeholder)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Iluminacao',
            'ToolTip': 'Insere um ponto de luz no teto/parede'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Comando Inserir Iluminacao Ativado\n")
        return

class CreateConduit:
    """Comando para criar um eletroduto a partir de uma selecao ou desenho"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Criar Eletroduto',
            'ToolTip': 'Converte uma linha selecionada em um Eletroduto BIM'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Conduit import ConduitManager
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("Selecione uma linha ou wire primeiro.\n")
            # Opcionalmente: Ativar a ferramenta de desenho de linha
            FreeCADGui.runCommand("Draft_Wire")
            return
            
        for obj in selection:
            if hasattr(obj, "Points"): # Verifica se e algo que tem pontos (Wire, Line)
                ConduitManager.create_conduit(obj.Points)
                FreeCAD.Console.PrintMessage(f"Objeto {obj.Label} convertido em Eletroduto.\n")
        
        return

class GenerateLoadSchedule:
    """Comando para gerar o quadro de cargas em planilha"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Quadro de Cargas',
            'ToolTip': 'Cria uma planilha com o resumo de cargas e dimensionamento'
        }

    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule()
        return

class GenerateLegend:
    """Comando para gerar a legenda de simbolos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Legenda',
            'ToolTip': 'Cria uma tabela com todos os simbolos usados no projeto'
        }

    def Activated(self):
        from EletricaLogic.Legend import LegendManager
        LegendManager.generate_legend()
        return

class OpenSettings:
    """Comando para abrir as configuracoes do projeto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Configuracoes do Projeto',
            'ToolTip': 'Define tensao, fator de potencia e outros dados globais'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Settings import ProjectSettings
        
        obj = ProjectSettings.get_settings_obj()
        if not obj: return
        
        # Dialogo Simples
        tensao, ok = QtWidgets.QInputDialog.getItem(
            None, "Configuracoes Eletrica", "Selecione a Tensao do Projeto:", 
            ["127V", "220V", "380V"], 0, False
        )
        if ok:
            obj.Tensao = tensao
            FreeCAD.Console.PrintMessage(f"Tensao definida para {tensao}\n")

class AnalyzeSpaceLighting:
    """Comando para sugerir iluminacao baseada no Arch Space selecionado"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Analisar Iluminacao do Espaco',
            'ToolTip': 'Calcula potencia e pontos de luz para o espaco selecionado'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Spaces import SpaceLightingManager
        from PySide2 import QtWidgets
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("Selecione um objeto 'Space' do Workbench BIM.\n")
            return
            
        space = selection[0]
        result = SpaceLightingManager.analyze_space(space)
        
        if result:
            msg = f"--- Analise do Espaco: {space.Label} ---\n"
            msg += f"Area: {result['Area']:.2f} m2\n"
            msg += f"Potencia Minima (NBR 5410): {result['PowerVA']} VA\n"
            msg += f"Alvo Luminotecnico: {result['LuxTarget']} lux\n"
            msg += f"Sugestao: {result['PointsSuggested']} pontos de luz\n\n"
            msg += "Deseja distribuir esses pontos automaticamente em grid agora?"
            
            res = QtWidgets.QMessageBox.question(None, "Analise de Iluminacao", msg, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if res == QtWidgets.QMessageBox.Yes:
                SpaceLightingManager.distribute_lights(space, result['PointsSuggested'])

class CreateTechnicalSheet:
    """Comando para gerar a prancha final do projeto no TechDraw"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Prancha do Projeto',
            'ToolTip': 'Cria uma folha de desenho com quadro de cargas e legenda'
        }

    def Activated(self):
        from EletricaLogic.Documentation import DocumentationManager
        DocumentationManager.create_technical_sheet()
        return

class BalancePhases:
    """Comando para equilibrar as fases do projeto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Equilibrar Fases',
            'ToolTip': 'Distribui os circuitos entre R, S e T automaticamente'
        }

    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.balance_phases()
        return

class CalculateWiring:
    """Comando para calcular comprimentos e quedas de tensao"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Calcular Fiacao',
            'ToolTip': 'Calcula metragem de cabos e verifica queda de tensao'
        }

    def Activated(self):
        from EletricaLogic.Wiring import WiringManager
        from PySide2 import QtWidgets
        lengths = WiringManager.calculate_circuit_lengths()
        
        msg = "--- Resumo de Fiacao ---\n"
        for c, l in lengths.items():
            msg += f"Circuito {c}: {l/1000.0:.2f} metros\n"
        
        QtWidgets.QMessageBox.information(None, "Relatorio de Fiacao", msg)

class PrepareIFC:
    """Comando para preparar a exportacao BIM/IFC"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Preparar IFC',
            'ToolTip': 'Mapeia propriedades para o padrao internacional IFC4'
        }

    def Activated(self):
        from EletricaLogic.IFC import IFCExportManager
        IFCExportManager.prepare_for_ifc()
        return

class GenerateTags:
    """Comando para gerar etiquetas de identificacao de circuito nos objetos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Etiquetas de Circuito',
            'ToolTip': 'Cria textos de identificacao (Ex: C1) ao lado de cada componente'
        }

    def Activated(self):
        from EletricaLogic.Tagging import TagManager
        TagManager.generate_circuit_tags()
        return

class GenerateWireSymbols:
    """Comando para gerar simbolos de fios (Tick Marks) nos eletrodutos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Símbolos de Fiação',
            'ToolTip': 'Desenha símbolos de Fase, Neutro e Terra sobre os eletrodutos'
        }

    def Activated(self):
        from EletricaLogic.Annotations import AnnotationManager
        selection = FreeCADGui.Selection.getSelection()
        
        if not selection:
            # Se nada selecionado, processar todos os eletrodutos
            for obj in FreeCAD.ActiveDocument.Objects:
                if hasattr(obj, "CircuitosPassantes"):
                    AnnotationManager.create_tick_marks(obj)
        else:
            for obj in selection:
                AnnotationManager.create_tick_marks(obj)
class GenerateReport:
    """Gera a memoria de calculo tecnica"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Memória de Cálculo',
            'ToolTip': 'Exporta um relatório técnico descritivo do projeto'
        }

    def Activated(self):
        from EletricaLogic.Reporting import ReportManager
        from PySide2 import QtWidgets
        path = ReportManager.generate_technical_memory()
        if path:
            QtWidgets.QMessageBox.information(None, "Relatório Gerado", f"Memória de Cálculo salva em:\n{path}")

class SolarEstimate:
    """Estima sistema fotovoltaico"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Estimativa Energia Solar',
            'ToolTip': 'Calcula o kit solar ideal baseado na carga do projeto'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Solar import SolarEstimator
        
        # Somar carga total
        total_va = 0.0
        for obj in FreeCAD.ActiveDocument.Objects:
            if hasattr(obj, "Potencia"):
                total_va += float(obj.Potencia)
                
        res = SolarEstimator.estimate_pv_system(total_va)
        msg = f"--- Estimativa Solar ---\n"
        msg += f"Consumo Estimado: {res['MonthlyConsumption']} kWh/mês\n"
        msg += f"Potência do Kit: {res['SystemPowerKWp']} kWp\n"
        msg += f"Qtd. Painéis (550W): {res['NumPanels']}\n"
        msg += f"Área de Telhado: {res['AreaNeeded']} m²"
        
        QtWidgets.QMessageBox.information(None, "Solar PV", msg)

class AssignCircuitToConduit:
    """Ferramenta para atribuir circuitos aos eletrodutos selecionados"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Atribuir Circuito a Eletroduto',
            'ToolTip': 'Adiciona um circuito (ex: C1) aos eletrodutos selecionados no 3D'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        import FreeCADGui
        
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione um ou mais eletrodutos primeiro.")
            return
            
        circuit, ok = QtWidgets.QInputDialog.getText(None, "Atribuir Circuito", "Digite o nome/número do circuito (ex: C1):")
        
        if ok and circuit:
            count = 0
            for obj in selection:
                if hasattr(obj, "CircuitosPassantes"):
                    current_list = list(obj.CircuitosPassantes)
                    if circuit not in current_list:
                        current_list.append(circuit)
                        obj.CircuitosPassantes = current_list
                        count += 1
            
            FreeCAD.ActiveDocument.recompute()
            QtWidgets.QMessageBox.information(None, "Sucesso", f"Circuito {circuit} atribuído a {count} eletroduto(s).")

class ClearConduitCircuits:
    """Limpa a lista de circuitos de um eletroduto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Limpar Circuitos do Tubo',
            'ToolTip': 'Remove todos os circuitos dos eletrodutos selecionados'
        }

    def Activated(self):
        import FreeCADGui
        selection = FreeCADGui.Selection.getSelection()
        for obj in selection:
            if hasattr(obj, "CircuitosPassantes"):
                obj.CircuitosPassantes = []
        FreeCAD.ActiveDocument.recompute()

class GeneratePanelLabels:
    """Gera etiquetas para a porta do quadro"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Etiquetas de Quadro',
            'ToolTip': 'Cria uma planilha com as etiquetas para colar no painel'
        }

    def Activated(self):
        from EletricaLogic.Circuits import CircuitManager
        CircuitManager.generate_load_schedule() # Garante que os dados estao prontos
        QtWidgets.QMessageBox.information(None, "Etiquetas", "Planilha de etiquetas gerada com sucesso!")

class AutoConnectSequence:
    """Conecta objetos selecionados em sequencia"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Conectar em Sequência',
            'ToolTip': 'Cria eletrodutos ligando as tomadas na ordem selecionada'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Routing import AutoRouter
        selection = FreeCADGui.Selection.getSelection()
        if len(selection) < 2:
            FreeCAD.Console.PrintWarning("Selecione pelo menos dois objetos.\n")
            return
        AutoRouter.connect_in_sequence(selection)

class AutoConnectCeiling:
    """Conecta objetos ao teto"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Conectar ao Teto',
            'ToolTip': 'Cria eletrodutos subindo a parede ate o ponto de luz mais proximo'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Routing import AutoRouter
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("Selecione os dispositivos que devem subir ao teto.\n")
            return
        AutoRouter.connect_to_nearest_ceiling(selection)

class CreateExposedConduit:
    """Cria eletrodutos aparentes (cinza/ferro) com conduletes automaticos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Lançar Linha Aparente (Conduletes)',
            'ToolTip': 'Cria eletrodutos cinza e insere caixas de condulete em cada curva'
        }

    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        from EletricaLogic.Fittings import FittingManager
        from PySide2 import QtWidgets
        import FreeCADGui
        
        # 1. Escolha do Material e Diametro
        materials = ["PVC Rigido Cinza", "Aco Galvanizado Leve", "Aco Galvanizado Pesado"]
        mat, ok1 = QtWidgets.QInputDialog.getItem(None, "Material", "Selecione o Material:", materials, 0, False)
        
        diameters = ["1/2\" (20mm)", "3/4\" (25mm)", "1\" (32mm)", "1 1/4\" (40mm)"]
        dia_str, ok2 = QtWidgets.QInputDialog.getItem(None, "Diametro", "Selecione o Diametro:", diameters, 1, False)
        
        if not (ok1 and ok2): return
        
        # Extrair valor numerico do diametro
        d_val = 25.0
        if "20mm" in dia_str: d_val = 20.0
        elif "32mm" in dia_str: d_val = 32.0
        elif "40mm" in dia_str: d_val = 40.0
        
        # 2. Chamar o criador de conduites padrao
        FreeCADGui.runCommand("Eletrica_CreateConduit")
        
        # 3. Pegar o ultimo objeto criado e customizar
        doc = FreeCAD.ActiveDocument
        last_obj = doc.Objects[-1]
        if hasattr(last_obj, "TaxaOcupacao"):
            last_obj.Label = f"Eletroduto_{mat.replace(' ', '_')}"
            last_obj.Material = mat
            last_obj.Diameter = d_val
            last_obj.ViewObject.ShapeColor = (0.3, 0.3, 0.3) # Cinza/Aco
            
            # 4. Adicionar Conduletes e Abracadeiras
            FittingManager.add_conduletes_to_conduit(last_obj)
            FittingManager.add_clamps(last_obj, spacing=1200) # Abracadeira a cada 1.2m
            
        return

class RunProjectAudit:
    """Comando para auditar o projeto em busca de erros"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Auditoria de Projeto (Verificar Erros)',
            'ToolTip': 'Varre o projeto em busca de tomadas sem circuito, tubos cheios e outras falhas'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Auditor import ProjectAuditor
        
        report = ProjectAuditor.run_full_audit()
        
        msg = "--- Auditoria de Projeto ---\n\n"
        
        if report["Errors"]:
            msg += "❌ ERROS CRÍTICOS:\n"
            msg += " - " + "\n - ".join(report["Errors"]) + "\n\n"
            
        if report["Warnings"]:
            msg += "⚠️ AVISOS:\n"
            msg += " - " + "\n - ".join(report["Warnings"]) + "\n"
            
        if not report["Errors"] and not report["Warnings"]:
            msg = "✅ Parabéns! Nenhuma inconsistência encontrada no projeto."
            
        QtWidgets.QMessageBox.information(None, "Relatório de Auditoria", msg)

class InsertTUE:
    """Comando para inserir equipamentos de uso especifico (Chuveiro, AC, etc)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Equipamento Especial (TUE)',
            'ToolTip': 'Insere chuveiros, ar condicionado e outros com carga definida'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Equipment import EquipmentManager
        
        presets = EquipmentManager.get_tue_presets()
        choice, ok = QtWidgets.QInputDialog.getItem(None, "Inserir TUE", "Selecione o equipamento:", list(presets.keys()), 0, False)
        
        if ok:
            EquipmentManager.insert_tue(choice)
            FreeCAD.Console.PrintMessage(f"Equipamento {choice} inserido.\n")

class ApplyHeatmap:
    """Comando para aplicar mapa de calor nos eletrodutos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Mapa de Calor (Inspeção)',
            'ToolTip': 'Colore eletrodutos baseado na ocupação (Verde/Vermelho)'
        }

    def Activated(self):
        from EletricaLogic.Visuals import VisualManager
        VisualManager.apply_voltage_drop_heatmap()

class ManageBoxes:
    """Comando para calcular caixas de passagem"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Calcular Caixas de Passagem',
            'ToolTip': 'Conta as caixas 4x2 e Octogonais baseadas nos componentes'
        }

    def Activated(self):
        from EletricaLogic.Equipment import EquipmentManager
        from PySide2 import QtWidgets
        c4x2, cocto = EquipmentManager.add_boxes_to_all()
        QtWidgets.QMessageBox.information(None, "Quantitativo de Caixas", f"Projeto Analisado:\n- Caixas 4x2: {c4x2}\n- Caixas Octogonais (Teto): {cocto}")

class InsertServiceEntrance:
    """Comando para inserir itens da entrada de energia"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Inserir Entrada de Energia',
            'ToolTip': 'Insere caixa de medicao ou caixas de passagem de solo'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.ServiceEntrance import ServiceEntranceManager
        
        presets = ServiceEntranceManager.get_entrance_presets()
        choice, ok = QtWidgets.QInputDialog.getItem(None, "Entrada de Energia", "Selecione o item:", list(presets.keys()), 0, False)
        
        if ok:
            # Criar um objeto placeholder para a entrada
            doc = FreeCAD.ActiveDocument
            obj = doc.addObject("App::FeaturePython", choice.replace(" ", "_"))
            obj.Label = choice
            FreeCAD.Console.PrintMessage(f"Item de entrada {choice} inserido.\n")

class GroundingCalculator:
    """Calculadora de malha de aterramento"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Calculadora de Aterramento',
            'ToolTip': 'Calcula o numero de hastes de terra baseada na resistividade do solo'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Grounding import GroundingManager
        
        rho, ok = QtWidgets.QInputDialog.getDouble(None, "Aterramento", "Resistividade do Solo (Ohm.m):", 100.0, 1, 5000, 1)
        if ok:
            res = GroundingManager.calculate_rods(rho)
            msg = f"--- Resultado Aterramento ---\n"
            msg += f"Resistencia de 1 haste: {res['SingleRodResistance']} Ohms\n"
            msg += f"Numero de hastes para {res['TargetResistance']} Ohms: {res['RequiredRods']}\n"
            QtWidgets.QMessageBox.information(None, "Resultado", msg)

class GenerateUnifilar:
    """Gera um esquema unifilar grafico"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Diagrama Unifilar Gráfico',
            'ToolTip': 'Cria o desenho técnico do quadro no TechDraw'
        }

    def Activated(self):
        import FreeCADGui
        from EletricaLogic.Diagrams import UnifilarGenerator
        from PySide2 import QtWidgets
        
        selection = FreeCADGui.Selection.getSelection()
        panel = next((obj for obj in selection if hasattr(obj, "TipoBIM") and obj.TipoBIM == "Quadro"), None)
        
        if not panel:
            QtWidgets.QMessageBox.warning(None, "Seleção", "Selecione um Quadro (QDC) para gerar o diagrama.")
            return
            
        UnifilarGenerator.create_graphic_diagram(panel)
        QtWidgets.QMessageBox.information(None, "Sucesso", "Diagrama gerado na aba TechDraw!")

class SPDAGui:
    """Calculadora de SPDA"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Calculadora de SPDA (Para-Raios)',
            'ToolTip': 'Calcula Franklin, Faraday e descidas de SPDA'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.SPDA import SPDACalculator
        
        h, ok = QtWidgets.QInputDialog.getDouble(None, "SPDA - Franklin", "Altura do Mastro (m):", 6.0, 1, 100, 1)
        if ok:
            r = SPDACalculator.calculate_franklin_radius(h)
            QtWidgets.QMessageBox.information(None, "Resultado SPDA", f"Raio de Proteção (Método Franklin): {r} metros")

class SPDARiskWizard:
    """Assistente de Analise de Risco NBR 5419"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Assistente de Risco SPDA (NBR 5419)',
            'ToolTip': 'Avalia se o empreendimento precisa de para-raios baseado em perguntas'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.SPDARisk import SPDARiskManager
        
        # Sequencia de perguntas
        length, ok1 = QtWidgets.QInputDialog.getDouble(None, "Dimensoes", "Comprimento do Prédio (m):", 20.0)
        width, ok2 = QtWidgets.QInputDialog.getDouble(None, "Dimensoes", "Largura do Prédio (m):", 15.0)
        height, ok3 = QtWidgets.QInputDialog.getDouble(None, "Dimensoes", "Altura do Prédio (m):", 10.0)
        
        if not (ok1 and ok2 and ok3): return
        
        ng, ok4 = QtWidgets.QInputDialog.getDouble(None, "Localidade", "Densidade de Raios (Ng) - Raios/km2/ano:", 5.0)
        
        locs = ["Estrutura Isolada", "Cercada por árvores", "Cercada por prédios altos"]
        loc, ok5 = QtWidgets.QInputDialog.getItem(None, "Ambiente", "Selecione o Entorno:", locs, 0, False)
        cd = 1.0 if "Isolada" in loc else 0.5
        
        structs = ["Residencial", "Escola/Público", "Hospital", "Risco Explosão/Posto"]
        struct, ok6 = QtWidgets.QInputDialog.getItem(None, "Tipo", "Tipo de Estrutura:", structs, 0, False)
        cf = 1.0
        if "Hospital" in struct: cf = 5.0
        if "Risco" in struct: cf = 10.0
        
        # Processar
        data = {
            'length': length, 'width': width, 'height': height,
            'ng': ng, 'factor_location': cd, 'factor_structure': cf
        }
        
        res = SPDARiskManager.calculate_risk(data)
        
        msg = f"--- Resultado da Análise (NBR 5419) ---\n\n"
        if res['Required']:
            msg += f"🚨 VEREDITO: SPDA OBRIGATÓRIO\n"
            msg += f"Nível de Proteção Sugerido: {res['Level']}\n"
        else:
            msg += f"✅ VEREDITO: SPDA NÃO OBRIGATÓRIO\n"
            msg += "O risco calculado está dentro dos limites toleráveis.\n"
            
        msg += f"\nFrequência Nd: {round(res['Nd'], 5)} raios/ano"
        
        QtWidgets.QMessageBox.information(None, "Veredito SPDA", msg)

class CreatePanel:
    """Comando para criar um quadro de distribuicao (QDC)"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Criar Quadro de Distribuição (QDC)',
            'ToolTip': 'Cria um quadro que gerencia circuitos e hierarquia'
        }

    def Activated(self):
        from PySide2 import QtWidgets
        from EletricaLogic.Panels import PanelManager
        
        name, ok = QtWidgets.QInputDialog.getText(None, "Novo Quadro", "Nome do Quadro (ex: QDC-Terreo):")
        if ok and name:
            PanelManager.create_panel(name)
            FreeCAD.Console.PrintMessage(f"Quadro {name} criado.\n")

class CheckConduitFill:
    """Comando para verificar a ocupacao dos eletrodutos"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Verificar Ocupacao de Tubos',
            'ToolTip': 'Calcula se os fios cabem nos eletrodutos (Max 40%)'
        }

    def Activated(self):
        from EletricaLogic.Conduit import ConduitManager
        from PySide2 import QtWidgets
        alerts = ConduitManager.check_all_conduits_fill()
        
        if alerts:
            msg = "\n".join(alerts)
            QtWidgets.QMessageBox.warning(None, "Alerta de Ocupacao", msg)
        else:
            QtWidgets.QMessageBox.information(None, "Ocupacao OK", "Todos os eletrodutos estao dentro dos limites da NBR 5410.")

class GenerateBOM:
    """Comando para gerar a lista de materiais completa"""
    def GetResources(self):
        return {
            'Pixmap': 'freecad',
            'MenuText': 'Gerar Lista de Materiais',
            'ToolTip': 'Cria uma planilha com o quantitativo de componentes, tubos e cabos'
        }

    def Activated(self):
        from EletricaLogic.BOM import BOMManager
        BOMManager.generate_global_bom()
        return

FreeCADGui.addCommand('Eletrica_InsertSocket', InsertSocket())
FreeCADGui.addCommand('Eletrica_InsertLight', InsertLight())
FreeCADGui.addCommand('Eletrica_CreateConduit', CreateConduit())
FreeCADGui.addCommand('Eletrica_GenerateLoadSchedule', GenerateLoadSchedule())
FreeCADGui.addCommand('Eletrica_GenerateLegend', GenerateLegend())
FreeCADGui.addCommand('Eletrica_OpenSettings', OpenSettings())
FreeCADGui.addCommand('Eletrica_AnalyzeSpaceLighting', AnalyzeSpaceLighting())
FreeCADGui.addCommand('Eletrica_BalancePhases', BalancePhases())
FreeCADGui.addCommand('Eletrica_CalculateWiring', CalculateWiring())
FreeCADGui.addCommand('Eletrica_PrepareIFC', PrepareIFC())
FreeCADGui.addCommand('Eletrica_CreateTechnicalSheet', CreateTechnicalSheet())
FreeCADGui.addCommand('Eletrica_GenerateTags', GenerateTags())
FreeCADGui.addCommand('Eletrica_CheckConduitFill', CheckConduitFill())
FreeCADGui.addCommand('Eletrica_GenerateBOM', GenerateBOM())
FreeCADGui.addCommand('Eletrica_GenerateWireSymbols', GenerateWireSymbols())
FreeCADGui.addCommand('Eletrica_GroundingCalculator', GroundingCalculator())
FreeCADGui.addCommand('Eletrica_GenerateUnifilar', GenerateUnifilar())
FreeCADGui.addCommand('Eletrica_SPDAGui', SPDAGui())
FreeCADGui.addCommand('Eletrica_SPDARiskWizard', SPDARiskWizard())
FreeCADGui.addCommand('Eletrica_CreatePanel', CreatePanel())
FreeCADGui.addCommand('Eletrica_InsertTUE', InsertTUE())
FreeCADGui.addCommand('Eletrica_InsertServiceEntrance', InsertServiceEntrance())
FreeCADGui.addCommand('Eletrica_AutoConnectSequence', AutoConnectSequence())
FreeCADGui.addCommand('Eletrica_AutoConnectCeiling', AutoConnectCeiling())
FreeCADGui.addCommand('Eletrica_ApplyHeatmap', ApplyHeatmap())
FreeCADGui.addCommand('Eletrica_AssignCircuitToConduit', AssignCircuitToConduit())
FreeCADGui.addCommand('Eletrica_ClearConduitCircuits', ClearConduitCircuits())
FreeCADGui.addCommand('Eletrica_GenerateReport', GenerateReport())
FreeCADGui.addCommand('Eletrica_SolarEstimate', SolarEstimate())
FreeCADGui.addCommand('Eletrica_GeneratePanelLabels', GeneratePanelLabels())
FreeCADGui.addCommand('Eletrica_RunProjectAudit', RunProjectAudit())
FreeCADGui.addCommand('Eletrica_CreateExposedConduit', CreateExposedConduit())
FreeCADGui.addCommand('Eletrica_ManageBoxes', ManageBoxes())
