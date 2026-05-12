# Gerador de Esquemas de Comando (Multifilar/Comando)
import FreeCAD

class ControlDiagramManager:
    @staticmethod
    def generate_starter_logic(method):
        """Retorna a sequencia de componentes para o esquema de comando"""
        logics = {
            "Direta": ["Disjuntor Comando", "Emergência", "Termostato/Relé", "Botão Desliga", "Botão Liga", "Selo Contator (K1)", "Bobina K1"],
            "Estrela-Triangulo": ["Comando", "Emergência", "Liga", "Temporizador", "K1 (Principal)", "K2 (Estrela)", "K3 (Triângulo)", "Intertravamento"],
            "Soft-Starter": ["Comando", "Emergência", "Entrada Digital DI1 (Start)", "Relé de Erro", "By-pass (Opcional)"],
            "Inversor de Frequencia": ["Comando", "Safe Torque Off (STO)", "Entrada Analogica (Velocidade)", "DI1 (Sentido Horario)"]
        }
        return logics.get(method, ["Circuito de Comando Geral"])

    @staticmethod
    def create_text_diagram(obj):
        """Cria um relatorio de fiacao para o comando do painel"""
        if not hasattr(obj, "TipoPartida"): return "Objeto não possui partida definida."
        
        logic = ControlDiagramManager.generate_starter_logic(obj.TipoPartida)
        report = f"ESQUEMA DE COMANDO - {obj.Label}\n"
        report += "="*30 + "\n"
        for i, step in enumerate(logic):
            report += f"[{i+1}] --- {step} ---\n"
        report += "="*30 + "\n"
        
        # Salva no objeto para consulta
        if not hasattr(obj, "EsquemaComando"):
            obj.addProperty("App::PropertyString", "EsquemaComando", "Documentação").EsquemaComando = report
            
        return report
