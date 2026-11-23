import os

from osdagbridge.core.reports.charts import (
    figure_latex, plot_concrete_vs_rebar, plot_steel_tonnage)
from osdagbridge.core.reports.styles import make_longtable


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _quantity_figures(q, chart_dir):
    """Charts of the same values the bill of materials prints."""
    girders = _number(q.get("steel_girders_wt_total"))
    parts = [_number(q.get(f"bracing_{m}_wt_total")) for m in ("top", "bot", "diag")]
    bracing = None if None in parts else sum(parts)
    # The bill of materials has no end diaphragm quantity.
    diaphragm = _number(q.get("end_diaphragm_wt_total"))
    steel = plot_steel_tonnage(["Girders", "Cross Bracing", "End Diaphragms"],
                               [girders, bracing, diaphragm],
                               os.path.join(chart_dir, "steel_tonnage.png"))
    deck = plot_concrete_vs_rebar(_number(q.get("concrete_deck_vol_total")),
                                  _number(q.get("rebar_deck_wt_total")),
                                  os.path.join(chart_dir, "concrete_rebar.png"))
    note = ("" if diaphragm is not None else
            "\\noindent\\textit{Note: N/A --- the quantity take-off does not "
            "compute end diaphragm steel.}\n")
    return (figure_latex(steel, "Structural steel weight by component", "fig:steel-tonnage") + note
            + figure_latex(deck, "Deck concrete volume and reinforcement weight", "fig:concrete-rebar"))


def ch7_quantities(input_dict, chart_dir):
    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

""" + make_longtable(
    [r"S.N.", r"Item Description", r"Volume", r"Quantity", r"Total Volume", r"Weight (MT)", r"Total Weight (MT)"],
    (r"""1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline"""),
    'C1 L3.8 C2.6 C1.8 C1.8 C1.8 C1.8',
    caption=r"Bill of Materials (Steel, Concrete, and Reinforcement Quantities)") + _quantity_figures(input_dict, chart_dir)
