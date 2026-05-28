"""
Shared brand styling for all Ideaalnet emails.

All templates use these tokens so future flows (orders, repairs, delivery)
inherit the same look automatically. If you want to rebrand, change values here.
"""

# Colors — matching the dashboard
GRAD_START = "#1ECDAB"       # teal
GRAD_END = "#0091FF"         # blue
PRIMARY = "#0091FF"
DARK = "#1E293B"
BODY = "#485364"
BG = "#F8F8F8"
WHITE = "#FFFFFF"
BORDER = "#E8EDF2"
SUCCESS = "#0A7A4F"
SUCCESS_BG = "#E8FFF5"
WARN = "#D4920A"
WARN_BG = "#FFF3CD"
DANGER = "#C0392B"
DANGER_BG = "#FFF0F0"

# Layout
RADIUS = "16px"
RADIUS_SM = "10px"
SHADOW = "0 2px 12px rgba(0,145,255,0.07)"

# Brand
BRAND_NAME = "Ideaalnet"
GRADIENT_BG = f"linear-gradient(135deg,{GRAD_START},{GRAD_END})"
GRADIENT_BG_FLAT = f"#0091FF"  # fallback for clients that don't render gradients (Outlook)


def email_shell(title: str, preheader: str, body_html: str) -> str:
    """Wraps email body in a consistent shell. Table-based for email-client compatibility."""
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="x-apple-disable-message-reformatting" />
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet" />
</head>
<body style="margin:0; padding:0; background:{BG}; font-family:'Montserrat',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; color:{DARK};">
  <span style="display:none; max-height:0; overflow:hidden; opacity:0; color:transparent;">{preheader}</span>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BG};">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px; width:100%; background:{WHITE}; border-radius:{RADIUS}; overflow:hidden; box-shadow:{SHADOW}; border:1px solid {BORDER};">

          <!-- Gradient header -->
          <tr>
            <td style="background:{GRADIENT_BG_FLAT}; background-image:{GRADIENT_BG}; padding:24px 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <span style="color:{WHITE}; font-size:22px; font-weight:700; letter-spacing:-0.5px;">{BRAND_NAME}</span>
                  </td>
                  <td align="right">
                    <span style="color:rgba(255,255,255,0.85); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.06em;">Klantenservice</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 32px;">
              {body_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 32px 28px; background:{BG}; border-top:1px solid {BORDER};">
              <p style="margin:0 0 6px; font-size:11px; color:{BODY}; text-align:center; line-height:1.5;">
                Dit is een geautomatiseerd bericht van {BRAND_NAME}.
              </p>
              <p style="margin:0; font-size:11px; color:{BODY}; opacity:0.7; text-align:center; line-height:1.5;">
                Heeft u dit bericht onbedoeld ontvangen? Dan kunt u het veilig negeren.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def change_summary_box(field: str, oldfield: str, newfield: str) -> str:
    """Reusable before/after summary block — used across the info-change flow."""
    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BG}; border-radius:{RADIUS_SM}; border:1px solid {BORDER}; margin:20px 0;">
      <tr>
        <td style="padding:20px 22px;">

          <p style="margin:0 0 4px; font-size:10px; font-weight:600; color:{BODY}; text-transform:uppercase; letter-spacing:0.06em;">Veld</p>
          <p style="margin:0 0 18px; font-size:15px; font-weight:600; color:{DARK};">{field}</p>

          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td width="50%" valign="top" style="padding-right:8px;">
                <p style="margin:0 0 4px; font-size:10px; font-weight:600; color:{BODY}; text-transform:uppercase; letter-spacing:0.06em;">Huidige waarde</p>
                <p style="margin:0; font-size:13px; color:#86868b; text-decoration:line-through;">{oldfield}</p>
              </td>
              <td width="50%" valign="top" style="padding-left:8px;">
                <p style="margin:0 0 4px; font-size:10px; font-weight:600; color:{SUCCESS}; text-transform:uppercase; letter-spacing:0.06em;">Nieuwe waarde</p>
                <p style="margin:0; font-size:13px; font-weight:600; color:{DARK};">{newfield}</p>
              </td>
            </tr>
          </table>

        </td>
      </tr>
    </table>
    """


def primary_button(label: str, href: str) -> str:
    """Gradient CTA button — primary action."""
    return f"""
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0;">
      <tr>
        <td style="background:{GRADIENT_BG_FLAT}; background-image:{GRADIENT_BG}; border-radius:99px;">
          <a href="{href}" style="display:inline-block; padding:13px 32px; color:{WHITE}; font-size:14px; font-weight:600; text-decoration:none; font-family:'Montserrat',sans-serif;">{label}</a>
        </td>
      </tr>
    </table>
    """


def secondary_button(label: str, href: str) -> str:
    """Outlined button — secondary action."""
    return f"""
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:16px 0;">
      <tr>
        <td style="background:{WHITE}; border:1.5px solid {BORDER}; border-radius:99px;">
          <a href="{href}" style="display:inline-block; padding:11px 28px; color:{BODY}; font-size:13px; font-weight:600; text-decoration:none; font-family:'Montserrat',sans-serif;">{label}</a>
        </td>
      </tr>
    </table>
    """


def info_pill(text: str, variant: str = "info") -> str:
    """Small status pill — for inline tags like 'Verloopt over 15 min'."""
    palette = {
        "info": (f"{PRIMARY}1A", PRIMARY),
        "warn": (f"{WARN}22", WARN),
        "success": (f"{SUCCESS}22", SUCCESS),
        "danger": (f"{DANGER}22", DANGER),
    }
    bg, color = palette.get(variant, palette["info"])
    return f'<span style="display:inline-block; padding:4px 10px; background:{bg}; color:{color}; font-size:10px; font-weight:700; border-radius:99px; text-transform:uppercase; letter-spacing:0.05em;">{text}</span>'
