import json
import os
import sqlite3
import uuid

try:
    import FreeCAD
except Exception:
    FreeCAD = None


WORKBENCH_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_RUST_DB = r"C:\Projetos\Eletrica Rust\eletrica.sqlite"


def _now_source_id(prefix):
    return f"{prefix}:{uuid.uuid4()}"


def _plain(value, default=None):
    if value is None:
        return default
    try:
        if hasattr(value, "Value"):
            return value.Value
    except Exception:
        pass
    return value


def _float(value, default=0.0):
    try:
        return float(_plain(value, default))
    except Exception:
        return default


def _int(value, default=0):
    try:
        text = str(_plain(value, default)).replace("V", "").replace("v", "").strip()
        if "/" in text:
            text = text.split("/", 1)[0]
        return int(float(text))
    except Exception:
        return default


def _text(value, default=""):
    try:
        value = _plain(value, default)
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def _slug(text):
    safe = []
    for ch in str(text or "").lower():
        if ch.isalnum():
            safe.append(ch)
        elif ch in [" ", "-", "_", ".", "/", "+"]:
            safe.append("_")
    value = "".join(safe).strip("_")
    while "__" in value:
        value = value.replace("__", "_")
    return value or "item"


def _normalize_source(source):
    return str(source or "").replace("\\", "/").strip("/")


def _module_count(value):
    text = str(value or "")
    for number in [3, 2, 1]:
        if text.startswith(str(number)) or f"{number} " in text:
            return number
    return 1


def _load_category(category="", load_classification=""):
    cat = str(category or "").lower()
    load = str(load_classification or "").upper()
    if "quadro" in cat or "panel" in cat:
        return "DistributionPanel"
    if "qgbt" in cat:
        return "MainSwitchboard"
    if "lumin" in cat or load == "LIGHTING":
        return "Lighting"
    if "motor" in cat:
        return "Motor"
    if "tue" in load or "especific" in load.lower():
        return "SpecificSocket"
    if "tomada" in cat or "socket" in cat or "tug" in load:
        return "GeneralSocket"
    return "GenericEquipment"


def _symbology(category="", modules=1):
    normalized = _load_category(category)
    if normalized == "DistributionPanel":
        return "DistributionPanel"
    if normalized == "Lighting":
        return "LightRound"
    if normalized in ["GeneralSocket", "SpecificSocket"]:
        return "SocketDouble" if modules >= 2 else "SocketSingle"
    return "None"


def get_database_path():
    if FreeCAD:
        try:
            params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
            configured = params.GetString("UnifiedSQLitePath", "")
            if configured:
                return configured
        except Exception:
            pass
    if os.path.isdir(os.path.dirname(DEFAULT_RUST_DB)):
        return DEFAULT_RUST_DB
    return os.path.join(WORKBENCH_DIR, "Library", "eletrica.sqlite")


def is_sync_enabled():
    if not FreeCAD:
        return True
    try:
        params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
        return params.GetBool("UnifiedSQLiteSyncEnabled", True)
    except Exception:
        return True


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS families (
    family_id TEXT PRIMARY KEY,
    external_id TEXT UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    discipline TEXT NOT NULL DEFAULT 'Eletrica',
    ifc_class TEXT NOT NULL DEFAULT '',
    source_app TEXT NOT NULL DEFAULT '',
    source_3d TEXT NOT NULL DEFAULT '',
    source_2d TEXT NOT NULL DEFAULT '',
    symbol_2d TEXT NOT NULL DEFAULT 'None',
    data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS family_electrical_defaults (
    family_id TEXT PRIMARY KEY,
    load_category TEXT NOT NULL,
    voltage INTEGER NOT NULL DEFAULT 127,
    phase TEXT NOT NULL DEFAULT 'R',
    active_power_watts REAL NOT NULL DEFAULT 0,
    apparent_power_va REAL NOT NULL DEFAULT 0,
    power_factor REAL NOT NULL DEFAULT 1,
    demand_factor REAL NOT NULL DEFAULT 1,
    utilization_factor REAL NOT NULL DEFAULT 1,
    simultaneity_factor REAL NOT NULL DEFAULT 1,
    harmonic_dist_thd REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(family_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS family_physical_defaults (
    family_id TEXT PRIMARY KEY,
    modules INTEGER NOT NULL DEFAULT 1,
    amperage TEXT NOT NULL DEFAULT '',
    socket_application TEXT NOT NULL DEFAULT '',
    mounting_height_mm REAL NOT NULL DEFAULT 0,
    height_type TEXT NOT NULL DEFAULT '',
    width_mm REAL NOT NULL DEFAULT 0,
    height_mm REAL NOT NULL DEFAULT 0,
    depth_mm REAL NOT NULL DEFAULT 0,
    weight_kg REAL NOT NULL DEFAULT 0,
    ip_rating TEXT NOT NULL DEFAULT '',
    fire_rating TEXT NOT NULL DEFAULT '',
    material_name TEXT NOT NULL DEFAULT '',
    material_density_kg_m3 REAL NOT NULL DEFAULT 0,
    embedded_carbon_kg_kg REAL NOT NULL DEFAULT 0,
    cost_per_unit REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(family_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS family_asset_defaults (
    family_id TEXT PRIMARY KEY,
    manufacturer TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    catalog_code TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    omniclass_code TEXT NOT NULL DEFAULT '',
    uniformat_code TEXT NOT NULL DEFAULT '',
    expected_life_years REAL NOT NULL DEFAULT 0,
    maintenance_manual_url TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (family_id) REFERENCES families(family_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS family_connectors (
    connector_id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    name TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    x_mm REAL NOT NULL DEFAULT 0,
    y_mm REAL NOT NULL DEFAULT 0,
    z_mm REAL NOT NULL DEFAULT 0,
    dir_x REAL NOT NULL DEFAULT 0,
    dir_y REAL NOT NULL DEFAULT 0,
    dir_z REAL NOT NULL DEFAULT 1,
    diameter_mm REAL NOT NULL DEFAULT 20,
    voltage INTEGER NOT NULL DEFAULT 127,
    phase TEXT NOT NULL DEFAULT 'R',
    max_load_va REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (family_id) REFERENCES families(family_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    code_standard TEXT NOT NULL DEFAULT 'NBR 5410',
    units TEXT NOT NULL DEFAULT 'Meters',
    georef_json TEXT NOT NULL DEFAULT '{}',
    data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS levels (
    level_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    external_id TEXT,
    name TEXT NOT NULL,
    elevation_m REAL NOT NULL DEFAULT 0,
    height_m REAL NOT NULL DEFAULT 3,
    data_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(project_id, name),
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS panels (
    panel_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    external_id TEXT,
    name TEXT NOT NULL,
    family_id TEXT,
    level_id TEXT,
    parent_panel_id TEXT,
    voltage INTEGER NOT NULL DEFAULT 220,
    phase_config TEXT NOT NULL DEFAULT 'ThreePhase',
    system TEXT NOT NULL DEFAULT '',
    has_dr_protection INTEGER NOT NULL DEFAULT 0,
    has_dps_protection INTEGER NOT NULL DEFAULT 0,
    x_m REAL NOT NULL DEFAULT 0,
    y_m REAL NOT NULL DEFAULT 0,
    z_m REAL NOT NULL DEFAULT 0,
    rotation_z_deg REAL NOT NULL DEFAULT 0,
    data_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(project_id, external_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(family_id),
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (parent_panel_id) REFERENCES panels(panel_id)
);

CREATE TABLE IF NOT EXISTS circuits (
    circuit_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    external_id TEXT,
    panel_id TEXT,
    code TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    voltage INTEGER NOT NULL DEFAULT 127,
    phase_config TEXT NOT NULL DEFAULT 'SinglePhase',
    phase_assignment TEXT NOT NULL DEFAULT 'PhaseR',
    installation_method TEXT NOT NULL DEFAULT 'B1',
    ambient_temperature REAL NOT NULL DEFAULT 30,
    grouping_factor REAL NOT NULL DEFAULT 1,
    temperature_factor REAL NOT NULL DEFAULT 1,
    max_voltage_drop_pct REAL NOT NULL DEFAULT 4,
    circuit_length_m REAL NOT NULL DEFAULT 0,
    breaker_rating_amp REAL NOT NULL DEFAULT 0,
    wire_size_mm2 REAL NOT NULL DEFAULT 0,
    has_dr_protection INTEGER NOT NULL DEFAULT 0,
    has_dps_protection INTEGER NOT NULL DEFAULT 0,
    is_panel INTEGER NOT NULL DEFAULT 0,
    total_active_power_watts REAL NOT NULL DEFAULT 0,
    total_apparent_power_va REAL NOT NULL DEFAULT 0,
    calculated_current_a REAL NOT NULL DEFAULT 0,
    design_current_a REAL NOT NULL DEFAULT 0,
    voltage_drop_pct REAL NOT NULL DEFAULT 0,
    data_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(project_id, panel_id, code),
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (panel_id) REFERENCES panels(panel_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS project_elements (
    element_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    external_id TEXT,
    source_app TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    family_id TEXT,
    category TEXT NOT NULL,
    ifc_class TEXT NOT NULL DEFAULT '',
    level_id TEXT,
    panel_id TEXT,
    circuit_id TEXT,
    circuit_number TEXT NOT NULL DEFAULT '',
    panel_board TEXT NOT NULL DEFAULT '',
    space_or_sector TEXT NOT NULL DEFAULT '',
    tag TEXT NOT NULL DEFAULT '',
    x_m REAL NOT NULL DEFAULT 0,
    y_m REAL NOT NULL DEFAULT 0,
    z_m REAL NOT NULL DEFAULT 0,
    rotation_z_deg REAL NOT NULL DEFAULT 0,
    scale_x REAL NOT NULL DEFAULT 1,
    scale_y REAL NOT NULL DEFAULT 1,
    scale_z REAL NOT NULL DEFAULT 1,
    voltage INTEGER NOT NULL DEFAULT 127,
    phase TEXT NOT NULL DEFAULT 'R',
    active_power_watts REAL NOT NULL DEFAULT 0,
    apparent_power_va REAL NOT NULL DEFAULT 0,
    power_factor REAL NOT NULL DEFAULT 1,
    demand_factor REAL NOT NULL DEFAULT 1,
    load_category TEXT NOT NULL DEFAULT '',
    mounting_height_mm REAL NOT NULL DEFAULT 0,
    final_elevation_mm REAL NOT NULL DEFAULT 0,
    host_object TEXT NOT NULL DEFAULT '',
    host_face TEXT NOT NULL DEFAULT '',
    data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, external_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(family_id),
    FOREIGN KEY (level_id) REFERENCES levels(level_id),
    FOREIGN KEY (panel_id) REFERENCES panels(panel_id),
    FOREIGN KEY (circuit_id) REFERENCES circuits(circuit_id)
);

CREATE TABLE IF NOT EXISTS element_connectors (
    connector_id TEXT PRIMARY KEY,
    element_id TEXT NOT NULL,
    family_connector_id TEXT,
    name TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    x_m REAL NOT NULL DEFAULT 0,
    y_m REAL NOT NULL DEFAULT 0,
    z_m REAL NOT NULL DEFAULT 0,
    dir_x REAL NOT NULL DEFAULT 0,
    dir_y REAL NOT NULL DEFAULT 0,
    dir_z REAL NOT NULL DEFAULT 1,
    diameter_mm REAL NOT NULL DEFAULT 20,
    voltage INTEGER NOT NULL DEFAULT 127,
    phase TEXT NOT NULL DEFAULT 'R',
    max_load_va REAL NOT NULL DEFAULT 0,
    connected_circuit_id TEXT,
    data_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (element_id) REFERENCES project_elements(element_id) ON DELETE CASCADE,
    FOREIGN KEY (family_connector_id) REFERENCES family_connectors(connector_id),
    FOREIGN KEY (connected_circuit_id) REFERENCES circuits(circuit_id)
);

CREATE TABLE IF NOT EXISTS sync_events (
    event_id TEXT PRIMARY KEY,
    source_app TEXT NOT NULL,
    target_app TEXT NOT NULL DEFAULT '',
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    error_message TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_families_category ON families(category);
CREATE INDEX IF NOT EXISTS idx_elements_project ON project_elements(project_id);
CREATE INDEX IF NOT EXISTS idx_elements_family ON project_elements(family_id);
CREATE INDEX IF NOT EXISTS idx_elements_circuit ON project_elements(circuit_id);
CREATE INDEX IF NOT EXISTS idx_circuits_panel ON circuits(panel_id);
CREATE INDEX IF NOT EXISTS idx_sync_pending ON sync_events(status, created_at);
"""


class UnifiedSQLite:
    @staticmethod
    def connect(path=None):
        path = path or get_database_path()
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_SQL)
        conn.executemany(
            "INSERT OR REPLACE INTO app_metadata (key, value) VALUES (?, ?)",
            [
                ("schema_name", "eletrica_unified"),
                ("schema_version", "1"),
                ("primary_format", "sqlite_json"),
                ("owner", "Eletrica FreeCAD + Eletrica Rust"),
            ],
        )
        conn.commit()
        return conn

    @staticmethod
    def export_family_catalog(path=None):
        from EletricaLogic.FamilyCatalog import list_families

        conn = UnifiedSQLite.connect(path)
        try:
            for family in list_families():
                UnifiedSQLite.upsert_family(conn, family)
            conn.commit()
        finally:
            conn.close()
        return path or get_database_path()

    @staticmethod
    def upsert_family(conn, family):
        source_3d = _normalize_source(family.get("source_3d", ""))
        family_id = family.get("id") or _slug(source_3d or family.get("name"))
        category = _load_category(family.get("category"), family.get("load_classification"))
        modules = _module_count(family.get("modules"))
        symbol_2d = _symbology(category, modules)
        data = {
            "schema_version": 1,
            "family_id": family_id,
            "name": family.get("name", family_id),
            "category": category,
            "discipline": family.get("discipline", "Eletrica"),
            "ifc_class": family.get("ifc_class", ""),
            "source_3d": source_3d,
            "source_2d": _normalize_source(family.get("source_2d", "")),
            "symbol_2d": symbol_2d,
            "electrical": {
                "voltage": _int(family.get("voltage"), 127),
                "phase": family.get("phase", "R"),
                "active_power_watts": _float(family.get("active_power_w"), _float(family.get("power"), 0.0)),
                "apparent_power_va": _float(family.get("apparent_power_va"), _float(family.get("power"), 0.0)),
                "power_factor": _float(family.get("power_factor"), 1.0),
                "demand_factor": _float(family.get("demand_factor"), 1.0),
                "utilization_factor": _float(family.get("utilization_factor"), 1.0),
                "simultaneity_factor": _float(family.get("simultaneity_factor"), 1.0),
                "harmonic_dist_thd": _float(family.get("harmonic_dist_thd"), 0.0),
            },
            "physical": {
                "modules": modules,
                "amperage": family.get("amperage", ""),
                "socket_application": family.get("socket_application", ""),
                "mounting_height_mm": _float(family.get("mounting_height"), 0.0),
                "height_type": family.get("height_type", ""),
                "dimensions_mm": [
                    _float(family.get("width_mm"), 0.0),
                    _float(family.get("height_mm"), 0.0),
                    _float(family.get("depth_mm"), 0.0),
                ],
                "ip_rating": family.get("ip_rating", ""),
                "fire_rating": family.get("fire_rating", ""),
                "material_name": family.get("material_name", ""),
                "cost_per_unit": _float(family.get("cost_per_unit"), 0.0),
            },
            "asset": {
                "manufacturer": family.get("manufacturer", ""),
                "model": family.get("model", ""),
                "catalog_code": family.get("catalog_code", ""),
                "description": family.get("description", ""),
            },
            "connectors": [
                {
                    "name": "Entrada",
                    "connector_type": "Conduit",
                    "relative_position_mm": [0.0, -40.0, 0.0],
                    "direction": [0.0, -1.0, 0.0],
                    "diameter_mm": 20.0,
                    "voltage": _int(family.get("voltage"), 127),
                    "phase": family.get("phase", "R"),
                    "max_load_va": _float(family.get("apparent_power_va"), 0.0),
                }
            ],
        }
        conn.execute(
            """
            INSERT INTO families (
                family_id, external_id, name, category, discipline, ifc_class,
                source_app, source_3d, source_2d, symbol_2d, data_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'freecad', ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(family_id) DO UPDATE SET
                external_id=excluded.external_id,
                name=excluded.name,
                category=excluded.category,
                discipline=excluded.discipline,
                ifc_class=excluded.ifc_class,
                source_app=excluded.source_app,
                source_3d=excluded.source_3d,
                source_2d=excluded.source_2d,
                symbol_2d=excluded.symbol_2d,
                data_json=excluded.data_json,
                updated_at=CURRENT_TIMESTAMP
            """,
            (
                family_id,
                f"freecad:family:{family_id}",
                data["name"],
                category,
                data["discipline"],
                data["ifc_class"],
                source_3d,
                data["source_2d"],
                symbol_2d,
                json.dumps(data, ensure_ascii=False, sort_keys=True),
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO family_electrical_defaults (
                family_id, load_category, voltage, phase, active_power_watts,
                apparent_power_va, power_factor, demand_factor, utilization_factor,
                simultaneity_factor, harmonic_dist_thd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                family_id,
                category,
                data["electrical"]["voltage"],
                data["electrical"]["phase"],
                data["electrical"]["active_power_watts"],
                data["electrical"]["apparent_power_va"],
                data["electrical"]["power_factor"],
                data["electrical"]["demand_factor"],
                data["electrical"]["utilization_factor"],
                data["electrical"]["simultaneity_factor"],
                data["electrical"]["harmonic_dist_thd"],
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO family_physical_defaults (
                family_id, modules, amperage, socket_application, mounting_height_mm,
                height_type, width_mm, height_mm, depth_mm, weight_kg, ip_rating,
                fire_rating, material_name, material_density_kg_m3,
                embedded_carbon_kg_kg, cost_per_unit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                family_id,
                modules,
                data["physical"]["amperage"],
                data["physical"]["socket_application"],
                data["physical"]["mounting_height_mm"],
                data["physical"]["height_type"],
                data["physical"]["dimensions_mm"][0],
                data["physical"]["dimensions_mm"][1],
                data["physical"]["dimensions_mm"][2],
                _float(family.get("weight_kg"), 0.0),
                data["physical"]["ip_rating"],
                data["physical"]["fire_rating"],
                data["physical"]["material_name"],
                _float(family.get("material_density_kg_m3"), 0.0),
                _float(family.get("embedded_carbon_kg_kg"), 0.0),
                data["physical"]["cost_per_unit"],
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO family_asset_defaults (
                family_id, manufacturer, model, catalog_code, description,
                omniclass_code, uniformat_code, expected_life_years, maintenance_manual_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                family_id,
                data["asset"]["manufacturer"],
                data["asset"]["model"],
                data["asset"]["catalog_code"],
                data["asset"]["description"],
                family.get("omniclass_code", ""),
                family.get("uniformat_code", ""),
                _float(family.get("expected_life_years"), 0.0),
                family.get("maintenance_manual_url", ""),
            ),
        )
        connector_id = f"{family_id}:entrada"
        conn.execute(
            """
            INSERT OR REPLACE INTO family_connectors (
                connector_id, family_id, name, connector_type, x_mm, y_mm, z_mm,
                dir_x, dir_y, dir_z, diameter_mm, voltage, phase, max_load_va
            ) VALUES (?, ?, 'Entrada', 'Conduit', 0, -40, 0, 0, -1, 0, 20, ?, ?, ?)
            """,
            (
                connector_id,
                family_id,
                data["electrical"]["voltage"],
                data["electrical"]["phase"],
                data["electrical"]["apparent_power_va"],
            ),
        )
        return family_id

    @staticmethod
    def ensure_project(conn, doc):
        name = _text(getattr(doc, "Name", ""), "Projeto_Eletrica")
        project_id = f"freecad:{name}"
        label = _text(getattr(doc, "Label", ""), name)
        conn.execute(
            """
            INSERT INTO projects (project_id, name, units, data_json, updated_at)
            VALUES (?, ?, 'Meters', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_id) DO UPDATE SET
                name=excluded.name,
                data_json=excluded.data_json,
                updated_at=CURRENT_TIMESTAMP
            """,
            (project_id, label, json.dumps({"freecad_document": name}, ensure_ascii=False)),
        )
        return project_id

    @staticmethod
    def ensure_level(conn, project_id, obj):
        level_name = _text(getattr(obj, "ReferenceLevel", ""), "Projeto") or "Projeto"
        elevation_mm = _float(getattr(obj, "LevelElevation", 0.0), 0.0)
        level_id = f"{project_id}:level:{_slug(level_name)}"
        conn.execute(
            """
            INSERT INTO levels (level_id, project_id, external_id, name, elevation_m, height_m, data_json)
            VALUES (?, ?, ?, ?, ?, 3, ?)
            ON CONFLICT(project_id, name) DO UPDATE SET
                elevation_m=excluded.elevation_m,
                data_json=excluded.data_json
            """,
            (
                level_id,
                project_id,
                f"freecad:level:{level_name}",
                level_name,
                elevation_mm / 1000.0,
                json.dumps({"source": "freecad"}, ensure_ascii=False),
            ),
        )
        row = conn.execute(
            "SELECT level_id FROM levels WHERE project_id = ? AND name = ?",
            (project_id, level_name),
        ).fetchone()
        return row[0] if row else level_id

    @staticmethod
    def ensure_panel(conn, project_id, panel_name):
        panel_name = _text(panel_name).strip()
        if not panel_name:
            return None
        panel_id = f"{project_id}:panel:{_slug(panel_name)}"
        conn.execute(
            """
            INSERT INTO panels (panel_id, project_id, external_id, name, data_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_id, external_id) DO UPDATE SET
                name=excluded.name,
                data_json=excluded.data_json
            """,
            (
                panel_id,
                project_id,
                f"freecad:panel:{panel_name}",
                panel_name,
                json.dumps({"source": "freecad", "name": panel_name}, ensure_ascii=False),
            ),
        )
        return panel_id

    @staticmethod
    def ensure_circuit(conn, project_id, panel_id, circuit_number, voltage):
        circuit_number = _text(circuit_number).strip()
        if not circuit_number:
            return None
        circuit_id = f"{project_id}:circuit:{_slug(panel_id or 'sem_painel')}:{_slug(circuit_number)}"
        conn.execute(
            """
            INSERT INTO circuits (circuit_id, project_id, external_id, panel_id, code, voltage, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, panel_id, code) DO UPDATE SET
                voltage=excluded.voltage,
                data_json=excluded.data_json
            """,
            (
                circuit_id,
                project_id,
                f"freecad:circuit:{panel_id or 'sem_painel'}:{circuit_number}",
                panel_id,
                circuit_number,
                voltage,
                json.dumps({"source": "freecad", "code": circuit_number}, ensure_ascii=False),
            ),
        )
        row = conn.execute(
            """
            SELECT circuit_id FROM circuits
            WHERE project_id = ? AND (panel_id IS ? OR panel_id = ?) AND code = ?
            """,
            (project_id, panel_id, panel_id, circuit_number),
        ).fetchone()
        return row[0] if row else circuit_id

    @staticmethod
    def family_from_object(obj):
        source = _text(getattr(obj, "SourceFile", ""), "")
        family_id = _slug(os.path.splitext(os.path.basename(source))[0] if source else getattr(obj, "FamilyName", obj.Name))
        modules = _int(getattr(obj, "ModuleCount", 1), 1)
        category = _load_category(getattr(obj, "FamilyCategory", ""), getattr(obj, "LoadClassification", ""))
        return {
            "id": family_id,
            "name": _text(getattr(obj, "FamilyName", ""), _text(getattr(obj, "Label", ""), family_id)),
            "category": category,
            "discipline": "Eletrica",
            "ifc_class": _text(getattr(obj, "IFC_Class", ""), "IfcDistributionElement"),
            "source_3d": source,
            "source_2d": "",
            "modules": f"{modules} Modulo",
            "amperage": _text(getattr(obj, "Amperage", ""), ""),
            "voltage": _text(getattr(obj, "Voltage", ""), "127V"),
            "power": _float(getattr(obj, "Power", 0.0), 0.0),
            "apparent_power_va": _float(getattr(obj, "ApparentPowerVA", 0.0), 0.0),
            "active_power_w": _float(getattr(obj, "ActivePowerW", 0.0), 0.0),
            "power_factor": _float(getattr(obj, "PowerFactor", 1.0), 1.0),
            "demand_factor": _float(getattr(obj, "DemandFactor", 1.0), 1.0),
            "phase": _text(getattr(obj, "Phase", ""), "R"),
            "load_classification": _text(getattr(obj, "LoadClassification", ""), ""),
            "socket_application": _text(getattr(obj, "SocketApplication", ""), ""),
            "ip_rating": _text(getattr(obj, "IP_Rating", ""), ""),
            "electrical_standard": _text(getattr(obj, "ElectricalStandard", ""), "NBR 5410"),
            "height_type": _text(getattr(obj, "HeightType", ""), ""),
            "mounting_height": _float(getattr(obj, "MountingHeight", 0.0), 0.0),
            "manufacturer": _text(getattr(obj, "Manufacturer", ""), ""),
            "model": _text(getattr(obj, "Model", ""), ""),
            "catalog_code": _text(getattr(obj, "CatalogCode", ""), ""),
            "description": _text(getattr(obj, "FamilyDescription", ""), ""),
        }

    @staticmethod
    def sync_element(obj, path=None):
        if not is_sync_enabled() or not obj:
            return None
        doc = getattr(obj, "Document", None)
        if not doc:
            return None

        conn = UnifiedSQLite.connect(path)
        try:
            project_id = UnifiedSQLite.ensure_project(conn, doc)
            level_id = UnifiedSQLite.ensure_level(conn, project_id, obj)
            family_id = UnifiedSQLite.upsert_family(conn, UnifiedSQLite.family_from_object(obj))
            panel_id = UnifiedSQLite.ensure_panel(conn, project_id, getattr(obj, "PanelBoard", ""))
            voltage = _int(getattr(obj, "Voltage", ""), 127)
            circuit_id = UnifiedSQLite.ensure_circuit(conn, project_id, panel_id, getattr(obj, "CircuitNumber", ""), voltage)

            placement = getattr(obj, "Placement", None)
            base = getattr(placement, "Base", None)
            x_m = _float(getattr(base, "x", 0.0), 0.0) / 1000.0
            y_m = _float(getattr(base, "y", 0.0), 0.0) / 1000.0
            z_m = _float(getattr(base, "z", 0.0), 0.0) / 1000.0
            rotation_z = 0.0
            try:
                rotation_z = float(placement.Rotation.toEuler()[0])
            except Exception:
                pass

            external_id = f"freecad:{doc.Name}:{obj.Name}"
            element_id = external_id
            load_category = _load_category(getattr(obj, "FamilyCategory", ""), getattr(obj, "LoadClassification", ""))
            payload = UnifiedSQLite.object_payload(obj)
            conn.execute(
                """
                INSERT INTO project_elements (
                    element_id, project_id, external_id, source_app, name, family_id,
                    category, ifc_class, level_id, panel_id, circuit_id, circuit_number,
                    panel_board, space_or_sector, tag, x_m, y_m, z_m, rotation_z_deg,
                    voltage, phase, active_power_watts, apparent_power_va, power_factor,
                    demand_factor, load_category, mounting_height_mm, final_elevation_mm,
                    host_object, host_face, data_json, updated_at
                ) VALUES (?, ?, ?, 'freecad', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(project_id, external_id) DO UPDATE SET
                    name=excluded.name,
                    family_id=excluded.family_id,
                    category=excluded.category,
                    ifc_class=excluded.ifc_class,
                    level_id=excluded.level_id,
                    panel_id=excluded.panel_id,
                    circuit_id=excluded.circuit_id,
                    circuit_number=excluded.circuit_number,
                    panel_board=excluded.panel_board,
                    space_or_sector=excluded.space_or_sector,
                    tag=excluded.tag,
                    x_m=excluded.x_m,
                    y_m=excluded.y_m,
                    z_m=excluded.z_m,
                    rotation_z_deg=excluded.rotation_z_deg,
                    voltage=excluded.voltage,
                    phase=excluded.phase,
                    active_power_watts=excluded.active_power_watts,
                    apparent_power_va=excluded.apparent_power_va,
                    power_factor=excluded.power_factor,
                    demand_factor=excluded.demand_factor,
                    load_category=excluded.load_category,
                    mounting_height_mm=excluded.mounting_height_mm,
                    final_elevation_mm=excluded.final_elevation_mm,
                    host_object=excluded.host_object,
                    host_face=excluded.host_face,
                    data_json=excluded.data_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    element_id,
                    project_id,
                    external_id,
                    _text(getattr(obj, "Label", ""), obj.Name),
                    family_id,
                    load_category,
                    _text(getattr(obj, "IFC_Class", ""), ""),
                    level_id,
                    panel_id,
                    circuit_id,
                    _text(getattr(obj, "CircuitNumber", ""), ""),
                    _text(getattr(obj, "PanelBoard", ""), ""),
                    _text(getattr(obj, "SpaceOrSector", ""), ""),
                    _text(getattr(obj, "Tag", ""), ""),
                    x_m,
                    y_m,
                    z_m,
                    rotation_z,
                    voltage,
                    _text(getattr(obj, "Phase", ""), "R"),
                    _float(getattr(obj, "ActivePowerW", 0.0), 0.0),
                    _float(getattr(obj, "ApparentPowerVA", 0.0), 0.0),
                    _float(getattr(obj, "PowerFactor", 1.0), 1.0),
                    _float(getattr(obj, "DemandFactor", 1.0), 1.0),
                    load_category,
                    _float(getattr(obj, "MountingHeight", 0.0), 0.0),
                    _float(getattr(obj, "FinalElevation", 0.0), 0.0),
                    _text(getattr(obj, "HostObject", ""), ""),
                    _text(getattr(obj, "HostFace", ""), ""),
                    json.dumps(payload, ensure_ascii=False, sort_keys=True),
                ),
            )

            connector_id = f"{element_id}:entrada"
            family_connector_id = f"{family_id}:entrada"
            conn.execute(
                """
                INSERT OR REPLACE INTO element_connectors (
                    connector_id, element_id, family_connector_id, name, connector_type,
                    x_m, y_m, z_m, dir_x, dir_y, dir_z, diameter_mm, voltage, phase,
                    max_load_va, connected_circuit_id, data_json
                ) VALUES (?, ?, ?, 'Entrada', 'Conduit', ?, ?, ?, 0, -1, 0, 20, ?, ?, ?, ?, ?)
                """,
                (
                    connector_id,
                    element_id,
                    family_connector_id,
                    x_m,
                    y_m,
                    z_m,
                    voltage,
                    _text(getattr(obj, "Phase", ""), "R"),
                    _float(getattr(obj, "ApparentPowerVA", 0.0), 0.0),
                    circuit_id,
                    json.dumps({"source": "freecad", "object": obj.Name}, ensure_ascii=False),
                ),
            )
            UnifiedSQLite.add_event(conn, "project_element", element_id, "upsert", payload)
            conn.commit()
            return element_id
        finally:
            conn.close()

    @staticmethod
    def add_event(conn, entity_type, entity_id, action, payload):
        conn.execute(
            """
            INSERT INTO sync_events (
                event_id, source_app, target_app, entity_type, entity_id, action, payload_json
            ) VALUES (?, 'freecad', 'rust', ?, ?, ?, ?)
            """,
            (
                _now_source_id("freecad:event"),
                entity_type,
                entity_id,
                action,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
            ),
        )

    @staticmethod
    def object_payload(obj):
        props = {}
        for name in getattr(obj, "PropertiesList", []):
            try:
                value = getattr(obj, name)
                value = _plain(value)
                if isinstance(value, (str, int, float, bool)) or value is None:
                    props[name] = value
                else:
                    props[name] = str(value)
            except Exception:
                pass
        return {
            "schema_version": 1,
            "source_app": "freecad",
            "external_id": f"freecad:{getattr(getattr(obj, 'Document', None), 'Name', '')}:{getattr(obj, 'Name', '')}",
            "name": _text(getattr(obj, "Label", ""), getattr(obj, "Name", "")),
            "freecad_name": _text(getattr(obj, "Name", ""), ""),
            "type_id": _text(getattr(obj, "TypeId", ""), ""),
            "properties": props,
        }


def export_family_catalog(path=None):
    return UnifiedSQLite.export_family_catalog(path)


def sync_element(obj, path=None):
    return UnifiedSQLite.sync_element(obj, path)
