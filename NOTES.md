# Notes

## Test input (src/tools/make_test_report.py)
- Sample bridge chosen for this task: 30 m span, 10.5 m carriageway, footpaths both sides, 7 girders (derived), 10 deg skew. The repo's example YAML files are placeholders.
- Material properties come from the GUI: `MaterialPropertiesDialog.get_export_fields()` in `desktop/ui/dialogs/material_properties.py`, called as `InputDock._prime_material_inputs` does (grades from `BASIC_INPUT_DICT`; values from `Intg_osdag.sqlite`).
- CAD and plot images need the Qt viewer, so the headless reports show placeholders for them.
- `src/tools/` is matched by `.gitignore`, so the script was added with `git add -f`.

## End diaphragm data fix (Sections 5.4 and 5.5)
- Wrong before: the three 5.4 tables printed the cross bracing rows, and the 5.5 "Moment" / "Shear" rows printed cross bracing compression / tension.
- Correct source: `output_dict["end_diaphragm_design_results"]`, `["end_diaphragm_forces_dict"]`, and the `transverse_member_design.ed.section_properties.*` keys. Files: `report_generator.py`, `chap5.py`.
- 5.5 rows are now Compression / Tension / Slenderness, since the values are axial. Rolled / welded types still show "design to be added".

## Known issues outside the report scope (not changed)
1. Zero skew: `Vz_i` is exactly 0 for every interior start and end edge element in all load cases (0 deg runs: 7, 5, 4 and 3 girders), so the end diaphragm design returns no members and the report shows N/A. This looks like an analysis bug. 10 deg skew gives results.
2. Any skew: with 5, 10 and -10 deg the deflection and load-case summaries are empty and `per_girder` holds one girder. `build_girders` (`analysis_results.py`) selects edge nodes by `x == min_x`, which fails on a skewed edge. Chapter 4 and the deflection tables are therefore incomplete in the 10 deg reports; the `_skew0` pair is complete there.
3. Vehicles: the analysis places Class A and 70R from IRC 6 Table 6A and does not use the UI check boxes. Chapter 3 has one row per vehicle selected in the Loading tab; a selected vehicle with no load case in the results reads "Not analysed" with a footnote, and a vehicle analysed but not selected is named in the note.
4. `IRC6_2017.cl_211_2_braking_force` raises `UnboundLocalError` for every lane count tried (1 to 4).
5. Cross bracing 5.5 demand is capacity x UR, and Osdag's compression UR differs from demand / capacity (5.656 / 16.28 = 0.35 vs 0.52). Left as found; end diaphragm rows print the analysed force and Osdag's UR.
6. Girder dimensions in Table 2.7 are metres labelled mm.

## N/A values
- Braking value and eccentricity, centrifugal load: not in the analysis (Considered = No).
- End diaphragm steel tonnage: not computed by `boq_generator.py`.
- End diaphragm forces, capacity and UR at 0 deg skew.

## Interpretations and other changes
- The generator used no PyLaTeX. Chapters build LaTeX strings, so `make_longtable` returns a string and `apply_document_styles` appends to a list; figures use PyLaTeX `Figure`.
- Table rows keep `\multirow` groups on one page.
- Chapter 3 analysed vehicles are read from the `CaseN` load case names in `design_results["per_girder"][G]["per_lc"]`. Total load is the IRC 6 axle sum for that vehicle; the impact factor is recomputed with the Cl. 208.3 function the analysis uses, as the results do not store it.
- Chapter 3 columns follow the spec's example, so the earlier axle load and centrifugal columns were dropped; the note says braking and centrifugal loads are not analysed. The UI eccentricity (1.2 m) is not printed because no braking load is applied.
- Chapter 3 tests: UI selections all 8, Class A + SV, 70R Wheeled only, and none (`--vehicles`). They change the reported selection only and reuse the stored design.
- Removed a permanently blank "Reactions at Supports" table in Chapter 4; reactions are in Table 4.1.
- Concrete vs reinforcement uses two panels (allowed by the task).
- Deck "Transverse Shear" has no value in the sample, so it has no bar.

## LaTeX status
- 0 errors, 0 overfull boxes above 10 pt (the baseline .tex gave 140 error lines). One duplicate label warning (`sec:assumptions`), from the original text.

## Polish
Bold filled headers, consistent captions, coloured PASS / FAIL, black footer text, colour-blind-checked pass / fail colours with hatching for FAIL, Latin Modern T1. Zebra rows are implemented but off: fills hid rules in the PDF render. `siunitx` is not used.

## macOS install
`osdag` 2026.04.0.0 needs `osdag_latex_env`, published only for Linux and Windows. Without a pin, conda silently installs 2025.01.a.2, which this code cannot use.
1. Use only osdag, geompy and conda-forge (`--override-channels`); install osdag's other dependencies, plus poppler.
2. `conda install` the exact `osdag-2026.04.0.0-py_0.conda` URL with its md5 (the solver ignored `--no-deps`). It is pinned in `conda-meta/pinned`.
3. `pip install "openseespy>=3.2.2.6" opsvis -e .`
4. Import `osdag_gui.__main__` once, so osdag builds its own database.
5. BasicTeX: `tlmgr install enumitem multirow titlesec lastpage makecell`.
No package was stubbed or substituted; osdag itself handles the missing import.
