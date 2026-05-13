# Gerenciamento de Manutenção e QR Codes (BIM 7D)
import FreeCAD
import os
import json

class MaintenanceManager:
    """Gera fichas técnicas e QR Codes para ativos do projeto."""

    @staticmethod
    def generate_asset_sheet(obj):
        """Cria um arquivo HTML com a ficha técnica do equipamento."""
        if not obj: return None
        
        doc = FreeCAD.ActiveDocument
        output_dir = os.path.join(os.path.dirname(doc.FileName or os.path.expanduser("~")), "Manutencao")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        file_path = os.path.join(output_dir, f"{obj.Label}_Ficha.html")
        
        # Coleta de dados
        data = {
            "Equipamento": obj.Label,
            "Tipo": getattr(obj, "TipoBIM", "N/A"),
            "Potência": f"{getattr(obj, 'Potencia', 0)} W / {getattr(obj, 'Potencia_CV', 0)} CV",
            "Tensão": getattr(obj, "Tensao", "N/A"),
            "Circuito": getattr(obj, "Circuito", "N/A"),
            "Número de Série": getattr(obj, "NumeroSerie", "N/A"),
            "Data Instalação": getattr(obj, "DataInstalacao", "N/A"),
            "Próxima Manutenção": getattr(obj, "DataManutencao", "N/A"),
            "Componentes de Partida": getattr(obj, "KitWEG", "N/A"),
            "Cabo": f"{getattr(obj, 'SecaoCabo', 0)} mm²"
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Ficha Técnica: {obj.Label}</title>
            <style>
                body {{ font-family: sans-serif; padding: 20px; background: #f4f4f4; }}
                .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }}
                h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
                .label {{ font-weight: bold; color: #7f8c8d; }}
                .value {{ color: #2c3e50; }}
                .footer {{ text-align: center; font-size: 10px; margin-top: 20px; color: #bdc3c7; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>{obj.Label}</h2>
                {"".join([f'<div class="row"><span class="label">{k}:</span><span class="value">{v}</span></div>' for k,v in data.items()])}
                <div class="footer">Gerado por Suite Elite BIM - FreeCAD 1.1</div>
            </div>
        </body>
        </html>
        """
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return file_path

    @staticmethod
    def generate_qr_for_obj(obj):
        """
        Gera um QR Code vinculando à ficha técnica e o insere no 3D.
        Usa a API do QRServer para gerar a imagem.
        """
        sheet_path = MaintenanceManager.generate_asset_sheet(obj)
        if not sheet_path: return
        
        # URL fictícia ou local (Para uso real, o ideal seria subir para uma nuvem/servidor)
        # Por enquanto, usamos o caminho local formatado para URI
        uri = "file://" + sheet_path.replace("\\", "/")
        
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={uri}"
        
        # No FreeCAD, podemos inserir uma imagem no plano 3D (Proxy ou Annotation)
        # Vamos criar um objeto de anotação com o link
        try:
            import Draft
            # Criar um retângulo para servir de base para o QR (opcional no 3D)
            # Para o MVP, vamos apenas imprimir o link e instrução
            FreeCAD.Console.PrintMessage(f"QR Code Gerado para {obj.Label}: {qr_url}\n")
            FreeCAD.Console.PrintMessage(f"Ficha salva em: {sheet_path}\n")
            
            # Adicionar link de manutenção no objeto
            if not hasattr(obj, "ManutencaoLink"):
                obj.addProperty("App::PropertyString", "ManutencaoLink", "Manutencao", "Link do QR Code")
            obj.ManutencaoLink = qr_url
            
            return qr_url
        except Exception as e:
            FreeCAD.Console.PrintError(f"Erro ao gerar QR: {str(e)}\n")
            return None
