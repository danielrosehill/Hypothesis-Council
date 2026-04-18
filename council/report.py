import json
import subprocess
from pathlib import Path


def _esc(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\\", "\\\\")
    for ch in ("*", "_", "#", "<", ">", "@", "$"):
        s = s.replace(ch, f"\\{ch}")
    return s


def _fmt(v, nd: int = 2) -> str:
    try:
        return f"{float(v):.{nd}f}"
    except (TypeError, ValueError):
        return "?"


def _typst(hypothesis: str, pack: list[dict], verdicts: list[dict], synthesis: dict) -> str:
    L: list[str] = []
    L += [
        '#set page(margin: 2cm)',
        '#set text(font: "IBM Plex Sans", size: 10pt)',
        '#set heading(numbering: "1.")',
        '',
        '#align(center)[#text(size: 18pt, weight: "bold")[Hypothesis Council Report]]',
        '',
        '= Hypothesis',
        '',
        f'#quote(block: true)[{_esc(hypothesis)}]',
        '',
        '= Headline',
        '',
        f'*{_esc(synthesis.get("headline", ""))}*',
        '',
    ]

    ms = synthesis.get("mean_scores", {})
    rg = synthesis.get("score_ranges", {})
    L += [
        '= Council scores',
        '',
        '#table(columns: (auto, auto, auto),',
        '  [*Axis*], [*Mean*], [*Range*],',
        f'  [Conspiratorial], [{_fmt(ms.get("conspiratorial"))}], '
        f'[{_fmt((rg.get("conspiratorial") or [None,None])[0])}–'
        f'{_fmt((rg.get("conspiratorial") or [None,None])[1])}],',
        f'  [Credible], [{_fmt(ms.get("credible"))}], '
        f'[{_fmt((rg.get("credible") or [None,None])[0])}–'
        f'{_fmt((rg.get("credible") or [None,None])[1])}],',
        f'  [Likely], [{_fmt(ms.get("likely"))}], '
        f'[{_fmt((rg.get("likely") or [None,None])[0])}–'
        f'{_fmt((rg.get("likely") or [None,None])[1])}],',
        ')',
        '',
        '= Per-member scores',
        '',
        '#table(columns: (auto, auto, auto, auto),',
        '  [*Member*], [*Conspiratorial*], [*Credible*], [*Likely*],',
    ]
    for v in verdicts:
        if "_error" in v:
            L.append(f'  [{v["_member"]}], [ERR], [ERR], [ERR],')
            continue
        s = v.get("scores", {})
        L.append(
            f'  [{v["_member"]}], [{_fmt(s.get("conspiratorial"))}], '
            f'[{_fmt(s.get("credible"))}], [{_fmt(s.get("likely"))}],'
        )
    L += [')', '']

    L += [
        '= Council verdict',
        '',
        _esc(synthesis.get("council_verdict", "")),
        '',
        '= Alternative readings',
        '',
        _esc(synthesis.get("alternative_reads_comparison", "")),
        '',
        '= Divergence analysis',
        '',
        _esc(synthesis.get("divergence_analysis", "")),
        '',
        '= Strongest supporting evidence',
        '',
    ]
    for e in synthesis.get("strongest_supporting_evidence", []):
        raised = ", ".join(e.get("raised_by", []))
        L.append(f'- {_esc(e.get("point", ""))} _(raised by: {raised})_')
    L += ['', '= Strongest refuting evidence', '']
    for e in synthesis.get("strongest_refuting_evidence", []):
        raised = ", ".join(e.get("raised_by", []))
        L.append(f'- {_esc(e.get("point", ""))} _(raised by: {raised})_')

    L += ['', '= Shared load-bearing assumptions', '']
    for a in synthesis.get("shared_load_bearing_assumptions", []):
        L.append(f'- {_esc(a)}')
    L += ['', '= Open questions', '']
    for q in synthesis.get("open_questions", []):
        L.append(f'- {_esc(q)}')
    L += ['', '= Calibration note', '', _esc(synthesis.get("calibration_note", ""))]

    L += ['', '#pagebreak()', '= Per-member detail']
    for v in verdicts:
        L += ['', f'== {_esc(v["_member"])} (`{v["_model"]}`)']
        if "_error" in v:
            L.append(f'Error: {_esc(v["_error"])}')
            continue
        s = v.get("scores", {})
        L += [
            '',
            f'Conspiratorial: *{_fmt(s.get("conspiratorial"))}*  '
            f'Credible: *{_fmt(s.get("credible"))}*  '
            f'Likely: *{_fmt(s.get("likely"))}*',
            '',
            '*Overall judgement*',
            '',
            _esc(v.get("overall_judgement", "")),
            '',
            '*Alternative read*',
            '',
            _esc(v.get("alternative_read", "")),
            '',
            '*Supporting evidence*',
        ]
        for e in v.get("supporting_evidence", []):
            L.append(f'- {_esc(e)}')
        L += ['', '*Refuting evidence*']
        for e in v.get("refuting_evidence", []):
            L.append(f'- {_esc(e)}')
        L += ['', '*Load-bearing assumptions*']
        for a in v.get("load_bearing_assumptions", []):
            L.append(f'- {_esc(a)}')
        shift = v.get("what_would_shift_me", {})
        L += ['', '*What would shift this member*', '', 'Toward likely:']
        for e in shift.get("toward_likely", []):
            L.append(f'- {_esc(e)}')
        L += ['', 'Away from likely:']
        for e in shift.get("away_from_likely", []):
            L.append(f'- {_esc(e)}')
        if v.get("grounding_notes"):
            L += ['', f'_Grounding notes: {_esc(v["grounding_notes"])}_']

    L += ['', '#pagebreak()', '= Grounding pack']
    for p in pack:
        L += ['', f'[{p["n"]}] *{_esc(p["title"])}*']
        if p.get("url"):
            L += ['', f'#link("{p["url"]}")']
        if p.get("snippet"):
            L += ['', _esc(p["snippet"][:600].replace("\n", " "))]

    return "\n".join(L)


def write_report(
    out_dir: Path,
    hypothesis: str,
    pack: list[dict],
    verdicts: list[dict],
    synthesis: dict,
) -> Path:
    (out_dir / "raw.json").write_text(
        json.dumps(
            {"hypothesis": hypothesis, "pack": pack, "verdicts": verdicts, "synthesis": synthesis},
            indent=2,
        )
    )
    typ = out_dir / "report.typ"
    typ.write_text(_typst(hypothesis, pack, verdicts, synthesis))
    pdf = out_dir / "report.pdf"
    try:
        subprocess.run(["typst", "compile", str(typ), str(pdf)], check=True)
        return pdf
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[warn] typst compile failed ({e}); leaving .typ only")
        return typ
