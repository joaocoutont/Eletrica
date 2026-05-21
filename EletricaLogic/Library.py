# Gerenciador de Biblioteca de Objetos
import os
import FreeCAD
import Part

class LibraryManager:
    def __init__(self, path_3d=None, path_2d=None):
        # Tenta carregar dos parametros do FreeCAD
        param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
        default_base = os.path.join(FreeCAD.getUserAppDataDir(), "Mod", "Eletrica", "Library")
        
        self.path_3d = path_3d or param.GetString("Path3D", os.path.join(default_base, "3D"))
        self.path_2d = path_2d or param.GetString("Path2D", os.path.join(default_base, "2D"))

    def get_active_level_height(self):
        """Tenta encontrar a altura do nivel (BuildingPart) ativo no Workbench BIM"""
        try:
            import Arch
            active_obj = Arch.getActiveFloor() # Tenta pegar o andar/nivel ativo
            if active_obj:
                # Retorna a altura (Z) do nivel
                return active_obj.Placement.Base.z
        except:
            pass
        return None

    @staticmethod
    def configure_independent_link(link):
        """Deixa o App::Link cair visualmente no Placement da propria instancia."""
        if not link:
            return
        try:
            if hasattr(link, "LinkTransform"):
                link.LinkTransform = True
            if hasattr(link, "LinkPlacement"):
                link.LinkPlacement = FreeCAD.Placement()
        except Exception:
            pass

    @staticmethod
    def open_link_source(full_path):
        previous_doc_name = None
        try:
            if FreeCAD.ActiveDocument:
                previous_doc_name = FreeCAD.ActiveDocument.Name
        except Exception:
            previous_doc_name = None
        source_doc = None
        try:
            try:
                source_doc = FreeCAD.openDocument(full_path, True, True)
            except TypeError:
                source_doc = FreeCAD.open(full_path)
            if not source_doc or not source_doc.Objects:
                return None
            return source_doc.Objects[0]
        finally:
            if previous_doc_name:
                try:
                    FreeCAD.setActiveDocument(previous_doc_name)
                except Exception:
                    pass

    @staticmethod
    def load_component_shape(full_path):
        previous_doc_name = None
        try:
            if FreeCAD.ActiveDocument:
                previous_doc_name = FreeCAD.ActiveDocument.Name
        except Exception:
            previous_doc_name = None

        source_doc = None
        try:
            try:
                source_doc = FreeCAD.openDocument(full_path, True, True)
            except TypeError:
                source_doc = FreeCAD.open(full_path)

            best_shape = None
            max_volume = -1.0
            for obj in getattr(source_doc, "Objects", []):
                shape = None
                try:
                    if hasattr(obj, "Shape") and obj.Shape and not obj.Shape.isNull():
                        shape = obj.Shape.copy()
                        if hasattr(obj, "Placement") and obj.Placement:
                            shape.transformShape(obj.Placement.toMatrix())
                    elif hasattr(obj, "Tip") and obj.Tip and obj.Tip.Shape and not obj.Tip.Shape.isNull():
                        shape = obj.Tip.Shape.copy()
                        if hasattr(obj, "Placement") and obj.Placement:
                            shape.transformShape(obj.Placement.toMatrix())
                except Exception:
                    shape = None
                if not shape:
                    continue
                try:
                    volume = float(shape.Volume)
                except Exception:
                    volume = 0.0
                if best_shape is None or volume > max_volume:
                    best_shape = shape
                    max_volume = volume

            if best_shape:
                center = best_shape.BoundBox.Center
                best_shape.translate(FreeCAD.Vector(-center.x, -center.y, -center.z))
            return best_shape
        finally:
            if source_doc:
                try:
                    FreeCAD.closeDocument(source_doc.Name)
                except Exception:
                    pass
            if previous_doc_name:
                try:
                    FreeCAD.setActiveDocument(previous_doc_name)
                except Exception:
                    pass

    @classmethod
    def get_or_create_link_source(cls, doc, full_path, obj_name):
        safe_name = "Matriz_" + "".join(ch if ch.isalnum() else "_" for ch in obj_name)
        source = doc.getObject(safe_name)
        if source:
            return source

        shape = cls.load_component_shape(full_path)
        if not shape:
            return None
        source = doc.addObject("Part::Feature", safe_name)
        source.Label = f"Matriz {obj_name}"
        source.Shape = shape
        try:
            source.ViewObject.Visibility = False
            source.ViewObject.Selectable = False
            if hasattr(source.ViewObject, "ShowInTree"):
                source.ViewObject.ShowInTree = False
        except Exception:
            pass
        return source

    @staticmethod
    def correct_link_visual_position(link, target_pos, doc=None):
        """
        Em FreeCAD 1.1 o App::Link pode compor o Placement do objeto linkado
        e/ou do container de origem. Corrige pelo resultado visual real.
        """
        if not link or getattr(link, "TypeId", "") != "App::Link" or target_pos is None:
            return
        doc = doc or getattr(link, "Document", None) or FreeCAD.ActiveDocument
        try:
            if doc:
                doc.recompute([link])
        except Exception:
            try:
                if doc:
                    doc.recompute()
            except Exception:
                pass

        for _ in range(3):
            try:
                shape = getattr(link, "Shape", None)
                if not shape or shape.isNull():
                    return
                center = shape.BoundBox.Center
                delta = FreeCAD.Vector(
                    target_pos.x - center.x,
                    target_pos.y - center.y,
                    target_pos.z - center.z,
                )
                if delta.Length < 0.01:
                    return
                link.Placement.Base = link.Placement.Base + delta
                if doc:
                    doc.recompute([link])
            except Exception as exc:
                FreeCAD.Console.PrintWarning(f"[Eletrica] Nao foi possivel corrigir Link: {exc}\n")
                return

    @classmethod
    def set_component_position(cls, obj, position, doc=None):
        if not obj or position is None:
            return
        try:
            obj.Placement.Base = position
            cls.correct_link_visual_position(obj, position, doc=doc)
        except Exception:
            pass

    def list_components(self):
        """Lista todos os componentes .FCStd disponiveis na biblioteca 3D"""
        if not os.path.exists(self.path_3d):
            return []
        return [f for f in os.listdir(self.path_3d) if f.endswith('.FCStd')]

    def insert_component(self, filename, label=None, symbol_height=None):
        """
        Insere um componente da biblioteca no documento ativo usando App::Link.
        """
        # Se nao for passada altura, tenta detectar o nivel BIM
        if symbol_height is None:
            bim_height = self.get_active_level_height()
            # Se encontrar o nivel, usamos a altura dele + um offset para o 'teto' (ex: 2.7m)
            # Ou podemos usar exatamente a altura do nivel se o usuario ja estiver no teto.
            symbol_height = bim_height + 2700.0 if bim_height is not None else 2700.0
        full_path = os.path.join(self.path_3d, filename)
        if not os.path.exists(full_path):
            FreeCAD.Console.PrintError(f"Arquivo nao encontrado: {full_path}\n")
            return None
        
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("ProjetoEletrico")
            
        # Nome do objeto baseado no arquivo
        obj_name = filename.replace(".FCStd", "")
        
        # Criar um Link para o arquivo externo
        # No FreeCAD, o App::Link pode apontar para um arquivo externo
        try:
            source = self.get_or_create_link_source(doc, full_path, obj_name)
            if not source:
                FreeCAD.Console.PrintError(f"Nenhuma geometria encontrada em: {full_path}\n")
                return None
            link = doc.addObject("App::Link", obj_name)
            link.LinkedObject = source
            self.configure_independent_link(link)
            self.correct_link_visual_position(link, FreeCAD.Vector(0, 0, 0), doc=doc)
            link.Label = label or obj_name
            
            # Adicionar propriedades elétricas customizadas (BIM)
            if not hasattr(link, "Potencia"):
                link.addProperty("App::PropertyPower", "Potencia", "Eletrica", "Potencia instalada em VA")
                link.Potencia = 100.0 # Valor default
                
            if not hasattr(link, "Tensao"):
                link.addProperty("App::PropertyEnumeration", "Tensao", "Eletrica", "Tensao de operacao")
                link.Tensao = ["127V", "220V", "380V"]
                try:
                    from EletricaLogic.Settings import ProjectSettings
                    link.Tensao = ProjectSettings.format_voltage(ProjectSettings.get_voltage())
                except Exception:
                    link.Tensao = "127V"
                
            if not hasattr(link, "QuadroVinculado"):
                link.addProperty("App::PropertyLink", "QuadroVinculado", "Eletrica", "Quadro de distribuicao que alimenta este item")
                
            if not hasattr(link, "Circuito"):
                link.addProperty("App::PropertyString", "Circuito", "Eletrica", "Identificacao do Circuito")
                link.Circuito = "Geral"
            
            doc.recompute()
            
            # Tentar inserir simbolo 2D correspondente
            symbol_file = self.get_symbol_for_3d(filename)
            if symbol_file:
                self.insert_symbol(symbol_file, link, height=symbol_height)
                FreeCAD.Console.PrintMessage(f"Simbolo 2D '{symbol_file}' vinculado em Z={symbol_height}.\n")
            
            FreeCAD.Console.PrintMessage(f"Inserido: {obj_name}\n")
            return link
        except Exception as e:
            FreeCAD.Console.PrintError(f"Erro ao inserir componente: {str(e)}\n")
            return None

    def get_symbol_for_3d(self, filename_3d):
        """
        Tenta encontrar o simbolo 2D mais adequado para o componente 3D.
        """
        # Mapeamento basico manual (podemos expandir isso)
        mapping = {
            "HRC_Tomada_1_10A": "Tomada Baixa.FCStd",
            "HRC_Tomada_1_20A": "Tomada Baixa.FCStd",
            "HRC_Interruptor_1Botao": "Interruptor Simples.FCStd",
            "HRC_Interruptor_2Botoes": "Interruptor 2 Seções.FCStd",
            "HRC_Caixa de Distribuição": "Quadro de distribuição.FCStd",
            "Bocal e Lampada": "Ponto de Luz no teto.FCStd"
        }
        
        # Tentar busca por prefixo se nao estiver no mapping
        base_name = filename_3d.replace(".FCStd", "")
        if base_name in mapping:
            return mapping[base_name]
            
        # Busca generica por palavras chave
        if "Tomada" in base_name: return "Tomada Baixa.FCStd"
        if "Interruptor" in base_name: return "Interruptor Simples.FCStd"
        if "Luz" in base_name or "Lampada" in base_name: return "Ponto de Luz no teto.FCStd"
        
        return None

    def insert_symbol(self, symbol_filename, parent_obj=None, height=2700.0):
        """
        Insere o simbolo 2D e o posiciona no nivel do teto (height).
        Isso evita que simbolos fiquem 'espalhados' em alturas diferentes no 3D.
        """
        if not symbol_filename: return
        
        full_path = os.path.join(self.path_2d, symbol_filename)
        if not os.path.exists(full_path): return
        
        doc = FreeCAD.ActiveDocument
        try:
            sym_name = "Simbolo_" + symbol_filename.replace(".FCStd", "")
            source = self.get_or_create_link_source(doc, full_path, sym_name)
            if not source:
                return None
            sym_link = doc.addObject("App::Link", sym_name)
            sym_link.LinkedObject = source
            self.configure_independent_link(sym_link)
            
            # Posicionamento: X e Y seguem o pai, Z vai para o 'teto'
            if parent_obj:
                # Copiar X e Y do objeto 3D
                pos = parent_obj.Placement.Base
                self.set_component_position(sym_link, FreeCAD.Vector(pos.x, pos.y, height), doc=doc)
            else:
                self.set_component_position(sym_link, FreeCAD.Vector(0, 0, height), doc=doc)
                
            return sym_link
        except:
            return None
