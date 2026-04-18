from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from .config import COUNCIL, SYNTHESISER, Member
from .grounding import format_pack, ground
from .openrouter import call_json
from .report import write_report

ROOT = Path(__file__).resolve().parent.parent
MEMBER_PROMPT = (ROOT / "prompts/member.md").read_text()
SYNTH_PROMPT = (ROOT / "prompts/synthesiser.md").read_text()


def _member_user_msg(hypothesis: str, pack_str: str) -> str:
    return f"# Hypothesis\n\n{hypothesis}\n\n# Grounding pack\n\n{pack_str}"


def _verdict(member: Member, hypothesis: str, pack_str: str) -> dict:
    try:
        out = call_json(member.model, MEMBER_PROMPT, _member_user_msg(hypothesis, pack_str))
        out["_member"] = member.name
        out["_model"] = member.model
        return out
    except Exception as e:
        return {"_member": member.name, "_model": member.model, "_error": str(e)}


def run_council(hypothesis: str) -> Path:
    print(f"[grounding] searching Tavily for context…")
    pack = ground(hypothesis)
    pack_str = format_pack(pack)
    print(f"[grounding] {len(pack)} results")

    print(f"[council] polling {len(COUNCIL)} members in parallel…")
    with ThreadPoolExecutor(max_workers=len(COUNCIL)) as ex:
        verdicts = list(ex.map(lambda m: _verdict(m, hypothesis, pack_str), COUNCIL))

    for v in verdicts:
        if "_error" in v:
            print(f"  ! {v['_member']}: {v['_error']}")
        else:
            print(f"  - {v['_member']}: {v.get('score')} ({v.get('confidence_band', '')})")

    print("[synthesis] merging verdicts…")
    synth_user = (
        f"# Hypothesis\n\n{hypothesis}\n\n"
        f"# Grounding pack\n\n{pack_str}\n\n"
        f"# Member verdicts\n\n{verdicts}"
    )
    synthesis = call_json(SYNTHESISER.model, SYNTH_PROMPT, synth_user)

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "reports" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = write_report(out_dir, hypothesis, pack, verdicts, synthesis)
    print(f"[done] {report_path}")
    return report_path
