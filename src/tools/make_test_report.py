"""Headless report harness: design a sample bridge, then compile the report.

    python src/tools/make_test_report.py [--stem NAME] [--carriageway M] [--out DIR] [--skew DEG] [--fresh]

Mirrors the GUI path (defaults -> set_input -> design -> generate_design_report).
The design result is cached as a pickle in the output directory; --fresh reruns
it. CAD figures need a Qt viewer, so Chapter 6 shows placeholders.
"""
import argparse
import os
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sample_inputs(skew=10):
    from osdagbridge.core.bridge_types.plate_girder.defaults import (
        BASIC_INPUT_DICT, solve_extend_basic_input_dict)
    from osdagbridge.core.utils import common as c
    inp = dict(BASIC_INPUT_DICT)
    inp.update({
        c.KEY_PROJECT_LOCATION: {
            "method": "custom_data", "data": {},
            "weather_data": {"zone": "III", "wind_speed": 44,
                             "max_temp": 45, "min_temp": 5}},
        c.KEY_SPAN: 30, c.KEY_CARRIAGEWAY_WIDTH: 10.5,
        c.KEY_FOOTPATH: "Both Sides",
        # 0 deg skew gives no end diaphragm forces (see NOTES.md)
        c.KEY_SKEW_ANGLE: skew,
    })
    prime_materials(inp)
    solve_extend_basic_input_dict(inp)
    return inp


def prime_materials(inp):
    """Material properties exactly as InputDock._prime_material_inputs sets them."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from osdagbridge.core.utils import common as c
    from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog
    app = QApplication.instance() or QApplication([])
    for key in (c.KEY_GIRDER, c.KEY_CROSS_BRACING, c.KEY_END_DIAPHRAGM,
                c.KEY_DECK_CONCRETE_GRADE_BASIC):
        dlg = MaterialPropertiesDialog(read_only=True, selected_material=inp[key], member=key)
        inp.update(dlg.get_export_fields())
    return app


def run_design(skew=10):
    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
    bridge = PlateGirderBridge()
    bridge.set_input(sample_inputs(skew))
    bridge.design()
    return {"input": dict(bridge.input_dict), "output": dict(bridge.output_dict),
            "lc": getattr(bridge, "_lc_summary", None),
            "rxn": getattr(bridge, "_reaction_summary", None)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default="Report")
    ap.add_argument("--out", default=str(ROOT / "reports_out"))
    ap.add_argument("--carriageway", type=float)
    ap.add_argument("--skew", type=float, default=10)
    ap.add_argument("--fresh", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = out / f"report_input_skew{args.skew:g}.pkl"
    if args.fresh or not cache.exists():
        cache.write_bytes(pickle.dumps(run_design(args.skew)))
    data = pickle.loads(cache.read_bytes())

    from osdagbridge.core.bridge_types.plate_girder.plategirderbridge import PlateGirderBridge
    from osdagbridge.core.reports import ReportMetadata, ReportOptions, ReportRequest
    from osdagbridge.core.utils import common as c
    if args.carriageway:  # exercise Table 6A vehicle listing without a redesign
        data["input"][c.KEY_CARRIAGEWAY_WIDTH] = args.carriageway
    bridge = PlateGirderBridge()
    bridge.input_dict, bridge.output_dict = data["input"], data["output"]
    bridge._lc_summary, bridge._reaction_summary = data["lc"], data["rxn"]
    meta = ReportMetadata(
        project_name="Sample Bridge", project_location="", designer="Designer",
        client="Client", company="Organization", subtitle="Rev 0",
        job_number="JOB-001", report_date="2026-01-01", reviewer="Reviewer")
    secs = ["exec_summary", "project_info", "input_parameters", "loads", "analysis",
            "design_checks", "drawings", "quantities", "standards",
            "design_log_window", "references"]
    result = bridge.generate_design_report(
        ReportRequest(meta, ReportOptions(secs, True, True, True), str(out), args.stem), {})
    print("PDF:", result.pdf_path)
    return 0 if result.pdf_path else 1


if __name__ == "__main__":
    code = main()
    sys.stdout.flush()
    os._exit(code)  # skip Qt/OpenSees teardown, which can crash
