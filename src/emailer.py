"""Render and send the daily digest via Gmail SMTP."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

NO_MATCHES_TEXT = "No new matching jobs today."


def _job_text_block(job: dict) -> str:
    sources = job.get("sources") or []
    primary = sources[0] if sources else {}
    extra = f" (+{len(sources) - 1} more source(s))" if len(sources) > 1 else ""
    exp = f"{job.get('required_years')}+ yrs" if job.get("required_years") else "not specified"
    location = "Remote" if job.get("remote") else (job.get("location") or "Unspecified")
    return (
        f"{job.get('title')} — {job.get('company')}\n"
        f"Location: {location}\n"
        f"Posted: {job.get('posted_at') or 'unknown'}\n"
        f"Experience: {exp}\n"
        f"Match reasons: {'; '.join(job.get('match_reasons') or [])}\n"
        f"Apply: {primary.get('application_url', '')}\n"
        f"Original post: {primary.get('original_url', '')}\n"
        f"Source: {primary.get('source', '')}{extra}\n"
    )


def _job_html_block(job: dict) -> str:
    sources = job.get("sources") or []
    primary = sources[0] if sources else {}
    extra = f" (+{len(sources) - 1} more source(s))" if len(sources) > 1 else ""
    exp = f"{job.get('required_years')}+ yrs" if job.get("required_years") else "not specified"
    location = "Remote" if job.get("remote") else (job.get("location") or "Unspecified")
    reasons = "; ".join(job.get("match_reasons") or [])
    return f"""
    <tr><td style="padding:12px 0;border-bottom:1px solid #eee">
      <div style="font-size:16px;font-weight:bold">{escape(job.get('title', ''))}</div>
      <div style="color:#555">{escape(job.get('company', ''))} — {escape(location)}</div>
      <div style="font-size:13px;color:#777">Posted: {escape(job.get('posted_at') or 'unknown')} &middot; Experience: {escape(exp)}</div>
      <div style="font-size:13px;margin:4px 0">{escape(reasons)}</div>
      <div style="font-size:13px">
        <a href="{escape(primary.get('application_url', ''))}">Apply</a> &middot;
        <a href="{escape(primary.get('original_url', ''))}">Original post</a> &middot;
        {escape(primary.get('source', ''))}{escape(extra)}
      </div>
    </td></tr>"""


def render_email(jobs: list[dict]) -> tuple[str, str]:
    if not jobs:
        return NO_MATCHES_TEXT, f"<p>{NO_MATCHES_TEXT}</p>"
    text = "\n---\n".join(_job_text_block(j) for j in jobs)
    html_rows = "".join(_job_html_block(j) for j in jobs)
    html = f"""<html><body style="font-family:sans-serif;max-width:640px">
    <h2>{len(jobs)} new matching job(s)</h2>
    <table style="width:100%;border-collapse:collapse">{html_rows}</table>
    </body></html>"""
    return text, html


def send_email(to_addr: str, gmail_address: str, gmail_app_password: str, jobs: list[dict], dry_run: bool = False) -> str:
    text, html = render_email(jobs)
    subject = f"Job Radar: {len(jobs)} new match(es)" if jobs else "Job Radar: no new matches today"

    if dry_run:
        print(f"[DRY RUN] Subject: {subject}\n{text}")
        return text

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_addr
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_addr], msg.as_string())
    return text
