"""Report bar charts (matplotlib, file output only). Appearance: styles.FIGURE."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg", force=False)
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure as MplFigure
from pylatex import Figure, NoEscape

from osdagbridge.core.reports.styles import FIGURE


def _new_figure(ncols=1):
    # Figure objects are built directly: the report runs on a GUI worker
    # thread, where pyplot's global state must not be touched.
    fig = MplFigure(figsize=FIGURE["size"], dpi=FIGURE["dpi"], layout="constrained")
    FigureCanvasAgg(fig)
    return fig, [fig.add_subplot(1, ncols, i + 1) for i in range(ncols)]


def _save(fig, path):
    fig.savefig(path)
    return Path(path).as_posix()


def _bars(ax, labels, values, color, fmt, hatches=None):
    bars = ax.bar(range(len(values)), values, width=0.55, color=color)
    for bar, value, hatch in zip(bars, values, hatches or [None] * len(values)):
        if hatch:
            bar.set_hatch(hatch)
        ax.annotate(fmt.format(value), (bar.get_x() + bar.get_width() / 2, value),
                    ha="center", va="bottom", xytext=(0, 2), textcoords="offset points", zorder=5,
                    bbox={"boxstyle": "square,pad=0.1", "fc": FIGURE["label_bg"], "ec": "none"})
    ax.set_xticks(range(len(values)), labels)
    ax.set_xlim(-0.6, len(values) - 0.4)


def plot_ur(element_name, labels, urs, path, failed=None):
    """Utilization ratio bars against the UR = 1.0 limit; failing bars are hatched."""
    failed = failed or [u > 1.0 for u in urs]
    with matplotlib.rc_context(FIGURE["rc"]):
        fig, (ax,) = _new_figure()
        _bars(ax, labels, urs,
              [FIGURE["bar_fail"] if f else FIGURE["bar_pass"] for f in failed],
              "{:.2f}", ["//" if f else None for f in failed])
        ax.axhline(1.0, color=FIGURE["threshold"], linestyle="--", linewidth=1.4)
        ax.annotate("UR = 1.0", (1, 1.0), xycoords=("axes fraction", "data"), va="center",
                    xytext=(4, 0), textcoords="offset points", color=FIGURE["threshold"])
        ax.set_ylim(0, max(1.2, max(urs) * 1.1))
        ax.set_ylabel("Utilization Ratio")
        ax.set_title(element_name)
        return _save(fig, path)


def plot_steel_tonnage(labels, tonnes, path):
    """Structural steel weight by component; a None value is marked N/A."""
    with matplotlib.rc_context(FIGURE["rc"]):
        fig, (ax,) = _new_figure()
        _bars(ax, labels, [t or 0.0 for t in tonnes], FIGURE["bar_steel"], "{:.2f}")
        for i, t in enumerate(tonnes):
            if t is None:
                ax.texts[i].set_text("N/A")
        ax.set_ylim(0, (max([t or 0.0 for t in tonnes]) or 1.0) * 1.15)
        ax.set_ylabel("Weight (t)")
        ax.set_title("Structural Steel")
        return _save(fig, path)


def plot_concrete_vs_rebar(concrete_m3, rebar_mt, path):
    """Side-by-side panels, because the units differ."""
    with matplotlib.rc_context(FIGURE["rc"]):
        fig, axes = _new_figure(2)
        for ax, value, label, unit, color in (
                (axes[0], concrete_m3, "Deck concrete", "Volume (m³)", FIGURE["bar_concrete"]),
                (axes[1], rebar_mt, "Reinforcement steel", "Weight (MT)", FIGURE["bar_rebar"])):
            _bars(ax, [label], [value or 0.0], color, "{:.2f}")
            if value is None:
                ax.texts[0].set_text("N/A")
            ax.set_ylim(0, (value or 1.0) * 1.15)
            ax.set_ylabel(unit)
        return _save(fig, path)


def figure_latex(path, caption, label=None):
    fig = Figure(position="H")
    fig.append(NoEscape(r"\centering"))
    fig.add_image(path, width=NoEscape(FIGURE["chart_width"]), placement=None)
    fig.add_caption(NoEscape(caption))
    if label:
        fig.append(NoEscape(r"\label{%s}" % label))
    return fig.dumps() + "\n"
