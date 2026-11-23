# Report generator map

Paths are relative to `src/osdagbridge/`. Report directory: `core/reports/`.

## Entry path
1. `desktop/ui/docks/output_dock.py` `_on_report_clicked` captures figure bytes on the Qt thread.
2. `desktop/ui/template_page.py` `open_report_dialog` builds a `ReportRequest` and starts `_ReportWorker`.
3. `core/bridge_types/plate_girder/plategirderbridge.py` `PlateGirderBridge.generate_design_report(request, cad_generator, is_preview)`.
   It copies `input_dict`, converts `output_dict` to a dict, and adds `analysis_summary` from `_lc_summary` / `_reaction_summary`.
   `cad_generator` is a dict; images are in `cad_generator["figure_data"]` as `{name: png bytes}`.
4. `core/reports/report_generator.py`: `build_report_payload(request, input_dict, output_dict)`, then `generate_report(payload, request)`.
   `generate_report` joins LaTeX strings, runs `pdflatex` twice in a temp dir and copies out the PDF and TEX.

The generator does NOT use PyLaTeX: no file in `src` imports it. Every chapter returns a raw LaTeX string.

## Files
| File | Produces |
|---|---|
| `report_generator.py` | preamble, title page, TOC, dataclasses, `ReportDataBridge` (cross bracing getters), orchestration |
| `report_utils.py` | `_tex`, `_render_value`, `get_girder_entries`, `_fig_or_placeholder`, `_fig_embed` |
| `executive_summary.py` | overview, key figures, Table 1, outcomes |
| `chap1.py` | project information |
| `chap2.py` | input parameters |
| `chap3.py` | loads and combinations |
| `chap4.py` | analysis results |
| `chap5.py` | design checks 5.1 to 5.5 |
| `chap6.py` | drawings |
| `chap7.py` | material take-off |
| `chap8.py` | standards, assumptions, limitations (`ch8_design_log`) |
| `chap9.py` | references |

## Where styling lives
- `geometry`, packages, `captionsetup`, `tabcolsep`, `arraystretch`, `osdagGreen`, fancyhdr and column types: `preamble()` in `report_generator.py`.
- `\titleformat` / `\titlespacing`: `toc_section()` and the end of `executive_summary.py` (which uses `-30pt`).
- `tabcolsep`, `LTleft`, `LTright`, `arraystretch` overrides: `chap2.py`, `chap4.py`, `chap5.py`, `chap7.py`, `chap8.py`. Those outside a group leak into later tables.
- Widths, `[6pt]` / `[8pt]` row gaps and `\textcolor{red}`: hardcoded throughout the chapters.
- Tables: `longtable` in chapters 2, 3, 4, 5, 7; `tabular` in the title page, executive summary, chapters 1, 2, 8. Only `chap4.py` (1 table) and `chap2.py` (1 table, empty `\endhead`) use `\endhead`.

## Suspected cause of the footer overlap
- `\multirow` groups forming rows up to 13 deep; `\footrule` uses `\vspace{-20pt}`; plain 1in margins with no `headheight` / `footskip`. To be confirmed on the baseline PDF.

## Chapter 3 live loads (`chap3.py`, `ch3_loads`)
- "Live Loads (LL)" holds vehicles, impact, braking and footpath in one 4-row table.
- A mode-aware `fp_str` is computed but unused; the table prints the raw footpath value, which is blank by default.
- The defaults treat the "As per IRC 6" footpath mode with an empty value.

## Vehicle selection (UI Loading tab)
- `ui_fields_additional_input.py` checkboxes store booleans in `input_dict`: `KEY_LL_IRC_CLASS_A`, `_AA_WHEELED`, `_AA_TRACKED`, `_70R_WHEELED`, `_70R_TRACKED`, `_70R_BOGIE`, `_CLASS_SV`, `_CLASS_FATIGUE`; `KEY_LL_CUSTOM_VEHICLES` (list, UI disabled).
- `KEY_BL_IRC_CLASS_SV` is a separate braking opt-in for Class SV. Other braking flags follow vehicle selection.
- `KEY_LL_ECCENTRICITY` (m, default 1.2). Footpath: `KEY_LL_FOOTPATH_PRESSURE_MODE` / `_VALUE`.
- `IRC6_2017.cl_211_2_braking_force` takes lane count only, so it yields no per-vehicle value. It uses `braking_force_2` before assignment for 1 or 2 lanes (caught as N/A). Out of scope to fix.
- No centrifugal force method was found in the searched IRC 6 class or plate girder code.

## Utilization ratios (Section 5.5 in `chap5.py`, `t522_content`)
- Girders: `output_dict["design_results"]["per_girder"][G]["checks"]` (`check_id`, `dcr`, `demand`, `capacity`); `per_lc` fallback.
- Deck: `output_dict["deck_report_values"]` (`KEY_DD_*`) demand / capacity; also `deck_design_results["ur_*"]`.
- Cross bracing: `output_dict["crossbracing_design_results"]` via `ReportDataBridge.get_cb_efficiency`.
- End diaphragm: `output_dict["end_diaphragm_design_results"]` exists, but `chap5.py` prints cross bracing data in Section 5.4 and in the 5.5 end diaphragm rows. Charts should read the real end diaphragm results.

## Chapter 7 quantities
- `core/boq/boq_generator.py` `calculate_material_quantities` adds string values to `payload.inputs`; `chap7.py` prints them.
- Girders `steel_girders_wt_total`; bracing `bracing_top|bot|diag_wt_total`; concrete `concrete_deck_vol_total`; rebar `rebar_deck_wt_total`.
- No end diaphragm quantity exists, so that bar will be N/A.

## Headless feasibility
- `BASIC_INPUT_DICT` and `solve_extend_basic_input_dict` (`core/bridge_types/plate_girder/defaults.py`), `PlateGirderBridge.set_input` and `design()` appear usable without the GUI. `examples/*.yaml` are placeholders. Not yet run: no Python environment.
