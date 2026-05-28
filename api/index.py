"""
Ideaalnet Email Notification API — preview mode.

Currently this API does not send any emails. Each endpoint renders an HTML email
template and saves it as a file in the previews/ directory so you can open it in
the browser or download it. SMTP sending will be wired in once the mail server
is configured.

Endpoint conventions:
  /preview/<flow>/<step>     GET  — render HTML inline in browser
  /api/<flow>/<step>         POST — render HTML, save to disk, return file URL

Currently implemented flow:
  info_change : user_confirm → support_review → user_final

Future flows will follow the same pattern (orders, repairs, delivery, etc.).
"""

import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from .templates import info_change

app = FastAPI(
    title="Ideaalnet Email API",
    description=(
        "Generates and previews customer service emails. "
        "Currently in **preview mode** — no emails are sent. "
        "Each POST endpoint renders the template and saves it to `previews/` for inspection."
    ),
    version="0.1.0",
)

# Directory where rendered previews are saved.
# Default to <project-root>/previews so it's always in the same place, regardless
# of where uvicorn was launched from. Vercel's filesystem is read-only except
# for /tmp, so we use that there.
if os.environ.get("VERCEL"):
    # Running on Vercel — only /tmp is writable, and it doesn't persist between
    # invocations, but it's fine for short-lived testing.
    PREVIEW_DIR = Path("/tmp/previews")
else:
    # Local dev — store next to the code so files persist between restarts.
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    PREVIEW_DIR = Path(os.environ.get("PREVIEW_DIR", PROJECT_ROOT / "previews"))

PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

# Serve the previews/ directory at /files so generated emails are accessible by URL
app.mount("/files", StaticFiles(directory=str(PREVIEW_DIR)), name="files")


# ────────────────────────────────────────────────────────────────────────────
# Request models
# ────────────────────────────────────────────────────────────────────────────

class InfoChangeRequest(BaseModel):
    """Payload for the info-change flow. Sent by Botpress when a customer
    requests to change their account info."""
    email: EmailStr = Field(..., description="Customer email address", examples=["klant@example.com"])
    field: str = Field(..., description="Which field is being changed", examples=["telefoonnummer"])
    oldfield: str = Field("", description="Current value", examples=["+31 6 1234 5678"])
    newfield: str = Field("", description="Desired new value", examples=["+31 6 9876 5432"])


class SupportReviewRequest(BaseModel):
    customer_email: EmailStr = Field(..., examples=["klant@example.com"])
    field: str = Field(..., examples=["telefoonnummer"])
    oldfield: str = Field("", examples=["+31 6 1234 5678"])
    newfield: str = Field("", examples=["+31 6 9876 5432"])


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def save_preview(filename: str, html: str) -> dict:
    """Save rendered email HTML to disk and return access metadata."""
    safe = filename.replace("/", "_").replace("\\", "_")
    path = PREVIEW_DIR / safe
    path.write_text(html, encoding="utf-8")
    return {
        "saved_as": safe,
        "url": f"/files/{safe}",
        "size_bytes": path.stat().st_size,
    }


def require_api_key(x_api_key: str | None):
    """Validate the x-api-key header against the API_KEY env var.

    If API_KEY isn't set in the environment, auth is disabled (useful for local dev).
    In production (Vercel), set the API_KEY env var so only Botpress can call the API.
    """
    expected = os.environ.get("API_KEY")
    if not expected:
        return  # auth disabled — local dev without API_KEY env var
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ────────────────────────────────────────────────────────────────────────────
# Index / hub
# ────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """Preview hub — landing page with links to all available previews."""
    return _hub_html()


@app.get("/api/saved_previews", tags=["previews"])
def list_saved_previews():
    """List all rendered preview files currently saved on disk."""
    files = []
    for p in sorted(PREVIEW_DIR.glob("*.html"), key=lambda f: f.stat().st_mtime, reverse=True):
        stat = p.stat()
        files.append({
            "name": p.name,
            "url": f"/files/{p.name}",
            "size_bytes": stat.st_size,
            "modified_at": int(stat.st_mtime),
        })
    return {"count": len(files), "files": files}


@app.delete("/api/saved_previews/{filename}", tags=["previews"])
def delete_saved_preview(filename: str):
    """Delete a single saved preview file."""
    safe = filename.replace("/", "_").replace("\\", "_")
    path = PREVIEW_DIR / safe
    if not path.exists():
        return {"deleted": False, "reason": "not_found"}
    path.unlink()
    return {"deleted": True, "name": safe}


@app.delete("/api/saved_previews", tags=["previews"])
def delete_all_saved_previews():
    """Delete every saved preview file."""
    count = 0
    for p in PREVIEW_DIR.glob("*.html"):
        p.unlink()
        count += 1
    return {"deleted": count}


@app.get("/api/debug", tags=["previews"])
def debug_storage():
    """Diagnostic: shows exactly where previews are being saved and verifies writability."""
    import sys
    test_file = PREVIEW_DIR / ".write_test"
    writable = False
    write_error = None
    try:
        test_file.write_text("ok")
        test_file.unlink()
        writable = True
    except Exception as e:
        write_error = str(e)

    return {
        "preview_dir": str(PREVIEW_DIR),
        "preview_dir_absolute": str(PREVIEW_DIR.resolve()),
        "exists": PREVIEW_DIR.exists(),
        "writable": writable,
        "write_error": write_error,
        "files_in_dir": sorted([p.name for p in PREVIEW_DIR.glob("*")]) if PREVIEW_DIR.exists() else [],
        "cwd": os.getcwd(),
        "is_vercel": bool(os.environ.get("VERCEL")),
        "python_version": sys.version,
    }


# ────────────────────────────────────────────────────────────────────────────
# Info change flow — POST endpoints (Swagger UI: fill in fields → Execute → view)
# ────────────────────────────────────────────────────────────────────────────

@app.post("/api/info_change/user_confirm", tags=["info_change"])
def generate_user_confirm(
    payload: InfoChangeRequest,
    x_api_key: str | None = Header(default=None),
):
    """
    Generate the **customer confirmation** email.

    **This is the endpoint Botpress calls** to start the info-change flow.
    In production it will both generate AND send the email; right now it only
    renders and saves it as a file in `previews/`.

    Requires `x-api-key` header to match the `API_KEY` env var (if set).
    """
    require_api_key(x_api_key)
    html = info_change.user_confirm(
        payload.field, payload.oldfield, payload.newfield,
        confirm_link="#preview-mode-no-real-link",
    )
    return {
        "status": "rendered",
        "flow": "info_change",
        "step": "user_confirm",
        "recipient": payload.email,
        **save_preview(f"info_change_user_confirm.html", html),
    }


@app.post("/api/info_change/support_review", tags=["info_change"])
def generate_support_review(payload: SupportReviewRequest):
    """
    Generate the **customer-support review** email.

    Triggered after the customer clicks their confirmation link.
    """
    html = info_change.support_review(
        payload.customer_email, payload.field, payload.oldfield, payload.newfield,
        approve_link="#preview-mode-no-real-link",
    )
    return {
        "status": "rendered",
        "flow": "info_change",
        "step": "support_review",
        **save_preview(f"info_change_support_review.html", html),
    }


@app.post("/api/info_change/user_final", tags=["info_change"])
def generate_user_final(payload: InfoChangeRequest):
    """
    Generate the **final confirmation** email to the customer.

    Triggered after customer support approves the change.
    """
    html = info_change.user_final(payload.field, payload.oldfield, payload.newfield)
    return {
        "status": "rendered",
        "flow": "info_change",
        "step": "user_final",
        "recipient": payload.email,
        **save_preview(f"info_change_user_final.html", html),
    }


# ────────────────────────────────────────────────────────────────────────────
# Hub page HTML — styled to match the dashboard
# ────────────────────────────────────────────────────────────────────────────

def _hub_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Ideaalnet — Email Preview Hub</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --grad-mid2: #1ECDAB;
      --grad-end:  #0091FF;
      --primary:   #0091FF;
      --dark1:     #1E293B;
      --body:      #485364;
      --bg:        #F8F8F8;
      --white:     #ffffff;
      --border:    #E8EDF2;
      --radius:    16px;
      --radius-sm: 10px;
      --shadow:    0 2px 12px rgba(0,145,255,0.07);
    }}
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:'Montserrat',sans-serif; background:var(--bg); color:var(--dark1); min-height:100vh; font-size:13px; }}

    nav {{ background:var(--white); border-bottom:1px solid var(--border); padding:0 28px; height:58px; display:flex; align-items:center; justify-content:space-between; }}
    .nav-logo {{ font-size:20px; font-weight:700; letter-spacing:-.5px; background:linear-gradient(90deg,var(--grad-mid2),var(--grad-end)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
    .nav-badge {{ background:linear-gradient(135deg,var(--grad-mid2),var(--grad-end)); color:white; padding:5px 14px; border-radius:99px; font-size:11px; font-weight:600; }}

    main {{ max-width:880px; margin:0 auto; padding:36px 24px; }}
    .page-title {{ font-size:24px; font-weight:700; color:var(--dark1); letter-spacing:-.3px; margin-bottom:4px; }}
    .page-sub {{ font-size:13px; color:var(--body); margin-bottom:28px; }}

    .section-title {{ font-size:11px; font-weight:600; color:var(--body); opacity:.7; text-transform:uppercase; letter-spacing:.08em; margin:28px 0 12px; }}
    .flow-card {{ background:var(--white); border-radius:var(--radius); border:1px solid var(--border); box-shadow:var(--shadow); margin-bottom:16px; overflow:hidden; }}
    .flow-header {{ padding:18px 22px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; }}
    .flow-name {{ font-size:15px; font-weight:700; color:var(--dark1); }}
    .flow-tag {{ font-size:10px; font-weight:700; padding:4px 10px; border-radius:99px; background:linear-gradient(135deg,rgba(30,205,171,.15),rgba(0,145,255,.15)); color:var(--primary); text-transform:uppercase; letter-spacing:.05em; }}
    .flow-tag.soon {{ background:#F0F0F0; color:#888; }}

    .step-row {{ padding:14px 22px; display:flex; align-items:center; gap:14px; border-bottom:1px solid var(--border); transition:background .15s; }}
    .step-row:last-child {{ border-bottom:none; }}
    .step-row:hover {{ background:var(--bg); }}
    .step-num {{ width:28px; height:28px; border-radius:50%; background:linear-gradient(135deg,var(--grad-mid2),var(--grad-end)); color:white; font-size:12px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
    .step-body {{ flex:1; min-width:0; }}
    .step-title {{ font-size:13px; font-weight:600; color:var(--dark1); margin-bottom:2px; }}
    .step-desc {{ font-size:11.5px; color:var(--body); }}
    .step-link {{ font-size:11px; font-weight:600; padding:6px 14px; border-radius:99px; background:linear-gradient(90deg,var(--grad-mid2),var(--grad-end)); color:white; text-decoration:none; white-space:nowrap; }}

    .util-card {{ background:var(--white); border-radius:var(--radius-sm); border:1px solid var(--border); padding:14px 18px; display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }}
    .util-card a {{ font-size:11px; font-weight:600; padding:6px 14px; border-radius:99px; background:var(--bg); color:var(--body); text-decoration:none; border:1px solid var(--border); }}
    .util-card a:hover {{ background:linear-gradient(90deg,var(--grad-mid2),var(--grad-end)); color:white; border-color:transparent; }}

    .card-list {{ background:var(--white); border-radius:var(--radius-sm); border:1px solid var(--border); padding:14px 22px; }}
    .card-list ul {{ list-style:none; padding:0; }}
    .card-list li {{ padding:8px 0; border-bottom:1px solid var(--border); font-size:12.5px; }}
    .card-list li:last-child {{ border-bottom:none; }}
    .card-list a {{ color:var(--primary); text-decoration:none; font-weight:500; }}
    .card-list a:hover {{ text-decoration:underline; }}

    code {{ background:var(--bg); padding:2px 6px; border-radius:4px; font-size:11px; font-family:'SF Mono',Menlo,monospace; color:var(--primary); }}
  </style>
</head>
<body>

<nav>
  <div class="nav-logo">Ideaalnet</div>
  <div class="nav-badge">Email Preview Hub</div>
</nav>

<main>
  <h1 class="page-title">Email templates</h1>
  <p class="page-sub">
    Preview every customer service email before it goes live. Customize with query params:
    <code>?field=adres&amp;oldfield=Oude Straat 1&amp;newfield=Nieuwe Straat 42</code>
  </p>

  <div class="section-title">Account info wijziging</div>
  <div class="flow-card">
    <div class="flow-header">
      <span class="flow-name">info_change</span>
      <span class="flow-tag">Live</span>
    </div>

    <div class="step-row">
      <div class="step-num">1</div>
      <div class="step-body">
        <div class="step-title">Bevestiging aan klant</div>
        <div class="step-desc">Wordt verstuurd nadat de klant via Botpress een wijziging aanvraagt.</div>
      </div>
      <a class="step-link" href="#" onclick="quickGenerate('info_change', 'user_confirm', this); return false;">Genereer voorbeeld</a>
    </div>

    <div class="step-row">
      <div class="step-num">2</div>
      <div class="step-body">
        <div class="step-title">Beoordeling klantenservice</div>
        <div class="step-desc">Wordt verstuurd nadat de klant zijn wijziging heeft bevestigd.</div>
      </div>
      <a class="step-link" href="#" onclick="quickGenerate('info_change', 'support_review', this); return false;">Genereer voorbeeld</a>
    </div>

    <div class="step-row">
      <div class="step-num">3</div>
      <div class="step-body">
        <div class="step-title">Eindbevestiging aan klant</div>
        <div class="step-desc">Wordt verstuurd nadat klantenservice de wijziging goedkeurt.</div>
      </div>
      <a class="step-link" href="#" onclick="quickGenerate('info_change', 'user_final', this); return false;">Genereer voorbeeld</a>
    </div>
  </div>

  <div class="section-title">Toekomstige flows</div>
  <div class="flow-card">
    <div class="flow-header">
      <span class="flow-name">order_status</span>
      <span class="flow-tag soon">Gepland</span>
    </div>
  </div>
  <div class="flow-card">
    <div class="flow-header">
      <span class="flow-name">repair_status</span>
      <span class="flow-tag soon">Gepland</span>
    </div>
  </div>
  <div class="flow-card">
    <div class="flow-header">
      <span class="flow-name">delivery</span>
      <span class="flow-tag soon">Gepland</span>
    </div>
  </div>

  <div class="section-title">Tools</div>
  <div class="util-card">
    <div>
      <div style="font-size:13px; font-weight:600;">Swagger UI</div>
      <div style="font-size:11px; color:var(--body);">Test endpoints, generate &amp; save previews to disk</div>
    </div>
    <a href="/docs" target="_blank">Openen</a>
  </div>
  <div class="util-card">
    <div>
      <div style="font-size:13px; font-weight:600;">ReDoc</div>
      <div style="font-size:11px; color:var(--body);">Alternatieve API-documentatie</div>
    </div>
    <a href="/redoc" target="_blank">Openen</a>
  </div>

  <div class="section-title" style="display:flex; align-items:center; justify-content:space-between;">
    <span>Opgeslagen previews <span id="saved-count" style="opacity:.5;">(laden...)</span></span>
    <span style="text-transform:none; letter-spacing:0; display:flex; gap:8px;">
      <button onclick="loadSaved()" style="font-size:10px; font-weight:600; padding:5px 12px; border-radius:99px; background:var(--white); color:var(--body); border:1px solid var(--border); cursor:pointer; font-family:inherit;">↻ Vernieuwen</button>
      <button onclick="deleteAll()" style="font-size:10px; font-weight:600; padding:5px 12px; border-radius:99px; background:#FFF0F0; color:#C0392B; border:1px solid #FFD0D0; cursor:pointer; font-family:inherit;">Alles wissen</button>
    </span>
  </div>
  <div id="saved-list" class="card-list">
    <div style="font-size:12px; color:var(--body); padding:8px 0; text-align:center;">Laden...</div>
  </div>
</main>

<script>
async function loadSaved() {{
  const list = document.getElementById('saved-list');
  const count = document.getElementById('saved-count');
  try {{
    const res = await fetch('/api/saved_previews');
    const data = await res.json();
    count.textContent = `(${{data.count}})`;
    if (data.count === 0) {{
      list.innerHTML = '<div style="font-size:12px; color:var(--body); padding:8px 0; text-align:center;">Nog geen previews opgeslagen. Genereer er een via Swagger UI.</div>';
      return;
    }}
    list.innerHTML = '<ul>' + data.files.map(f => {{
      const when = new Date(f.modified_at * 1000).toLocaleString('nl-NL', {{ dateStyle: 'short', timeStyle: 'short' }});
      return `<li style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
        <div style="min-width:0; flex:1;">
          <a href="${{f.url}}" target="_blank" style="display:block; font-weight:600;">${{f.name}}</a>
          <span style="font-size:10.5px; color:var(--body); opacity:.7;">${{when}} · ${{f.size_bytes}} bytes</span>
        </div>
        <div style="display:flex; gap:6px; flex-shrink:0;">
          <a href="${{f.url}}" target="_blank" style="font-size:10px; font-weight:600; padding:5px 12px; border-radius:99px; background:linear-gradient(90deg,var(--grad-mid2),var(--grad-end)); color:white; text-decoration:none;">Open</a>
          <button onclick="deleteOne('${{f.name}}')" style="font-size:10px; font-weight:600; padding:5px 10px; border-radius:99px; background:#FFF0F0; color:#C0392B; border:1px solid #FFD0D0; cursor:pointer; font-family:inherit;">✕</button>
        </div>
      </li>`;
    }}).join('') + '</ul>';
  }} catch (e) {{
    list.innerHTML = '<div style="font-size:12px; color:#C0392B; padding:8px 0;">Fout bij laden: ' + e.message + '</div>';
  }}
}}

async function deleteOne(name) {{
  if (!confirm('Verwijderen: ' + name + '?')) return;
  await fetch('/api/saved_previews/' + encodeURIComponent(name), {{ method: 'DELETE' }});
  loadSaved();
}}

async function deleteAll() {{
  if (!confirm('Alle opgeslagen previews verwijderen?')) return;
  await fetch('/api/saved_previews', {{ method: 'DELETE' }});
  loadSaved();
}}

loadSaved();
// Auto-refresh every 5 seconds so newly generated previews show up automatically
setInterval(loadSaved, 5000);

async function quickGenerate(flow, step, btn) {{
  // Sample payload — same shape as the API expects.
  // Support review uses customer_email, the others use email.
  const sample = step === 'support_review'
    ? {{ customer_email: 'klant@example.com', field: 'telefoonnummer',
         oldfield: '+31 6 1234 5678', newfield: '+31 6 9876 5432' }}
    : {{ email: 'klant@example.com', field: 'telefoonnummer',
         oldfield: '+31 6 1234 5678', newfield: '+31 6 9876 5432' }};

  const original = btn.textContent;
  btn.textContent = 'Genereren...';
  btn.style.opacity = '0.6';

  try {{
    const res = await fetch(`/api/${{flow}}/${{step}}`, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(sample),
    }});
    const data = await res.json();
    if (data.url) {{
      window.open(data.url, '_blank');
      loadSaved();
    }} else {{
      alert('Onverwacht antwoord: ' + JSON.stringify(data));
    }}
  }} catch (e) {{
    alert('Fout: ' + e.message);
  }} finally {{
    btn.textContent = original;
    btn.style.opacity = '1';
  }}
}}
</script>

</body>
</html>"""