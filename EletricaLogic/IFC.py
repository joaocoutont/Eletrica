# Utilitarios para Exportacao IFC4 - Mapeamento de Property Sets Elétricos
try:
    import FreeCAD
except ImportError:
    FreeCAD = None

# Mapeamento de tipo BIM para IFC Entity + Pset Principal
IFC_TYPE_MAP = {
    "Tomada":      ("IfcOutlet",                    "Pset_ElectricalDeviceCommon"),
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
            tipo = getattr(obj, "TipoBIM", None)
            if not tipo:
                # Tenta inferir se for um objeto elétrico
                if hasattr(obj, "Potencia"):
                    tipo = "Tomada"
                elif hasattr(obj, "PotenciaAcumulada"):
                    tipo = "Quadro"
                else:
                    continue

            ifc_entity, pset_name = IFC_TYPE_MAP.get(tipo, (None, None))
            if not ifc_entity:
                continue

            # Definir entidade IFC para o exportador do FreeCAD
            if hasattr(obj, "IfcType"):
                obj.IfcType = ifc_entity
            else:
                # Alguns objetos Arch/BIM já possuem, outros precisam adicionar
                try:
                    obj.addProperty("App::PropertyEnumeration", "IfcType", "BIM", "Tipo IFC")
                    obj.IfcType = ifc_entity
                except:
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
                    
                    try:
                        # Trata conversão de tipos (ex: "220V" -> 220.0 se for Float)
                        if prop_type == "App::PropertyFloat" and isinstance(value, str):
                            numeric_val = float(value.replace("V", "").replace("A", "").strip())
                            setattr(obj, pset_full_name, numeric_val)
                        else:
                            setattr(obj, pset_full_name, value)
                    except Exception:
                        # Fallback para string se a conversão falhar
                        try:
                            setattr(obj, pset_full_name, str(value))
                        except:
                            pass

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
