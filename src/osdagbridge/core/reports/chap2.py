# Chapter 2: Input Parameters — exact LaTeX template match


from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_CB_TYPE,
    KEY_CROSS_BRACING,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DO_GAMMA_C_BASIC,
    KEY_DO_GAMMA_FLT,
    KEY_DO_GAMMA_M0,
    KEY_DO_GAMMA_M1,
    KEY_DO_GAMMA_MF,
    KEY_DO_GAMMA_S,
    KEY_DO_GAMMA_V,
    KEY_END_DIAPHRAGM,
    KEY_FOOTPATH,
    KEY_GIRDER,
    KEY_INCLUDE_MEDIAN,
    KEY_MD_TYPE,
    KEY_MP_CB_BRACING_SECTION_DESIGNATION,
    KEY_MP_CB_MEMBER_ID,
    KEY_MP_CB_SELECT_GIRDERS,
    KEY_MP_CB_SPACING,
    KEY_MP_CB_TYPE,
    KEY_MP_ED_BRACING_SECTION_DESIGNATION,
    KEY_MP_ED_MEMBER_ID,
    KEY_MP_ED_SELECT_GIRDERS,
    KEY_MP_ED_TYPE,
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS,
    KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH,
    KEY_MP_GIRDER_DEPTH,
    KEY_MP_GIRDER_SYMMETRY,
    KEY_MP_GIRDER_TOP_FLANGE_THICKNESS,
    KEY_MP_GIRDER_TOP_FLANGE_WIDTH,
    KEY_MP_GIRDER_TORSIONAL_RESTRAINT,
    KEY_MP_GIRDER_TYPE,
    KEY_MP_GIRDER_WARPING_RESTRAINT,
    KEY_MP_GIRDER_WEB_THICKNESS,
    KEY_MP_GIRDER_WEB_TYPE,
    KEY_MP_STIFFENER_BEARING_THICKNESS,
    KEY_MP_STIFFENER_INTERMEDIATE,
    KEY_MP_STIFFENER_INTERMEDIATE_SPACING,
    KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS,
    KEY_MP_STIFFENER_LONGITUDINAL,
    KEY_MP_STIFFENER_NO_BEARING_STIFFENERS,
    KEY_MP_STIFFENER_SPACING,
    KEY_RL_LOAD_VALUE,
    KEY_RL_TYPE,
    KEY_SD_SHEAR_DIAMETER,
    KEY_SD_SHEAR_HEIGHT,
    KEY_SD_SHEAR_STUDS_PER_SECTION,
    KEY_SD_SHEAR_ULTIMATE_STRENGTH,
    KEY_SD_SHEAR_YIELD_STRENGTH,
    KEY_SKEW_ANGLE,
    KEY_SPAN,
    KEY_STRUCTURE_TYPE,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_GIRDER_SPACING,
    KEY_TS_NO_OF_GIRDERS,
    KEY_TS_OVERALL_WIDTH,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS
)

from osdagbridge.core.reports.report_utils import _render_value, get_girder_entries, _tex
from osdagbridge.core.reports.styles import make_longtable

def ch2_input_parameters(m, input_dict, output_dict=None):
    girder_entries = get_girder_entries(input_dict)
    n_girders = len(girder_entries)
    # Median row only shown when the user included a median
    median_row = ""
    if str(input_dict.get(KEY_INCLUDE_MEDIAN, "")).strip().lower() in ("yes", "true", "1"):
        median_row = (r"\textnormal{Median Type} & "
                      + _render_value(input_dict, KEY_MD_TYPE)
                      + r""" \\
\hline
""")
    return r"""
\chapter{Input Parameters}


This section documents all inputs provided to OsdagBridge. User-provided inputs are clearly distinguished from software-assumed defaults. Where the user did not supply a value, the software has applied the IRC/IS code default or an empirical guideline; these are annotated with an asterisk (\sdstar{}).

\section{Basic Inputs (User-Defined)}
\label{sec:basic-inputs}

\noindent\textit{Note: These inputs are mandatory and were provided by the user.}
""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Project Location} & """ + _tex(m.project_location) + r""" \\
\hline
\textnormal{Latitude / Longitude} & """ + (_render_value(input_dict,'latitude')) + ', ' + (_render_value(input_dict,'longitude')) + r""" \\
\hline
\textnormal{Seismic Zone (IRC 6)} & """ + (_render_value(input_dict,'seismic_zone')) + r""" \\
\hline
\textnormal{Basic Wind Speed (IRC 6)} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" \\
\hline
\textnormal{Shade Temp. Max / Min (IRC 6)} & """ + (_render_value(input_dict,'shade_temp_max','')) + r""" °C / """ + (_render_value(input_dict,'shade_temp_min','')) + r""" °C \\
\hline"""),
    'L5.5 L8.5',
    caption=r"Project Location", label=r"subsec:project-location") + r"""
""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Type of Structure} & """ + (_render_value(input_dict, KEY_STRUCTURE_TYPE)) + r""" \\
\hline
\textnormal{Span (m)} & """ + (_render_value(input_dict, KEY_SPAN, ' m')) + r""" \\
\hline
\textnormal{Carriageway Width (m)} & """ + (_render_value(input_dict, KEY_CARRIAGEWAY_WIDTH, ' m')) + r""" \\
\hline
\textnormal{Include Median} & """ + (_render_value(input_dict, KEY_INCLUDE_MEDIAN)) + r""" \\
\hline
\textnormal{Footpath} & """ + (_render_value(input_dict, KEY_FOOTPATH)) + r""" \\
\hline
\textnormal{Skew Angle (degrees)} & """ + (_render_value(input_dict, KEY_SKEW_ANGLE, '°')) + r""" (IRC 24 Cl. 504.8 limit: $\pm$15°) \\
\hline"""),
    'L5.5 L8.5',
    caption=r"Bridge Geometry", label=r"subsec:bridge-geometry") + r"""
""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Girder Steel Grade (IS 2062)} & """ + (_render_value(input_dict, KEY_GIRDER)) + r""" \\
\hline
\textnormal{Cross Bracing Steel Grade} & """ + (_render_value(input_dict, KEY_CROSS_BRACING)) + r""" \\
\hline
\textnormal{End Diaphragm Steel Grade} & """ + (_render_value(input_dict, KEY_END_DIAPHRAGM)) + r""" \\
\hline
\textnormal{Concrete Deck Grade (IRC 22)} & """ + (_render_value(input_dict, KEY_DECK_CONCRETE_GRADE_BASIC)) + r""" \\
\hline"""),
    'L5.5 L8.5',
    caption=r"Material Selection", label=r"subsec:material") + r"""

\section{Additional Inputs}
\label{sec:additional-inputs}

Where the user has modified additional inputs, those values are reported here. Where no modification was made, the software default is shown.

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Overall Bridge Width (m)} & """ + (_render_value(input_dict, KEY_TS_OVERALL_WIDTH)) + r""" \\
\hline
\textnormal{No. of Girders} & """ + (_render_value(input_dict, KEY_TS_NO_OF_GIRDERS)) + r""" \\
\hline
\textnormal{Girder Spacing (m)} & """ + (_render_value(input_dict, KEY_TS_GIRDER_SPACING, ' m')) + r""" \\
\hline
\textnormal{Deck Overhang Width (m)} & """ + (_render_value(input_dict, KEY_TS_DECK_OVERHANG, ' m')) + r""" \\
\hline
\textnormal{Deck Thickness (mm)} & """ + (_render_value(input_dict, KEY_TS_DECK_THICKNESS, ' mm')) + r""" \\
\hline
\textnormal{Footpath Width (m)} & """ + (_render_value(input_dict, KEY_TS_FOOTPATH_WIDTH, ' m')) + r""" (IRC 5 Cl. 104.3.6 min: 1.5 m) \\
\hline
\textnormal{No. of Traffic Lanes} & """ + (_render_value(input_dict, KEY_WC_LD_LANE_TABLE_COUNT)) + r""" (per IRC 5 Cl. 104.3.1) \\
\hline"""),
    'L5.5 L10',
    caption=r"Typical Section Details") + r"""

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Crash Barrier Type} & """ + (_render_value(input_dict, KEY_CB_TYPE)) + r""" \\
\hline
\textnormal{Crash Barrier Load (kN/m)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" \\
\hline
""" + median_row + r"""
\textnormal{Railing Type} & """ + (_render_value(input_dict, KEY_RL_TYPE)) + r""" \\
\hline
\textnormal{Railing Load (kN/m)} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" \\
\hline
\textnormal{Wearing Course Material} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" \\
\hline
\textnormal{Wearing Course Thickness (mm)} & """ + (_render_value(input_dict, KEY_WC_THICKNESS, ' mm')) + r""" \\
\hline"""),
    'L5.5 L10',
    caption=r"Components Details") + r"""

""" + _girder_tables(input_dict, n_girders) + r"""

""" + _bracing_tables(input_dict, n_girders) + r"""

""" + _shear_connector_table(input_dict, output_dict) + r"""

""" + _safety_factors_table(input_dict)


def _girder_tables(input_dict, n_girders):
    # Fetch backend-populated labels via exact suffix pattern (defaults.py)
    # KEY_MP_GD_SELECT_GIRDER.G{i}    = 'G{i}'
    # KEY_MP_GD_MEMBER_ID.G{i}.M1     = 'G{i}M1'
    # All other girder/stiffener keys: {BASE_KEY}.G{i}.M1
    n = n_girders if n_girders >= 1 else 1
    girder_entries = get_girder_entries(input_dict)
    if not girder_entries:
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
    
    entries_for_table = [
        (lbl, mid, i)
        for i, (lbl, mid) in enumerate(
            girder_entries,
            start=1,
        )
    ]

    # Helper: one girder-dimension row
    def _dim_row(g_lbl, i):
        return (g_lbl + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_DEPTH}.G{i}.M1", ' mm'))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_WEB_THICKNESS}.G{i}.M1", ' mm'))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_TOP_FLANGE_WIDTH}.G{i}.M1", ' mm'))
                + ', '
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_TOP_FLANGE_THICKNESS}.G{i}.M1", ' mm'))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_BOTTOM_FLANGE_WIDTH}.G{i}.M1", ' mm'))
                + ', '
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_BOTTOM_FLANGE_THICKNESS}.G{i}.M1", ' mm'))
                + r""" \\
\hline
""")

    # Helper: one general-info row
    def _gen_row(g_lbl, m_id, i):
        return (g_lbl + r""" & """ + m_id + r""" & """
                + (_render_value(input_dict, KEY_DESIGN_MODE))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_TYPE}.G{i}.M1"))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_SYMMETRY}.G{i}.M1"))
                + r""" \\
\hline
""")

    # Helper: one restraint/stiffener row
    def _rst_row(g_lbl, i):
        return (g_lbl + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_TORSIONAL_RESTRAINT}.G{i}.M1"))
                + ', '
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_WARPING_RESTRAINT}.G{i}.M1"))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_GIRDER_WEB_TYPE}.G{i}.M1"))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE}.G{i}.M1"))
                + '; Spacing: '
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE_SPACING}.G{i}.M1", ' mm'))
                + '; Thickness: '
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_INTERMEDIATE_THICKNESS}.G{i}.M1", ' mm'))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_LONGITUDINAL}.G{i}.M1"))
                + r""" & No.: """
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_NO_BEARING_STIFFENERS}.G{i}.M1"))
                + '; Spacing: '
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_SPACING}.G{i}.M1", ' mm'))
                + '; Thickness: '
                + (_render_value(input_dict, f"{KEY_MP_STIFFENER_BEARING_THICKNESS}.G{i}.M1", ' mm'))
                + r""" \\
\hline
""")

    gen_rows = "".join([_gen_row(g_lbl, m_id, i) for g_lbl, m_id, i in entries_for_table])
    dim_rows = "".join([_dim_row(g_lbl, i) for g_lbl, _, i in entries_for_table])
    rst_rows = "".join([_rst_row(g_lbl, i) for g_lbl, _, i in entries_for_table])

    return (r"""

\noindent
            
""" + make_longtable(
    [r"Girder", r"Member ID", r"Design Mode", r"Girder Type", r"Girder Symmetry"],
    (r""""""
            + gen_rows
            + r""""""),
    'L2.2 L1.8 L3.8 L3.8 L3.8',
    caption=r"Girder General Information") + r"""


""" + make_longtable(
    [r"Girder", r"Total Depth, D (mm)", r"Web, $t_w$ (mm)", r"Top Flange (b\textsubscript{tf}, t\textsubscript{tf}) mm", r"Bottom Flange (b\textsubscript{bf}, t\textsubscript{bf}) mm"],
    (r""""""
            + dim_rows
            + r""""""),
    'L1.8 L2.3 L1.8 L4.8 L4.8',
    caption=r"Girder Section Dimensions") + r"""


""" + make_longtable(
    [r"Girder", r"Torsional / Warping Restraint", r"Web Philosophy", r"Intermediate Stiffeners", r"Longitudinal Stiffeners", r"Bearing Stiffener"],
    (r""""""
            + rst_rows
            + r""""""),
    'L1.4 L2.2 L2.2 L3 L2.4 L2.2',
    caption=r"Girder Restraint and Stiffener Details") + r"""
""")


def _bracing_tables(input_dict, n_girders):
    n = n_girders if n_girders >= 2 else 2
    panels = [
        (
            _render_value(input_dict, f"{KEY_MP_CB_SELECT_GIRDERS}.G{i}G{i+1}.B{i}M1"),
            _render_value(input_dict, f"{KEY_MP_CB_MEMBER_ID}.G{i}G{i+1}.B{i}M1"),
            _render_value(input_dict, f"{KEY_MP_ED_SELECT_GIRDERS}.G{i}G{i+1}.E{i}M1"),
            _render_value(input_dict, f"{KEY_MP_ED_MEMBER_ID}.G{i}G{i+1}.E{i}M1"),
            i
        )
        for i in range(1, n)
    ]

    # Helper: one cross-bracing row (all locations share same bracing config)
    def _cb_row(location, member_ids, i):
        return (location + r""" & """ + member_ids + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_CB_TYPE}.G{i}G{i+1}.B{i}M1"))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_CB_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.B{i}M1"))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_CB_SPACING}.G{i}G{i+1}.B{i}M1", ' m'))
                + r""" \\
\hline
""")

    # Helper: one end-diaphragm row (all locations share same config)
    def _ed_row(location, member_ids, i):
        return (location + r""" & """ + member_ids + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_ED_TYPE}.G{i}G{i+1}.E{i}M1"))
                + r""" & """
                + (_render_value(input_dict, f"{KEY_MP_ED_BRACING_SECTION_DESIGNATION}.G{i}G{i+1}.E{i}M1"))
                + r""" \\
\hline
""")

    cb_rows = "".join([_cb_row(cb_loc, cb_ids, i) for cb_loc, cb_ids, _, _, i in panels])
    ed_rows = "".join([_ed_row(ed_loc, ed_ids, i) for _, _, ed_loc, ed_ids, i in panels])

    return (r"""

""" + make_longtable(
    [r"Location", r"Member IDs", r"Type of Bracing", r"Bracing Section", r"Spacing (m)"],
    (r""""""
+ cb_rows
+ r""""""),
    'L2.2 L2.2 L3 L2.5 C1.8',
    caption=r"Member Properties: Cross Bracing Details") + r"""

\noindent
""" + make_longtable(
    [r"Location", r"Member IDs", r"Type of Bracing", r"Bracing Section"],
    (r""""""
+ ed_rows
+ r""""""),
    'L2.2 L2.2 L3 L2.5',
    caption=r"Member Properties: End Diaphragm Details") + r"""
""")


def _shear_connector_table(input_dict, output_dict=None):
    # Stud computed properties live in output_dict (populated by store_design_results)
    od = output_dict or {}
    return r"""
\label{subsec:shear-connectors}


""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{Stud Diameter (mm)} & """ + (_render_value(od, KEY_SD_SHEAR_DIAMETER, ' mm')) + r""" \\
\hline
\textnormal{Stud Height (mm)} & """ + (_render_value(od, KEY_SD_SHEAR_HEIGHT, ' mm')) + r""" \\
\hline
\textnormal{Stud $f_y$ (MPa)} & """ + (_render_value(od, KEY_SD_SHEAR_YIELD_STRENGTH, ' MPa')) + r""" \\
\hline
\textnormal{Stud $f_u$ (MPa)} & """ + (_render_value(od, KEY_SD_SHEAR_ULTIMATE_STRENGTH, ' MPa')) + r""" \\
\hline
\textnormal{No. of Studs per Section} & """ + (_render_value(od, KEY_SD_SHEAR_STUDS_PER_SECTION)) + r""" \\
\hline"""),
    'L5.5 L10',
    caption=r"Shear Connector Details") + r"""
"""

def _safety_factors_table(input_dict):
    return r"""
\label{subsec:safety-factors}


\noindent\textit{Note: All values are per IRC 22 Table 1 unless user-modified.}

""" + make_longtable(
    [r"Parameter", r"Value"],
    (r"""\textnormal{$\gamma_{M0}$ (Yielding / Buckling)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_M0)) + r""" \\
\hline
\textnormal{$\gamma_{M1}$ (Ultimate Stress)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_M1)) + r""" \\
\hline
\textnormal{$\gamma_C$ (Concrete, Basic)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_C_BASIC)) + r""" \\
\hline
\textnormal{$\gamma_s$ (Reinforcement)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_S)) + r""" \\
\hline
\textnormal{$\gamma_v$ (Shear Connectors)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_V)) + r""" \\
\hline
\textnormal{$\gamma_{fft}$ (Fatigue Load)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_FLT)) + r""" \\
\hline
\textnormal{$\gamma_{Mft}$ (Fatigue Strength)} & """ + (_render_value(input_dict, KEY_DO_GAMMA_MF)) + r""" \\
\hline"""),
    'L5.5 L10',
    caption=r"Partial Safety Factors") + r"""
"""

