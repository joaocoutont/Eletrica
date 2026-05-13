# Auditoria de Projeto (Check-list de Erros)
import FreeCAD
import os
from datetime import datetime
from EletricaLogic.Calculator import ElectricalCalculator

class ProjectAuditor:
    @staticmethod
    def _log_event(message, level="INFO"):
        """Salva a mensagem de auditoria no arquivo de log do projeto."""
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # 1. Salvar em arquivo físico (se o doc estiver salvo)
        if doc.FileName:
            log_path = os.path.join(os.path.dirname(doc.FileName), f"Auditoria_{doc.Name}.log")
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(log_entry)
            except:
                pass
        
        # 2. Salvar no console do FreeCAD
        if level == "ERROR":
            FreeCAD.Console.PrintError(log_entry)
        elif level == "WARN":
            FreeCAD.Console.PrintWarning(log_entry)
        else:
            FreeCAD.Console.PrintMessage(log_entry)

    @staticmethod
    def run_full_audit():
        """Varre o projeto em busca de inconsistencias tecnicas"""
        doc = FreeCAD.ActiveDocument
        if not doc: return
        
        errors = []
        warnings = []
        
        ProjectAuditor._log_event(f"Iniciando auditoria completa no projeto '{doc.Name}'...")

        # 1. Verificar Pontos sem Circuito ou sem Quadro
        for obj in doc.Objects:
            if hasattr(obj, "Potencia"):
                if not hasattr(obj, "Circuito") or obj.Circuito == "Geral":
                    msg = f"Objeto [{obj.Label}] sem circuito definido."
                    warnings.append(f"⚠️ {msg}")
                    ProjectAuditor._log_event(msg, "WARN")
                    
                if not hasattr(obj, "QuadroVinculado") or obj.QuadroVinculado is None:
                    msg = f"Objeto [{obj.Label}] não vinculado a nenhum Quadro (QDC)."
                    errors.append(f"❌ {msg}")
                    ProjectAuditor._log_event(msg, "ERROR")

        # 2. Coordenação de Proteção (Ib <= In <= Iz) - NBR 5410
        # Agrupar cargas por circuito para validar
        circuits = {}
        for obj in doc.Objects:
            if hasattr(obj, "Circuito") and hasattr(obj, "Potencia"):
                c = obj.Circuito
                if c not in circuits:
                    circuits[c] = {"power": 0.0, "breaker": 0, "section": 0.0, "method": "B1"}
                circuits[c]["power"] += float(obj.Potencia)
                if hasattr(obj, "Disjuntor"): circuits[c]["breaker"] = float(obj.Disjuntor)
                if hasattr(obj, "SecaoCabo"):  circuits[c]["section"] = float(obj.SecaoCabo)
                if hasattr(obj, "MetodoInstalacao"): circuits[c]["method"] = obj.MetodoInstalacao

        for c_name, data in circuits.items():
            if c_name == "Geral": continue
            
            # Ib: Corrente de projeto (simplificada aqui, idealmente leria do Quadro de Cargas)
            ib = data["power"] / 127.0 # Simplificação para auditoria rápida
            in_breaker = data["breaker"]
            
            # Iz: Capacidade do cabo (usando a tabela do Calculator)
            # Precisamos da capacidade real, não a seção sugerida. 
            # Vou usar um método auxiliar ou o dicionário interno.
            section = data["section"]
            if section > 0 and in_breaker > 0:
                # Mock de Iz para validação (o ideal seria ter get_wire_capacity no Calculator)
                iz = ElectricalCalculator.get_standard_wire_gauge(999, method=data["method"]) # To get table
                # Nota: Esta parte requer que o Calculator exponha as capacidades.
                # Por hora, vamos validar Ib <= In.
                if ib > in_breaker:
                    msg = f"Circuito [{c_name}]: Sobrecarga detectada! Ib({ib:.1f}A) > In({in_breaker}A)."
                    errors.append(f"❌ {msg}")
                    ProjectAuditor._log_event(msg, "ERROR")

        # 3. Verificar Eletrodutos Vazios ou Superlotados
        for obj in doc.Objects:
            if hasattr(obj, "TaxaOcupacao"):
                if not getattr(obj, "CircuitosPassantes", []):
                    msg = f"Eletroduto [{obj.Label}] vazio (sem circuitos)."
                    warnings.append(f"⚠️ {msg}")
                if obj.TaxaOcupacao > 40.0:
                    msg = f"Eletroduto [{obj.Label}] ocupação crítica ({round(obj.TaxaOcupacao, 2)}%)."
                    errors.append(f"❌ {msg}")
                    ProjectAuditor._log_event(msg, "ERROR")
        
        # 4. Clash Detection de Precisão (BB -> Shape.Common)
        conduits = [o for o in doc.Objects if hasattr(o, "TaxaOcupacao") and hasattr(o, "Shape")]
        for i in range(len(conduits)):
            for j in range(i + 1, len(conduits)):
                try:
                    # Passo 1: Check rápido por BoundBox
                    if conduits[i].Shape.BoundBox.intersect(conduits[j].Shape.BoundBox):
                        # Passo 2: Check preciso por Interseção de Sólidos
                        common = conduits[i].Shape.common(conduits[j].Shape)
                        if common.Volume > 0.001: # Tolerância de 1mm3
                            msg = f"Colisão Real detectada: {conduits[i].Label} x {conduits[j].Label} (Vol: {common.Volume:.1f}mm³)"
                            errors.append(f"❌ {msg}")
                            ProjectAuditor._log_event(msg, "ERROR")
                            # Destacar visualmente
                            conduits[i].ViewObject.ShapeColor = (1.0, 0.0, 0.0)
                            conduits[j].ViewObject.ShapeColor = (1.0, 0.0, 0.0)
                        elif not common.isNull():
                            # Apenas encostando (Warning)
                            msg = f"Aproximação crítica: {conduits[i].Label} x {conduits[j].Label}"
                            warnings.append(f"⚠️ {msg}")
                            conduits[i].ViewObject.ShapeColor = (1.0, 0.5, 0.0)
                except Exception as e:
                    ProjectAuditor._log_event(f"Erro no Clash Detection: {str(e)}", "WARN")
        
        # 6. Auditoria de Queda de Tensão (V%)
        from EletricaLogic.Wiring import WiringManager
        circuit_lengths = WiringManager.calculate_circuit_lengths()
        meta = doc.getObject("Eletrica_ProjectData")
        v_nom = float(getattr(meta, "Voltage", "127/220V").split("/")[0].replace("V", "")) if meta else 127.0
        max_drop = float(getattr(meta, "MaxVoltageDrop", "4%").replace("%", "")) if meta else 4.0
        
        for c_name, data in circuits.items():
            if c_name == "Geral": continue
            length_m = circuit_lengths.get(c_name, 0.0) / 1000.0
            if length_m > 0 and data["section"] > 0:
                drop = ElectricalCalculator.calculate_voltage_drop(data["power"]/v_nom, length_m, data["section"], v_nom)
                if drop > max_drop:
                    msg = f"Circuito [{c_name}]: Queda de tensão excessiva ({drop:.2f}%). Limite configurado é {max_drop}%."
                    errors.append(f"❌ {msg}")
                    ProjectAuditor._log_event(msg, "ERROR")

        # 7. Exibir resultado em janela Qt
        try:
            from EletricaLogic.i18n import tr
            from PySide2 import QtWidgets
        except ImportError:
            from PySide6 import QtWidgets
        
        n_err = len(errors)
        n_warn = len(warnings)
        ProjectAuditor._log_event(f"Auditoria finalizada. Encontrados {n_err} erros e {n_warn} avisos.")
        
        lines = [f"Auditoria Concluída: {n_err} erro(s), {n_warn} aviso(s).\n"]
        if errors:
            lines += ["=== ERROS ==="] + errors + [""]
        if warnings:
            lines += ["=== AVISOS ==="] + warnings
        if not errors and not warnings:
            lines.append("✅ Projeto sem inconsistências detectadas!")
        
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(tr("Relatório de Auditoria"))
        msg_box.setText("\n".join(lines))
        msg_box.setIcon(QtWidgets.QMessageBox.Critical if errors else QtWidgets.QMessageBox.Warning if warnings else QtWidgets.QMessageBox.Information)
        msg_box.exec_()
        
        return {"Errors": errors, "Warnings": warnings}

