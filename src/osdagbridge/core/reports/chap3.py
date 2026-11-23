# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

import re

from osdagbridge.core.utils.common import (
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_CLASS_SV,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_FOOTPATH,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_CB_LOAD,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
from osdagbridge.core.utils.codes.keyfile import kN
from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.styles import make_longtable

# (UI check box key, label, name used in the analysis load cases, geometry method)
_UI_VEHICLES = [
    (KEY_LL_IRC_CLASS_A,       "Class A",             "ClassA",   "cl_204_1_ClassA_vehicle"),
    (KEY_LL_IRC_AA_WHEELED,    "Class AA (Wheeled)",  None, None),
    (KEY_LL_IRC_AA_TRACKED,    "Class AA (Tracked)",  None, None),
    (KEY_LL_IRC_70R_WHEELED,   "Class 70R (Wheeled)", "Class70R", "cl_204_1_Class70R_vehicle_wheel"),
    (KEY_LL_IRC_70R_TRACKED,   "Class 70R (Tracked)", None, None),
    (KEY_LL_IRC_70R_BOGIE,     "Class 70R (Bogie)",   None, None),
    (KEY_LL_IRC_CLASS_SV,      "Class SV",            None, None),
    (KEY_LL_IRC_CLASS_FATIGUE, "Class Fatigue",       None, None),
]


def _analysed_vehicles(output_dict):
    """Vehicle names in the analysed load cases, e.g. 'Case2 1xClassA + 1xClass70R'."""
    per_girder = ((output_dict or {}).get("design_results") or {}).get("per_girder") or {}
    found = set()
    for girder in per_girder.values():
        for case in (girder.get("per_lc") or {}):
            if re.match(r"Case\d+ ", str(case)):
                found.update(re.findall(r"\d+x(\w+)", str(case)))
    return found


def _live_load_tables(input_dict, output_dict):
    """Vehicle and footpath live load tables.

    One row per vehicle selected in the UI Loading tab. Values are given only
    for vehicles found in the analysis results.
    """
    analysed = _analysed_vehicles(output_dict)
    selected = [v for v in _UI_VEHICLES if input_dict.get(v[0])]
    for custom_vehicle in input_dict.get(KEY_LL_CUSTOM_VEHICLES) or []:
        name = custom_vehicle.get("name") if isinstance(custom_vehicle, dict) else custom_vehicle
        if name:
            selected.append((None, str(name), None, None))

    # The analysis applies one dynamic factor (Cl. 208.3) to every vehicle case.
    try:
        impact = f"{1.0 + IRC6_2017.cl_208_3_impact_factor(float(input_dict.get(KEY_SPAN))):.3f}"
    except Exception:
        impact = "N/A"

    rows, skipped = [], False
    for _, label, name, method in selected:
        if name in analysed:
            total = sum(getattr(IRC6_2017, method)()["wheel_loads"]) / kN
            # Braking load is not part of the analysis.
            rows.append([_tex(label), f"{total:.1f}", impact, "No", "N/A", "N/A"])
        elif not analysed:
            rows.append([_tex(label)] + ["N/A"] * 5)
        else:
            skipped = True
            rows.append([_tex(label), r"\multicolumn{5}{c|}{Not analysed\textsuperscript{\dag}}"])
    if not rows:
        rows = [[r"\multicolumn{6}{|c|}{No vehicle selected}"]]
    vehicle_table = make_longtable(
        None, rows, "L3.2 C2.2 C2.2 C2.6 C2.2 C2.8",
        caption="Vehicle Live Loads", head=(
            r"\rowcolor{osdagHeader} & & & \multicolumn{3}{c|}{\textbf{Braking Load}} \\" "\n"
            r"\rowcolor{osdagHeader} \textbf{Vehicle} & \textbf{Total Load (kN)}"
            r" & \textbf{Impact Factor} & \textbf{Considered?}"
            r" & \textbf{Value (kN)} & \textbf{Eccentricity (m)} \\"))
    notes = []
    if skipped:
        notes.append(r"\textsuperscript{\dag}Selected in the Loading tab, but no load case "
                     r"for this vehicle exists in the analysis results.")
    selected_names = {name for _, _, name, _ in selected}
    unselected = [label for _, label, name, _ in _UI_VEHICLES if name in analysed - selected_names]
    if unselected:
        notes.append("Analysed although not selected: " + _tex(", ".join(unselected)) + ".")
    notes.append("Impact factor: IRC 6 Cl. 208.3 value applied by the analysis to all vehicles. "
                 "Braking (Cl. 211) and centrifugal (Cl. 212) loads are not included in the "
                 "analysis. N/A = not available.")
    vehicle_table += r"\noindent\textit{Note: " + " ".join(notes) + "}\n"

    mode = str(input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE) or "").strip()
    custom = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE)
    footpath = str(input_dict.get(KEY_FOOTPATH) or "None").strip()
    if footpath.lower() == "none":
        pressure, unit, ref = "Not applicable (no footpath)", "---", "---"
    elif mode.lower() in ("as per irc 6", "as per irc6", "automatic"):
        pressure, unit, ref = f"{IRC6_2017.cl_206_1_footway_load():.3f}", r"kN/m\textsuperscript{2}", "IRC 6 Cl. 206.1"
    elif custom not in (None, ""):
        pressure, unit, ref = _tex(custom), r"kN/m\textsuperscript{2}", "User-defined"
    else:
        pressure, unit, ref = "N/A", "---", "---"
    footpath_table = make_longtable(
        ["Parameter", "Value", "Unit", "Reference"],
        [["Footpath", _tex(footpath), "---", "Input"],
         ["Footpath Width", _render_value(input_dict, KEY_TS_FOOTPATH_WIDTH) or "N/A", "m", "IRC 5 Cl. 104.3.6"],
         ["Pressure Mode", _tex(mode) or "N/A", "---", "Input"],
         ["Footpath Live Load", pressure, unit, ref]],
        "L4.5 C4.5 C2.5 L4", caption="Footpath (Footway) Live Load")
    return vehicle_table, footpath_table


def ch3_loads(input_dict, output_dict):
    vehicle_table, footpath_table = _live_load_tables(input_dict, output_dict)

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\
\hline"""),
    'L5.5 L10',
    caption=r"Dead Load -- Self Weight") + r"""

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\
\hline"""),
    'L5.5 L10',
    caption=r"Dead Load for Surfacing (DW)") + r"""

""" + vehicle_table + r"""
""" + footpath_table + r"""

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\
\hline"""),
    'L5.5 L10',
    caption=r"Wind Load (WL) --- per IRC 6") + r"""

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\
\hline"""),
    'L5.5 L10',
    caption=r"Earthquake Load (EL) --- per IRC 6") + r"""

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\
\hline"""),
    'L5.5 L10',
    caption=r"Temperature Load (TL) --- per IRC 6") + r"""

""" + make_longtable(
    [r"Combination ID", r"Load Cases"],
    (r"""""" + lc_rows_str + r""""""),
    'C4 L11.5',
    caption=r"Load Combinations") + r"""

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


