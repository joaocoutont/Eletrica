# Utilitarios para Exportacao IFC4 - Mapeamento de Property Sets Elétricos
try:
    import FreeCAD
except ImportError:
    FreeCAD = None

# Mapeamento de tipo BIM para IFC Entity + Pset Principal
IFC_TYPE_MAP = {
    "Tomada":      ("IfcOutlet",                    "Pset_ElectricalDeviceCommon"),
    "Socket":      ("IfcOutlet",                    "Pset_ElectricalDeviceCommon"),
    "Tomada TUE":  ("IfcElectricAppliance",         "Pset_ElectricalDeviceCommon"),
    "TUE":         ("IfcElectricAppliance",         "Pset_ElectricalDeviceCommon"),
    "Luminaria":   ("IfcLightFixture",              "Pset_LightFixtureTypeCommon"),
    "Interruptor": ("IfcSwitchingDevice",           "Pset_SwitchingDeviceTypeCommon"),
    "Painel":      ("IfcElectricDistributionBoard", "Pset_ElectricDistributionBoardCommon"),
    "Quadro":      ("IfcElectricDistributionBoard", "Pset_ElectricDistributionBoardCommon"),
    "Motor":       ("IfcElectricMotor",             "Pset_ElectricMotorTypeCommon"),
    "Eletroduto":  ("IfcConduit",                   "Pset_ConduitTypeCommon"),
    "Eletrocalha": ("IfcCableTray",                 "Pset_CableCarrierSegmentTypeCableTray"),
    "Subestacao":  ("IfcTransformer",               "Pset_TransformerTypeCommon"),
    "Motobomba":   ("IfcPump",                      "Pset_PumpTypeCommon"),
    "ArCondicionado": ("IfcUnitaryEquipment",       "Pset_UnitaryEquipmentTypeCommon"),
    "Telecom":     ("IfcCommunicationsAppliance",   "Pset_CommunicationsApplianceTypeCommon"),
    "Rack":        ("IfcCablingRack",               "Pset_CommunicationsApplianceTypeCommon"),
}

# Mapeamento de propriedades internas → Pset IFC (Prop, Tipo, Descrição)
PROP_MAP = {
    "Power":             ("NominalPower",         "App::PropertyFloat",  "Potência aparente/nominal legada"),
    "ApparentPowerVA":   ("ApparentPowerVA",      "App::PropertyFloat",  "Potência aparente em VA"),
    "ActivePowerW":      ("ActivePowerW",         "App::PropertyFloat",  "Potência ativa em W"),
    "PowerFactor":       ("PowerFactor",          "App::PropertyFloat",  "Fator de potência"),
    "DemandFactor":      ("DemandFactor",         "App::PropertyFloat",  "Fator de demanda"),
    "LoadClassification":("LoadClassification",   "App::PropertyString", "Classificação da carga"),
    "Voltage":           ("NominalVoltage",       "App::PropertyString", "Tensão nominal"),
    "Amperage":          ("RatedCurrent",         "App::PropertyString", "Corrente nominal da tomada"),
    "Phase":             ("Phases",               "App::PropertyString", "Fases de alimentação"),
    "CircuitNumber":     ("CircuitNumber",        "App::PropertyString", "Número do circuito"),
    "PanelBoard":        ("PanelBoard",           "App::PropertyString", "Quadro de distribuição"),
    "SpaceOrSector":     ("SpaceOrSector",        "App::PropertyString", "Ambiente ou setor"),
    "ModuleCount":       ("ModuleCount",          "App::PropertyInteger","Quantidade de módulos"),
    "SocketType":        ("SocketType",           "App::PropertyString", "Tipo da tomada"),
    "SocketApplication": ("SocketApplication",    "App::PropertyString", "Aplicação da tomada"),
    "IP_Rating":         ("IngressProtection",    "App::PropertyString", "Grau de proteção IP"),
    "ElectricalStandard":("ElectricalStandard",   "App::PropertyString", "Norma aplicada"),
    "FamilyName":        ("FamilyName",           "App::PropertyString", "Família BIM"),
    "ReferenceLevel":    ("ReferenceLevel",       "App::PropertyString", "Nível BIM de referência"),
    "FinalElevation":    ("FinalElevation",       "App::PropertyFloat",  "Elevação final do ponto"),
    "SymbolPlaneName":   ("SymbolPlaneName",      "App::PropertyString", "Plano de simbologia"),
    "SymbolFinalElevation": ("SymbolFinalElevation", "App::PropertyFloat", "Elevação final da simbologia"),
    "Potencia":          ("NominalPower",         "App::PropertyFloat",  "Potência Ativa"),
    "PotenciaAcumulada": ("TotalInstalledLoad",   "App::PropertyFloat",  "Carga Total Instalada"),
    "Tensao":            ("NominalVoltage",       "App::PropertyString", "Tensão Nominal"),
    "CorrenteNom":       ("RatedCurrent",         "App::PropertyFloat",  "Corrente Nominal"),
    "Disjuntor":         ("RatedCurrent",         "App::PropertyFloat",  "Corrente do Disjuntor"),
    "Circuito":          ("CircuitBreakerId",     "App::PropertyString", "Identificação do Circuito"),
    "Fase":              ("Phases",               "App::PropertyString", "Fases de Alimentação"),
    "TipoBIM":           ("ElectricalDeviceType", "App::PropertyString", "Categoria Elétrica"),
    "TipoPartida":       ("StartingMethod",       "App::PropertyString", "Método de Partida"),
    "Vazao":             ("NominalFlowRate",      "App::PropertyFloat",  "Vazão de Projeto"),
    "MCA":               ("NominalHead",          "App::PropertyFloat",  "Altura Manométrica"),
    "BTU":               ("NominalCoolingCapacity","App::PropertyString","Capacidade Térmica"),
    "KitWEG":            ("MotorStarterType",     "App::PropertyString", "Componentes de Partida"),
    "SecaoCabo":         ("ConductorCrossSection","App::PropertyFloat",  "Seção do Condutor"),
    # --- Instrumentação MT ---
    "TC_Ratio":          ("CurrentTransformerRatio", "App::PropertyString", "Relação TC"),
    "TC_Class":          ("CurrentTransformerClass", "App::PropertyString", "Classe TC"),
    "TP_Ratio":          ("VoltageTransformerRatio", "App::PropertyString", "Relação TP"),
    "TP_Class":          ("VoltageTransformerClass", "App::PropertyString", "Classe TP"),
    # --- Dados de Placa (Motor) ---
    "FatorServico":      ("ServiceFactor",        "App::PropertyFloat",  "FS"),
    "RPM":               ("RatedSpeed",           "App::PropertyInteger","Rotação"),
    "Polos":             ("NumberOfPoles",        "App::PropertyInteger","Polos"),
    "CosPhi":            ("PowerFactor",          "App::PropertyFloat",  "Fator de Potência"),
    # --- Gestão de Ativos (BIM 6D / O&M) ---
    "NumeroSerie":       ("SerialNumber",         "App::PropertyString", "Número de Série"),
    "DataInstalacao":    ("InstallationDate",     "App::PropertyString", "Data de Instalação"),
    "DataManutencao":    ("WarrantyStartDate",    "App::PropertyString", "Próxima Manutenção"),
}

# Mapeamento de Psets extras por finalidade
EXTRA_PSET_MAP = {
    "NumeroSerie":    "Pset_Asset",
    "DataInstalacao": "Pset_Asset",
    "DataManutencao": "Pset_Asset",
    "ApparentPowerVA": "Eletrica_LoadData",
    "ActivePowerW": "Eletrica_LoadData",
    "PowerFactor": "Eletrica_LoadData",
    "DemandFactor": "Eletrica_LoadData",
    "LoadClassification": "Eletrica_LoadData",
    "CircuitNumber": "Eletrica_CircuitData",
    "PanelBoard": "Eletrica_CircuitData",
    "SpaceOrSector": "Eletrica_CircuitData",
    "ModuleCount": "Eletrica_DeviceData",
    "SocketType": "Eletrica_DeviceData",
    "SocketApplication": "Eletrica_DeviceData",
    "IP_Rating": "Eletrica_DeviceData",
    "ElectricalStandard": "Eletrica_DeviceData",
    "FamilyName": "Eletrica_DeviceData",
    "ReferenceLevel": "Eletrica_PlacementData",
    "FinalElevation": "Eletrica_PlacementData",
    "SymbolPlaneName": "Eletrica_SymbolData",
    "SymbolFinalElevation": "Eletrica_SymbolData",
}

def _is_library_matrix(obj):
    role = getattr(obj, "BIMRole", "")
    if role in ["SocketMatrix", "LibraryMatrix", "FamilyMatrix"]:
        return True
    try:
        if bool(getattr(obj, "IsLibraryMatrix", False)):
            return True
    except Exception:
        pass
    name = f"{getattr(obj, 'Name', '')} {getattr(obj, 'Label', '')}"
    return "Matriz_" in name or "Matrix_" in name


def _plain_value(value):
    return value.Value if hasattr(value, "Value") else value


def _infer_tipo_bim(obj):
    tipo = getattr(obj, "TipoBIM", None)
    if tipo:
        return str(tipo)
    role = getattr(obj, "BIMRole", "")
    if role == "Socket":
        return "Tomada"
    if role == "ModularSet":
        return "Tomada"
    if hasattr(obj, "ApparentPowerVA") or hasattr(obj, "CircuitNumber") or hasattr(obj, "PanelBoard"):
        return "Tomada"
    if hasattr(obj, "Potencia"):
        return "Tomada"
    if hasattr(obj, "PotenciaAcumulada"):
        return "Quadro"
    return None


def _ensure_export_property(obj, prop_type, name, group, desc, value):
    try:
        if not hasattr(obj, name):
            obj.addProperty(prop_type, name, group, desc)
        if prop_type == "App::PropertyFloat":
            value = float(_plain_value(value))
        elif prop_type == "App::PropertyInteger":
            value = int(_plain_value(value))
        else:
            value = str(_plain_value(value))
        setattr(obj, name, value)
    except Exception:
        try:
            setattr(obj, name, str(_plain_value(value)))
        except Exception:
            pass


def _set_ifc_class(obj, ifc_entity):
    for name, group in [("IfcType", "IFC"), ("IFC_Class", "BIM_Classificacao")]:
        try:
            if not hasattr(obj, name):
                obj.addProperty("App::PropertyString", name, group, "Classe IFC")
            setattr(obj, name, ifc_entity)
        except Exception:
            pass


class IFCExportManager:
    """Prepara objetos elétricos para exportação IFC4 com Property Sets padrão."""

    @staticmethod
    def prepare_for_ifc():
        """
        Mapeia propriedades da bancada Eletrica para Property Sets IFC4.
        Deve ser chamado antes de exportar via File > Export > IFC.
        """
        doc = FreeCAD.ActiveDocument
        if not doc:
            return

        mapped = 0
        for obj in doc.Objects:
            if _is_library_matrix(obj):
                continue
            tipo = _infer_tipo_bim(obj)
            if not tipo:
                continue

            ifc_entity, pset_name = IFC_TYPE_MAP.get(tipo, (None, None))
            if not ifc_entity:
                continue

            # Definir entidade IFC para o exportador do FreeCAD
            _set_ifc_class(obj, ifc_entity)
            if not hasattr(obj, "TipoBIM"):
                try:
                    obj.addProperty("App::PropertyString", "TipoBIM", "BIM_Classificacao", "Tipo BIM elétrico")
                    obj.TipoBIM = tipo
                except Exception:
                    pass

            # Mapear propriedades para o Pset
            for int_prop, (ifc_prop, prop_type, desc) in PROP_MAP.items():
                if hasattr(obj, int_prop):
                    value = getattr(obj, int_prop)
                    # O FreeCAD exporta propriedades no formato Pset_Nome_Propriedade
                    pset_full_name = f"{pset_name}_{ifc_prop}"
                    
                    # Verificar se a propriedade pertence a um Pset extra (ex: Pset_Asset)
                    if int_prop in EXTRA_PSET_MAP:
                        target_pset = EXTRA_PSET_MAP[int_prop]
                        pset_full_name = f"{target_pset}_{ifc_prop}"
                        if not hasattr(obj, pset_full_name):
                            obj.addProperty(prop_type, pset_full_name, target_pset, desc)
                    elif not hasattr(obj, pset_full_name):
                        obj.addProperty(prop_type, pset_full_name, pset_name, desc)
                    
                    _ensure_export_property(obj, prop_type, pset_full_name, EXTRA_PSET_MAP.get(int_prop, pset_name), desc, value)

            mapped += 1

        FreeCAD.Console.PrintMessage(f"IFC4: {mapped} objeto(s) elétrico(s) enriquecido(s) com Psets.\n")
        
        # Enriquecer o objeto de Projeto/Site se existir
        IFCExportManager.prepare_project_metadata()
        return mapped

    @staticmethod
    def prepare_project_metadata():
        """Mapeia os dados globais do projeto (Endereço, UTM, Trafo) para o IfcSite/IfcProject"""
        doc = FreeCAD.ActiveDocument
        meta = doc.getObject("Eletrica_ProjectData")
        if not meta: return

        # Procura o objeto de Site do BIM/Arch para injetar os dados
        site_obj = None
        for obj in doc.Objects:
            if hasattr(obj, "IfcType") and obj.IfcType in ["IfcSite", "IfcProject"]:
                site_obj = obj
                break
        
        if not site_obj:
            # Se não achar, cria um objeto proxy para carregar os dados no IFC
            site_obj = doc.getObject("Site") or doc.getObject("Projeto")
            if not site_obj: return

        # Mapeamento para Pset_SiteCommon e Custom Psets
        mappings = [
            ("Address",            "Pset_SiteCommon_Address",            "App::PropertyString", "Endereço"),
            ("UTM_E",              "Pset_SiteCommon_UTM_E",              "App::PropertyString", "Coordenada E"),
            ("UTM_N",              "Pset_SiteCommon_UTM_N",              "App::PropertyString", "Coordenada N"),
            ("UTM_Zone",           "Pset_SiteCommon_UTM_Zone",           "App::PropertyString", "Zona UTM"),
            ("PrimaryVoltage",     "Pset_Transformer_PrimaryVoltage",    "App::PropertyString", "Tensão MT"),
            ("Voltage",            "Pset_Transformer_SecondaryVoltage",  "App::PropertyString", "Tensão BT"),
            ("TrafoPower",         "Pset_Transformer_Power",             "App::PropertyString", "Potência Trafo"),
            ("TrafoConnection",    "Pset_Transformer_Connection",        "App::PropertyString", "Ligação Trafo"),
            ("DesignerName",       "Pset_ProjectOrder_Designer",         "App::PropertyString", "Responsável"),
            ("TC_Ratio",           "Pset_Transformer_TCRatio",           "App::PropertyString", "Relação TC"),
            ("TP_Ratio",           "Pset_Transformer_TPRatio",           "App::PropertyString", "Relação TP"),
        ]

        # Adicionar novos campos de Demanda e Aterramento do Configuracoes_Eletrica
        settings = doc.getObject("Configuracoes_Eletrica")
        if settings:
            extra_mappings = [
                ("EsquemaAterramento", "Pset_ElectricalCircuit_EarthingSystem", "App::PropertyString", "Esquema de Aterramento"),
                ("DemandaContratada_kW", "Pset_ElectricalDeviceCommon_ContractedDemand", "App::PropertyFloat", "Demanda Contratada"),
                ("TipoTarifa",         "Pset_ElectricalDeviceCommon_TariffType",       "App::PropertyString", "Modalidade Tarifária"),
            ]
            for meta_prop, ifc_prop, prop_type, desc in extra_mappings:
                if hasattr(settings, meta_prop):
                    if not hasattr(site_obj, ifc_prop):
                        site_obj.addProperty(prop_type, ifc_prop, "BIM_Utility_Data", desc)
                    setattr(site_obj, ifc_prop, getattr(settings, meta_prop))

        for meta_prop, ifc_prop, prop_type, desc in mappings:
            if hasattr(meta, meta_prop):
                if not hasattr(site_obj, ifc_prop):
                    site_obj.addProperty(prop_type, ifc_prop, "BIM_Project_Data", desc)
                setattr(site_obj, ifc_prop, getattr(meta, meta_prop))
        
        FreeCAD.Console.PrintMessage("IFC4: Metadados globais do projeto sincronizados para exportação.\n")


class IFCManager:
    """Comandos de exportação IFC da bancada Eletrica."""

    @staticmethod
    def export_electrical_discipline(file_path=None):
        doc = FreeCAD.ActiveDocument if FreeCAD else None
        if not doc:
            return 0

        if not file_path:
            try:
                import FreeCADGui
                from PySide import QtGui
                default_name = f"{doc.Name}_Eletrica.ifc"
                file_path, _ = QtGui.QFileDialog.getSaveFileName(
                    FreeCADGui.getMainWindow(),
                    "Exportar disciplina eletrica BIM",
                    default_name,
                    "IFC (*.ifc)",
                )
            except Exception:
                file_path = ""
        if not file_path:
            return 0
        if not file_path.lower().endswith(".ifc"):
            file_path += ".ifc"

        IFCExportManager.prepare_for_ifc()
        from EletricaLogic.Exporter import DisciplineExporter
        return DisciplineExporter.export_by_discipline("Elétrica", file_path)
