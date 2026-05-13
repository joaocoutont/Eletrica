# Gerador de QR Code para Realidade Aumentada e Acesso Rápido
import FreeCAD
import urllib.parse
import os

class ARManager:
    """Gera QR Code de acesso rápido a dados do projeto para uso em campo."""

    @staticmethod
    def _build_project_url(doc):
        """Monta a URL com os dados do projeto embutidos como query string."""
        meta = doc.getObject("Eletrica_ProjectData")
        params = {
            "project": doc.Name,
            "name":    getattr(meta, "ProjectName",  doc.Name)    if meta else doc.Name,
            "author":  getattr(meta, "DesignerName", "")          if meta else "",
            "crea":    getattr(meta, "CREA",          "")          if meta else "",
            "utility": getattr(meta, "Utility",       "")          if meta else "",
            "voltage": getattr(meta, "Voltage",       "")          if meta else "",
        }
        base_url = "https://eletrica-bim.app/viewer"
        return base_url + "?" + urllib.parse.urlencode(params)

    @staticmethod
    def generate_project_qr_code(page_obj=None):
        """
        Gera um QR Code com os dados do projeto e salva:
        - URL no metadado 'QRLink' do objeto de página (se fornecido)
        - Arquivo PNG do QR na mesma pasta do .FCStd
        - Mensagem no console com o link
        """
        doc = FreeCAD.ActiveDocument
        if not doc:
            FreeCAD.Console.PrintWarning("QR Code: Nenhum documento ativo.\n")
            return None

        project_url = ARManager._build_project_url(doc)
        # Usando QuickChart API (Mais moderna e flexível)
        qr_api_url  = (f"https://quickchart.io/qr?"
                       f"text={urllib.parse.quote(project_url)}&size=300&margin=2")

        # Salvar URL na página TechDraw (se fornecida)
        if page_obj and hasattr(page_obj, "addProperty"):
            if not hasattr(page_obj, "QRLink"):
                page_obj.addProperty("App::PropertyString", "QRLink",
                                      "Eletrica", "Link de Realidade Aumentada")
            page_obj.QRLink = project_url

        # Tentar baixar e salvar o PNG do QR
        qr_saved = None
        if doc.FileName:
            try:
                import urllib.request
                save_dir  = os.path.dirname(doc.FileName)
                save_path = os.path.join(save_dir, f"QRCode_{doc.Name}.png")
                urllib.request.urlretrieve(qr_api_url, save_path)
                qr_saved = save_path
                FreeCAD.Console.PrintMessage(f"QR Code salvo em: {save_path}\n")
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"QR Code: não foi possível baixar PNG ({e}).\n")
                FreeCAD.Console.PrintMessage(f"Use o link para gerar manualmente:\n{qr_api_url}\n")
        else:
            FreeCAD.Console.PrintMessage(f"Salve o projeto (.FCStd) para exportar o QR Code PNG.\n")

        FreeCAD.Console.PrintMessage(f"QR Code URL:\n{project_url}\n")
        return {"url": project_url, "qr_api": qr_api_url, "png_path": qr_saved}

    @staticmethod
    def get_panel_qr(panel_obj):
        """
        Gera QR Code específico para um quadro de distribuição (CCM/QDC).
        Útil para manutenção: ao escanear, mostra os circuitos do quadro.
        """
        doc = FreeCAD.ActiveDocument
        if not doc or not panel_obj:
            return None

        params = {
            "panel":   panel_obj.Label,
            "project": doc.Name,
            "power":   getattr(panel_obj, "PotenciaAcumulada", 0),
            "dr":      "sim" if getattr(panel_obj, "PossuiDR", False) else "nao",
            "dps":     "sim" if getattr(panel_obj, "PossuiDPS", False) else "nao",
        }
        url = "https://eletrica-bim.app/panel?" + urllib.parse.urlencode(params)
        qr_api = (f"https://chart.googleapis.com/chart?"
                  f"chs=200x200&cht=qr&chl={urllib.parse.quote(url)}&choe=UTF-8")

        FreeCAD.Console.PrintMessage(f"QR do painel '{panel_obj.Label}':\n{url}\n")
        return {"url": url, "qr_api": qr_api}
