import json
import os
import sqlite3

try:
    import FreeCAD
except Exception:
    FreeCAD = None

from EletricaLogic.UnifiedSQLite import (
    _float,
    _int,
    _load_category,
    _module_count,
    _normalize_source,
    _slug,
    _symbology,
    _text,
)


WORKBENCH_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_RUST_FAMILY_DB = r"C:\Projetos\Eletrica Rust\familias.sqlite"


FAMILY_SCHEMA_SQL = """
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
    data_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY (family_id) REFERENCES families(family_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_family_category ON families(category);
CREATE INDEX IF NOT EXISTS idx_family_source_3d ON families(source_3d);
CREATE INDEX IF NOT EXISTS idx_family_connectors_family ON family_connectors(family_id);
"""


def get_family_database_path():
    if FreeCAD:
        try:
            params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Eletrica")
            configured = params.GetString("FamilySQLitePath", "")
            if configured:
                return configured
        except Exception:
            pass
    if os.path.isdir(os.path.dirname(DEFAULT_RUST_FAMILY_DB)):
        return DEFAULT_RUST_FAMILY_DB
    return os.path.join(WORKBENCH_DIR, "Library", "familias.sqlite")


def connect(path=None):
    path = path or get_family_database_path()
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(FAMILY_SCHEMA_SQL)
    conn.executemany(
        "INSERT OR REPLACE INTO app_metadata (key, value) VALUES (?, ?)",
        [
            ("schema_name", "eletrica_family_library"),
            ("schema_version", "1"),
            ("primary_format", "sqlite_json"),
            ("purpose", "families_only"),
            ("owner", "Eletrica FreeCAD + Eletrica Rust"),
        ],
    )
    conn.commit()
    return conn


def family_record_from_catalog(family):
    source_3d = _normalize_source(family.get("source_3d", ""))
    family_id = family.get("id") or _slug(source_3d or family.get("name"))
    load_category = _load_category(family.get("category"), family.get("load_classification"))
    modules = _module_count(family.get("modules"))
    voltage = _int(family.get("voltage"), 127)
    phase = family.get("phase", "R")
    apparent_power = _float(family.get("apparent_power_va"), _float(family.get("power"), 0.0))
    active_power = _float(family.get("active_power_w"), _float(family.get("power"), 0.0))
    symbol_2d = _symbology(load_category, modules)
    data = {
        "schema_version": 1,
        "family_id": family_id,
        "external_id": f"freecad:family:{family_id}",
        "name": family.get("name", family_id),
        "category": load_category,
        "discipline": family.get("discipline", "Eletrica"),
        "ifc_class": family.get("ifc_class", ""),
        "source_3d": source_3d,
        "source_2d": _normalize_source(family.get("source_2d", "")),
        "symbol_2d": symbol_2d,
        "electrical": {
            "load_category": load_category,
            "voltage": voltage,
            "phase": phase,
            "active_power_watts": active_power,
            "apparent_power_va": apparent_power,
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
            "weight_kg": _float(family.get("weight_kg"), 0.0),
            "ip_rating": family.get("ip_rating", ""),
            "fire_rating": family.get("fire_rating", ""),
            "material_name": family.get("material_name", ""),
            "material_density_kg_m3": _float(family.get("material_density_kg_m3"), 0.0),
            "embedded_carbon_kg_kg": _float(family.get("embedded_carbon_kg_kg"), 0.0),
            "cost_per_unit": _float(family.get("cost_per_unit"), 0.0),
        },
        "asset": {
            "manufacturer": family.get("manufacturer", ""),
            "model": family.get("model", ""),
            "catalog_code": family.get("catalog_code", ""),
            "description": family.get("description", ""),
            "omniclass_code": family.get("omniclass_code", ""),
            "uniformat_code": family.get("uniformat_code", ""),
            "expected_life_years": _float(family.get("expected_life_years"), 0.0),
            "maintenance_manual_url": family.get("maintenance_manual_url", ""),
        },
        "connectors": [
            {
                "connector_id": f"{family_id}:entrada",
                "name": "Entrada",
                "connector_type": "Conduit",
                "relative_position_mm": [0.0, -40.0, 0.0],
                "direction": [0.0, -1.0, 0.0],
                "diameter_mm": 20.0,
                "voltage": voltage,
                "phase": phase,
                "max_load_va": apparent_power,
            }
        ],
    }
    return data


def upsert_family(conn, family):
    data = family_record_from_catalog(family)
    family_id = data["family_id"]
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
            data["external_id"],
            data["name"],
            data["category"],
            data["discipline"],
            data["ifc_class"],
            data["source_3d"],
            data["source_2d"],
            data["symbol_2d"],
            json.dumps(data, ensure_ascii=False, sort_keys=True),
        ),
    )
    e = data["electrical"]
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
            e["load_category"],
            e["voltage"],
            e["phase"],
            e["active_power_watts"],
            e["apparent_power_va"],
            e["power_factor"],
            e["demand_factor"],
            e["utilization_factor"],
            e["simultaneity_factor"],
            e["harmonic_dist_thd"],
        ),
    )
    p = data["physical"]
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
            p["modules"],
            p["amperage"],
            p["socket_application"],
            p["mounting_height_mm"],
            p["height_type"],
            p["dimensions_mm"][0],
            p["dimensions_mm"][1],
            p["dimensions_mm"][2],
            p["weight_kg"],
            p["ip_rating"],
            p["fire_rating"],
            p["material_name"],
            p["material_density_kg_m3"],
            p["embedded_carbon_kg_kg"],
            p["cost_per_unit"],
        ),
    )
    a = data["asset"]
    conn.execute(
        """
        INSERT OR REPLACE INTO family_asset_defaults (
            family_id, manufacturer, model, catalog_code, description,
            omniclass_code, uniformat_code, expected_life_years, maintenance_manual_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            family_id,
            a["manufacturer"],
            a["model"],
            a["catalog_code"],
            a["description"],
            a["omniclass_code"],
            a["uniformat_code"],
            a["expected_life_years"],
            a["maintenance_manual_url"],
        ),
    )
    for connector in data["connectors"]:
        conn.execute(
            """
            INSERT OR REPLACE INTO family_connectors (
                connector_id, family_id, name, connector_type, x_mm, y_mm, z_mm,
                dir_x, dir_y, dir_z, diameter_mm, voltage, phase, max_load_va, data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                connector["connector_id"],
                family_id,
                connector["name"],
                connector["connector_type"],
                connector["relative_position_mm"][0],
                connector["relative_position_mm"][1],
                connector["relative_position_mm"][2],
                connector["direction"][0],
                connector["direction"][1],
                connector["direction"][2],
                connector["diameter_mm"],
                connector["voltage"],
                connector["phase"],
                connector["max_load_va"],
                json.dumps(connector, ensure_ascii=False, sort_keys=True),
            ),
        )
    return family_id


def export_family_catalog(path=None):
    from EletricaLogic.FamilyCatalog import list_families

    conn = connect(path)
    try:
        for family in list_families():
            upsert_family(conn, family)
        conn.commit()
    finally:
        conn.close()
    return path or get_family_database_path()


def family_from_object(obj):
    source = _text(getattr(obj, "SourceFile", ""), "")
    family_id = _slug(os.path.splitext(os.path.basename(source))[0] if source else getattr(obj, "FamilyName", obj.Name))
    modules = _int(getattr(obj, "ModuleCount", 1), 1)
    return {
        "id": family_id,
        "name": _text(getattr(obj, "FamilyName", ""), _text(getattr(obj, "Label", ""), family_id)),
        "category": _text(getattr(obj, "FamilyCategory", ""), ""),
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


def sync_family_from_object(obj, path=None):
    conn = connect(path)
    try:
        family_id = upsert_family(conn, family_from_object(obj))
        conn.commit()
        return family_id
    finally:
        conn.close()
