"""
Landing pages shown to users after they click a link in an email.

These are not emails — they're full HTML pages rendered by FastAPI when someone
visits /confirm/<token> or /approve/<token>. They use the same Ideaalnet brand
palette as the dashboard.
"""

from .templates.brand import (
    GRAD_START, GRAD_END, PRIMARY, DARK, BODY, BG, WHITE, BORDER,
    SUCCESS, SUCCESS_BG, WARN, WARN_BG, DANGER, DANGER_BG, RADIUS, SHADOW,
    GRADIENT_BG, GRADIENT_BG_FLAT, BRAND_NAME,
)


def landing_page(
    *,
    title: str,
    heading: str,
    message: str,
    variant: str = "success",
    extra_html: str = "",
) -> str:
    """Render a full HTML landing page. Variant controls the accent color."""
    palette = {
        "success": (SUCCESS, SUCCESS_BG, "✓"),
        "info": (PRIMARY, f"{PRIMARY}1A", "ⓘ"),
        "warn": (WARN, WARN_BG, "!"),
        "danger": (DANGER, DANGER_BG, "✕"),
    }
    accent, accent_bg, icon = palette.get(variant, palette["info"])

    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} — {BRAND_NAME}</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Montserrat',-apple-system,BlinkMacSystemFont,sans-serif; background:{BG}; color:{DARK}; min-height:100vh; display:flex; flex-direction:column; }}
  nav {{ background:{WHITE}; border-bottom:1px solid {BORDER}; padding:0 28px; height:58px; display:flex; align-items:center; }}
  .nav-logo {{ font-size:20px; font-weight:700; letter-spacing:-.5px; background:linear-gradient(90deg,{GRAD_START},{GRAD_END}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
  main {{ flex:1; display:flex; align-items:center; justify-content:center; padding:40px 20px; }}
  .card {{ max-width:520px; width:100%; background:{WHITE}; border:1px solid {BORDER}; border-radius:{RADIUS}; box-shadow:{SHADOW}; padding:48px 40px; text-align:center; animation:fadeUp .35s ease both; }}
  @keyframes fadeUp {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
  .icon-wrap {{ width:64px; height:64px; margin:0 auto 20px; border-radius:50%; background:{accent_bg}; color:{accent}; display:flex; align-items:center; justify-content:center; font-size:28px; font-weight:700; }}
  h1 {{ font-size:22px; font-weight:700; color:{DARK}; margin-bottom:12px; letter-spacing:-.3px; }}
  p {{ font-size:14px; color:{BODY}; line-height:1.6; }}
  .extra {{ margin-top:28px; padding-top:24px; border-top:1px solid {BORDER}; text-align:left; }}
</style>
</head>
<body>
<nav>
  <div class="nav-logo">{BRAND_NAME}</div>
</nav>
<main>
  <div class="card">
    <div class="icon-wrap">{icon}</div>
    <h1>{heading}</h1>
    <p>{message}</p>
    {f'<div class="extra">{extra_html}</div>' if extra_html else ''}
  </div>
</main>
</body>
</html>"""


def dev_link_block(label: str, url: str) -> str:
    """A dev-only block that displays a clickable link, used until real emails are wired up."""
    return f"""
    <p style="font-size:11px; font-weight:600; color:{BODY}; text-transform:uppercase; letter-spacing:.05em; margin-bottom:8px;">
      {label}
    </p>
    <p style="font-size:12px; line-height:1.5;">
      In productie staat deze link in de e-mail. Voor nu:
    </p>
    <a href="{url}" style="display:block; margin-top:10px; padding:12px 16px; background:{GRADIENT_BG_FLAT}; background-image:{GRADIENT_BG}; color:{WHITE}; text-decoration:none; border-radius:8px; font-size:13px; font-weight:600; word-break:break-all;">
      {url}
    </a>
    """