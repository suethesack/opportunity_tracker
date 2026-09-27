"""
Turns a list of AI-scored opportunities into a dated Markdown report,
sorted so the most relevant postings appear first.
"""

from datetime import date
from pathlib import Path

from ai_evaluator import Evaluation
from config import REPORTS_DIR


def write_report(evaluations: list[Evaluation], min_score: int = 5) -> Path:
    ensure_reports_dir_exists = REPORTS_DIR
    ensure_reports_dir_exists.mkdir(exist_ok=True)

    today = date.today().isoformat()
    report_path = REPORTS_DIR / f"{today}.md"

    relevant = [e for e in evaluations if e.relevant and e.score >= min_score]
    relevant.sort(key=lambda e: e.score, reverse=True)

    lines = [f"# EEE Opportunity Digest — {today}", ""]

    if not relevant:
        lines.append("No new opportunities cleared the relevance bar today.")
    else:
        lines.append(f"{len(relevant)} new opportunit{'y' if len(relevant) == 1 else 'ies'} found:\n")
        for e in relevant:
            lines.append(f"## {e.opportunity.title}  (score: {e.score}/10)")
            lines.append(f"- Source: {e.opportunity.source}")
            lines.append(f"- Link: {e.opportunity.link}")
            lines.append(f"- Why it matters: {e.reason}")
            lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
