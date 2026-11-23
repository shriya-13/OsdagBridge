"""Single source of truth for report layout and appearance.

Chapter files must not hardcode margins, fonts, colours, padding or table
styles: they take them from here. Column specs are given as "C2.5 L8 C5"
(alignment + relative weight) and always scale to the text width.
"""
import math
import re

PAGE = {
    "paper": "a4paper", "base_size": "12pt",
    "top": "15mm", "bottom": "14mm", "left": "25.4mm", "right": "25.4mm",
    # Two footer lines (software-default note + page number) fit in footskip.
    "headheight": "16pt", "headsep": "14pt", "footskip": "40pt",
    "includeheadfoot": True,
    # Space to reserve, in baselineskips: before a heading; caption + header +
    # foot of a table; each row of its first unbreakable group; upper cap.
    "section_needspace": 20, "table_needspace": 8, "row_needspace": 1.75,
    "wrap_needspace": 1.1, "chars_per_line": 80, "max_needspace": 34,
}

FONTS = {
    "packages": [r"\usepackage[T1]{fontenc}", r"\usepackage{lmodern}"],
    "chapter": r"\normalfont\Large\bfseries\centering",
    "line_stretch": "1.15",
    "table": r"\small", "table_dense": r"\footnotesize", "footer": r"\footnotesize",
    "title": r"\Huge", "subtitle": r"\large", "heading": r"\Large",
}

COLORS = {
    "osdagGreen": "#91B014", "osdagHeader": "#E6EFC8", "osdagAltRow": "#F7F9EF",
    "osdagPass": "#00897B", "osdagFail": "#B71C1C", "osdagGrid": "#9E9E9E",
    "osdagInfo": "#1565C0",
}

TABLE = {
    "arraystretch": "1.35", "tabcolsep": "4pt", "extrarowheight": "1pt",
    "rule": "0.6pt", "pre": "8pt", "post": "10pt", "zebra": False,
    "continued": "continued", "continues": "Continued on next page",
}

HEADER_FOOTER = {
    "left": r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay",
    "right": r"Page \thepage\ of \pageref{LastPage}",
    "default_note": r"* Software default value",
    "rule": "1pt",
}

FIGURE = {
    "width": r"0.85\textwidth", "embed_width": r"0.75\textwidth",
    "full_width": r"0.97\textwidth", "cell_width": r"0.31\textwidth",
    "placeholder_width": r"0.9\textwidth", "chart_width": r"0.85\textwidth",
    "dpi": 200, "size": (7.0, 2.9),
    "rc": {"font.family": "serif", "font.size": 9, "axes.grid": True,
           "axes.grid.axis": "y", "axes.axisbelow": True,
           "grid.color": COLORS["osdagGrid"], "grid.alpha": 0.35,
           "axes.spines.top": False, "axes.spines.right": False},
    "bar_pass": COLORS["osdagPass"], "bar_fail": COLORS["osdagFail"],
    "bar_steel": COLORS["osdagGreen"], "bar_concrete": COLORS["osdagGrid"],
    "bar_rebar": COLORS["osdagInfo"], "threshold": "red", "label_bg": "white",
}


def define_colors():
    return "\n".join(r"\definecolor{%s}{HTML}{%s}" % (n, h.lstrip("#"))
                     for n, h in COLORS.items())


def _page_style(name, header):
    return (r"\fancypagestyle{" + name + "}{\n\\fancyhf{}\n" + header
            + r"\fancyfoot[L]{" + HEADER_FOOTER["left"]
            + r"\ifbool{hasSDonPage}{\\{" + FONTS["footer"] + r"\textit{"
            + HEADER_FOOTER["default_note"] + "}}}{}}\n"
            + r"\fancyfoot[R]{" + HEADER_FOOTER["right"] + "}\n"
            + r"\renewcommand{\headrule}{{\color{osdagGreen}\hrule width\headwidth height "
            + (HEADER_FOOTER["rule"] if header else "0pt") + "}}\n"
            + r"\renewcommand{\footrule}{{\color{osdagGreen}\hrule width\headwidth height "
            + HEADER_FOOTER["rule"] + "}\\vskip 4pt}\n}\n")


def apply_document_styles(doc, head_left="", head_right=""):
    """Append the full preamble (class, packages, styles) to ``doc``, a list of
    LaTeX strings. Packages missing from a chapter belong here."""
    header = r"\fancyhead[L]{%s}" % head_left + "\n" + r"\fancyhead[R]{%s}" % head_right + "\n"
    geometry = ",".join([PAGE["paper"]] + ["%s=%s" % (k, PAGE[k]) for k in (
        "top", "bottom", "left", "right", "headheight", "headsep", "footskip")]
        + (["includeheadfoot"] if PAGE["includeheadfoot"] else []))
    packages = "\n".join(r"\usepackage{%s}" % p for p in (
        "graphicx", "amsmath", "amssymb", "booktabs", "array", "float", "fancyhdr",
        "setspace", "enumitem", "caption", "subcaption", "multirow", "longtable",
        "titlesec", "titletoc", "lastpage", "makecell", "etoolbox", "needspace"))
    doc.append(
        r"\documentclass[%s,%s]{report}" % (PAGE["base_size"], PAGE["paper"]) + "\n"
        + r"\usepackage[%s]{geometry}" % geometry + "\n"
        + "\n".join(FONTS["packages"]) + "\n" + r"\usepackage[table]{xcolor}" + "\n"
        + packages + "\n" + r"\usepackage[hidelinks]{hyperref}" + "\n"
        + define_colors() + r"""
\DeclareUnicodeCharacter{2264}{\ensuremath{\leq}}
\DeclareUnicodeCharacter{2265}{\ensuremath{\geq}}
\DeclareUnicodeCharacter{03B3}{\ensuremath{\gamma}}
\DeclareUnicodeCharacter{03C3}{\ensuremath{\sigma}}
\DeclareUnicodeCharacter{03C4}{\ensuremath{\tau}}
\DeclareUnicodeCharacter{0394}{\ensuremath{\Delta}}
\DeclareUnicodeCharacter{03B4}{\ensuremath{\delta}}
\captionsetup{labelfont=bf,justification=raggedright,singlelinecheck=false,format=plain}
\captionsetup[table]{skip=4pt}
\numberwithin{table}{chapter}
\numberwithin{figure}{chapter}
\setlength{\LTleft}{0pt}
\setlength{\LTright}{0pt plus 1fill}
""" + r"\setlength{\LTpre}{%s}\setlength{\LTpost}{%s}" % (TABLE["pre"], TABLE["post"]) + "\n"
        + r"\setlength{\tabcolsep}{%s}" % TABLE["tabcolsep"] + "\n"
        + r"\renewcommand{\arraystretch}{%s}" % TABLE["arraystretch"] + "\n"
        + r"\setlength{\arrayrulewidth}{%s}" % TABLE["rule"] + "\n"
        + r"\setlength{\extrarowheight}{%s}" % TABLE["extrarowheight"] + "\n"
        + r"\setlength{\emergencystretch}{3em}" + "\n"
        + r"\AddToHook{cmd/section/before}{\Needspace{%d\baselineskip}}" % PAGE["section_needspace"] + "\n"
        + r"""
% No page break at a \cline, so multi-row groups stay together.
\makeatletter
\patchcmd{\@cline}{\vskip-\arrayrulewidth}{\nobreak\vskip-\arrayrulewidth}{}{\typeout{cline patch failed}}
\makeatother
\newbool{hasSDonPage}
\newcommand{\markSD}{\global\booltrue{hasSDonPage}}
\newcommand{\sdstar}{\textsuperscript{*}\markSD{}}
\AddToHook{shipout/after}{\global\boolfalse{hasSDonPage}}
""" + _page_style("main", header) + _page_style("plain", header) + _page_style("firstpage", "")
        + r"\pagestyle{main}" + "\n" + r"\setstretch{%s}" % FONTS["line_stretch"]
        + r"""
\newcommand{\placeholder}[1]{\textit{\textless #1\textgreater}}
\newcommand{\statuspass}[1]{\textcolor{osdagPass}{\textbf{#1}}}
\newcommand{\statusfail}[1]{\textcolor{osdagFail}{\textbf{#1}}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
\begin{document}
""")
    return doc


def chapter_format():
    """Chapter headings, reissued after the executive summary."""
    return (r"\titleformat{\chapter}[block]{%s}{\thechapter}{1em}{}" % FONTS["chapter"]
            + "\n" + r"\titlespacing*{\chapter}{0pt}{0pt}{10pt}" + "\n")


def col_spec(spec):
    """'C2.5 L8 C5' -> ruled longtable columns that exactly fill the text width."""
    cols = [(c[0], float(c[1:])) for c in spec.split()]
    total, n = sum(w for _, w in cols), len(cols)
    avail = r"\dimexpr\linewidth-%d\tabcolsep-%d\arrayrulewidth\relax" % (2 * n, n + 1)
    return "|" + "|".join("%s{%.5f%s}" % (a, w / total, avail) for a, w in cols) + "|"


def _color_status(body):
    body = re.sub(r"(?<=& )PASS(?=\s*\\\\)", lambda m: r"\statuspass{PASS}", body)
    return re.sub(r"(?<=& )FAIL(?=\s*\\\\)", lambda m: r"\statusfail{FAIL}", body)


def _first_group_lines(body, spec):
    """Estimated height, in baselines, of the first unbreakable row group."""
    weights = [float(c[1:]) for c in spec.split()]
    height = 0.0
    for row in body.split(r"\hline")[0].split(r"\\"):
        if not re.sub(r"\*|\\cline\{[^}]*\}|\s", "", row):
            continue
        wraps = 1
        for w, cell in zip(weights, re.split(r"(?<!\\)&", row)):
            plain = re.sub(r"\\[A-Za-z]+\*?|[{}$]", "", cell).strip()
            chars = max(1.0, PAGE["chars_per_line"] * w / sum(weights))
            wraps = max(wraps, math.ceil(len(plain) / chars))
        height += PAGE["row_needspace"] + PAGE["wrap_needspace"] * (wraps - 1)
    return height


def make_longtable(headers, rows, spec, units=None, caption=None, *, numbered=True,
                   head=None, font="table", zebra=None, label=None):
    """The one table helper: a longtable whose header repeats on every page.

    headers  column titles (LaTeX), or None for a table without a header row
    rows     list of cell lists, or a ready LaTeX body (rows ending in \\\\ + \\hline)
    spec     column spec string, see col_spec()
    units    optional per-column units, shown under the titles
    head     raw header rows, for multi-level headers (overrides headers)
    """
    n = len(spec.split())
    if not isinstance(rows, str):
        rows = "\n".join(" & ".join(map(str, r)) + r" \\" + "\n" + r"\hline" for r in rows)
    body = re.sub(r"\\\\\[\d+pt\]", lambda m: r"\\", rows).strip()
    body = re.sub(r"\\cline\{[^}]*\}\s*(?=\\hline)", "", body)
    # Keep \multirow groups on one page.
    body = re.sub(r"\\\\\s*(?=\\cline)", lambda m: "\\\\*\n", body)
    body = _color_status(body)
    if not body.endswith(r"\hline"):
        body += "\n\\hline"
    if zebra is None:
        zebra = TABLE["zebra"] and r"\multirow" not in body
    if head is None and headers:
        cells = [r"\textbf{%s}" % h if h else "" for h in headers]
        if units:
            cells = [c + (" (%s)" % u if u else "") for c, u in zip(cells, units)]
        head = r"\rowcolor{osdagHeader} " + " & ".join(cells) + r" \\"
    head_rows = (r"\hline" + "\n" + head + "\n" + r"\hline" + "\n") if head else r"\hline" + "\n"
    first = cont = ""
    if caption:
        first = (r"\caption" + ("" if numbered else "*") + r"{\textbf{%s}}" % caption
                 + (r"\label{%s}" % label if label else "") + r"\\" + "\n")
        name = (r"\tablename\ \thetable{} -- " if numbered else "")
        cont = r"\multicolumn{%d}{@{}l}{\textit{%s%s}}\\" % (n, name, TABLE["continued"]) + "\n"
    # Reserve room for caption + header + first group, so the table never
    # starts with an orphaned "continued" header.
    need = min(PAGE["max_needspace"], PAGE["table_needspace"] + _first_group_lines(body, spec))
    lines = [r"\par\begingroup" + FONTS[font], r"\Needspace{%.1f\baselineskip}" % need]
    if zebra:
        lines.append(r"\rowcolors{1}{}{osdagAltRow}")
    lines += [r"\begin{longtable}{%s}" % col_spec(spec),
              first + head_rows + r"\endfirsthead",
              cont + head_rows + r"\endhead",
              r"\multicolumn{%d}{r@{}}{\textit{%s}}\\" % (n, TABLE["continues"]),
              r"\endfoot", r"\endlastfoot", body, r"\end{longtable}", r"\endgroup"]
    return "\n" + "\n".join(lines) + "\n"


def note(text):
    return r"\noindent\textit{%s}" % text + "\n"
