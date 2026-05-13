# Logica de Interruptores e Comando de Iluminacao
import FreeCAD

class LightingManager:
    @staticmethod
    def insert_switch(switch_type="Simples", cmd_letter="a"):
        """Insere um interruptor e define sua logica de comando"""
        from EletricaLogic.Library import LibraryManager
        lib = LibraryManager()
        
        # Escolher componente baseado no tipo
        comp_map = {
            "Simples": "Interrup_Simples.FCStd",
            "Paralelo": "Interrup_Paralelo.FCStd",
            "Intermediario": "Interrup_FourWay.FCStd",
            "Fotocelula": "Relé_Fotocelula.FCStd",
            "Sensor_IR": "Sensor_Presenca_PIR.FCStd"
        }
        
        comp = comp_map.get(switch_type, "Interrup_Simples.FCStd")
        obj = lib.insert_component(comp, label=f"Interrup_{cmd_letter}")
        
        if obj:
            # Adicionar Propriedades de Comando
            if not hasattr(obj, "Comando"):
                obj.addProperty("App::PropertyString", "Comando", "Iluminação", "Letra de Comando (ex: a)").Comando = cmd_letter
                obj.addProperty("App::PropertyEnumeration", "TipoInterruptor", "Iluminação", "Tipo")
                obj.TipoInterruptor = ["Simples", "Paralelo", "Intermediario", "Fotocelula", "Sensor_IR"]
                obj.TipoInterruptor = str(switch_type)
                obj.addProperty("App::PropertyInteger", "QtdTeclas", "Iluminação", "Quantidade de Teclas").QtdTeclas = 1
                
        FreeCAD.ActiveDocument.recompute()
        return obj

    @staticmethod
    def merge_switches(switch_list):
        """Mescla varios interruptores em uma unica placa (2 ou 3 teclas)"""
        if len(switch_list) < 2:
            FreeCAD.Console.PrintWarning("Mesclagem requer no minimo 2 interruptores.\n")
            return
        
        # GUARD: filtra apenas interruptores com a propriedade Comando
        valid = [s for s in switch_list if hasattr(s, "Comando")]
        invalid = [s for s in switch_list if not hasattr(s, "Comando")]
        for inv in invalid:
            FreeCAD.Console.PrintWarning(f"Objeto [{inv.Label}] ignorado: sem propriedade 'Comando'.\n")
        
        if len(valid) < 2:
            FreeCAD.Console.PrintError("Interruptores validos insuficientes para mesclagem.\n")
            return
        
        base_obj = valid[0]
        commands = [s.Comando for s in valid]
        
        # Atualiza o primeiro objeto para ser multi-tecla
        base_obj.Label = "Interrup_" + "_".join(commands)
        base_obj.Comando = ", ".join(commands)
        if hasattr(base_obj, "QtdTeclas"):
            base_obj.QtdTeclas = len(valid)
        
        # Remove os outros para nao duplicar no BOM
        doc = FreeCAD.ActiveDocument
        for i in range(1, len(valid)):
            doc.removeObject(valid[i].Name)
            
        FreeCAD.Console.PrintMessage(f"Interruptores mesclados: {len(commands)} teclas na mesma caixa.\n")
        doc.recompute()
class LightingExpert:
    """Realiza cálculos luminotécnicos (Método dos Lúmens)"""
    
    @staticmethod
    def calculate_fixtures(length, width, height_working, lux_target, lumen_per_fixture, u_factor=0.5, m_factor=0.8):
        """
        Calcula quantidade de luminárias necessárias
        lux_target: Lux desejado (ex: 300 para galpão)
        u_factor: Coeficiente de Utilização (0.0 a 1.0)
        m_factor: Fator de Manutenção (0.8 normal)
        """
        area = length * width
        flux_total = (lux_target * area) / (u_factor * m_factor)
        n_fixtures = math.ceil(flux_total / lumen_per_fixture)
        
        # Sugestão de grid (X, Y)
        # Tenta manter a proporção da sala
        ratio = length / width
        ny = math.sqrt(n_fixtures / ratio)
        nx = n_fixtures / ny
        
        return {
            "n_fixtures": n_fixtures,
            "flux_total": flux_total,
            "grid_x": math.ceil(nx),
            "grid_y": math.ceil(ny),
            "area": area
        }

    @staticmethod
    def generate_lighting_report(room_name, results):
        html = f"""
        <html><body>
            <h2>Relatório Luminotécnico: {room_name}</h2>
            <table border='1'>
                <tr><th>Parâmetro</th><th>Valor</th></tr>
                <tr><td>Área Total</td><td>{results['area']:.2f} m²</td></tr>
                <tr><td>Fluxo Total Necessário</td><td>{results['flux_total']:.0f} lm</td></tr>
                <tr><td><b>Qtd. de Luminárias</b></td><td><b>{results['n_fixtures']}</b></td></tr>
                <tr><td>Arranjo Sugerido (Col x Lin)</td><td>{results['grid_x']} x {results['grid_y']}</td></tr>
            </table>
        </body></html>
        """
        return html
