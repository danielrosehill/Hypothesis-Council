import json
import subprocess
from pathlib import Path


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _typst(hypothesis: str, pack: list[dict], verdicts: list[dict], synthesis: dict) -> str:
    lines: list[str] = []
    lines.append('#set page(margin: 2cm)')
    lines.append('#set text(font: "IBM Plex Sans", size: 10pt)')
    lines.append('#set heading(numbering: "1.")')
    lines.append('')
    lines.append('#align(center)[#text(size: 18pt, weight: "bold")[Hypothesis Council Report]]')
    lines.append('')
    lines.append('= Hypothesis')
    lines.append('')
    lines.append(f'#quote(block: true)[{hypothesis}]')
    lines.append('')
    lines.append('= Headline')
    lines.append('')
    lines.append(f'*{synthesis.get("headline", "(no headline)")}*')
    lines.append('')
    cs = synthesis.get("consensus_score")
    sr = synthesis.get("score_range", [None, None])
    lines.append(f'- Consensus score: *{cs}* (range {sr[0]}–{sr[1]})')
    lines.append('')
    lines.append('= Council verdicts')
    lines.append('')
    lines.append('#table(columns: (auto, auto, auto, 1fr),')
    lines.append('  [*Member*], [*Score*], [*Band*], [*One-line verdict*],')
    for v in verdicts:
        if "_error" in v:
            lines.append(
                f'  [{v["_member"]}], [ERR], [--], [{_escape(v["_error"][:80])}],'
            )
            continue
        lines.append(
            f'  [{v["_member"]}], [{v.get("score", "?")}], '
            f'[{v.get("confidence_band", "?")}], '
            f'[{_escape(v.get("one_line_verdict", ""))}],'
        )
    lines.append(')')
    lines.append('')
    lines.append('= Divergence analysis')
    lines.append('')
    lines.append(synthesis.get("divergence_analysis", ""))
    lines.append('')
    lines.append('= Strongest counterarguments (ranked)')
    lines.append('')
    for i, c in enumerate(synthesis.get("strongest_counterarguments_ranked", []), 1):
        raised = ", ".join(c.get("raised_by", []))
        lines.append(f'{i}. *[{c.get("severity", "?")}]* {c.get("point", "")} _(raised by: {raised})_')
    lines.append('')
    lines.append('= Shared load-bearing assumptions')
    lines.append('')
    for a in synthesis.get("shared_load_bearing_assumptions", []):
        lines.append(f'- {a}')
    lines.append('')
    lines.append('= Open questions')
    lines.append('')
    for q in synthesis.get("what_the_council_wants_to_know", []):
        lines.append(f'- {q}')
    lines.append('')
    lines.append('= Calibration note')
    lines.append('')
    lines.append(synthesis.get("calibration_note", ""))
    lines.append('')
    lines.append('#pagebreak()')
    lines.append('= Per-member detail')
    for v in verdicts:
        lines.append('')
        lines.append(f'== {v["_member"]} (`{v["_model"]}`)')
        if "_error" in v:
            lines.append(f'Error: {v["_error"]}')
            continue
        lines.append('')
        lines.append(f'Score: *{v.get("score")}*  Band: {v.get("confidence_band")}')
        lines.append('')
        lines.append('*Counterarguments*')
        for c in v.get("counterarguments", []):
            lines.append(f'- {c}')
        lines.append('')
        lines.append('*Load-bearing assumptions*')
        for a in v.get("load_bearing_assumptions", []):
            lines.append(f'- {a}')
        lines.append('')
        shift = v.get("evidence_that_would_shift_me", {})
        lines.append('*Evidence that would shift this member*')
        lines.append('')
        lines.append('Upward:')
        for e in shift.get("upward", []):
            lines.append(f'- {e}')
        lines.append('')
        lines.append('Downward:')
        for e in shift.get("downward", []):
            lines.append(f'- {e}')
    lines.append('')
    lines.append('#pagebreak()')
    lines.append('= Grounding pack')
    for p in pack:
        lines.append('')
        lines.append(f'[{p["n"]}] *{_escape(p["title"])}*')
        lines.append('')
        lines.append(f'#link("{p["url"]}")')
        lines.append('')
        lines.append(p["snippet"][:600].replace("\n", " "))
    return "\n".join(lines)


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
