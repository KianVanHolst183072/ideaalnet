"""
Password reset flow — single email sent when a user requests a password reset.

Flow:
  1. user_reset — sent to the user with a clickable reset link

The actual "set new password" page is hosted on the main app (not on this
API), so the email just contains a link to wherever that page lives.
"""

from .brand import (
    email_shell,
    primary_button,
    info_pill,
    DARK,
    BODY,
    BORDER,
    BG,
    WARN,
    WARN_BG,
)


def user_reset(reset_link: str, expires_in_minutes: int = 15) -> str:
    """Email sent to a user who requested a password reset.

    The link expires after `expires_in_minutes` minutes."""

    body = f"""
      <p style="margin:0 0 10px;">{info_pill("Wachtwoord opnieuw instellen", "warn")}</p>
      <h1 style="margin:0 0 14px; font-size:24px; font-weight:700; color:{DARK}; letter-spacing:-0.3px;">
        Wachtwoord opnieuw instellen
      </h1>
      <p style="margin:0 0 8px; font-size:14px; line-height:1.6; color:{BODY};">
        Wij hebben een verzoek ontvangen om uw wachtwoord opnieuw in te stellen.
      </p>
      <p style="margin:0; font-size:14px; line-height:1.6; color:{BODY};">
        Klik op de knop hieronder om een nieuw wachtwoord te kiezen.
      </p>

      {primary_button("Wachtwoord opnieuw instellen", reset_link)}

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:20px; background:{WARN_BG}; border-radius:10px; border:1px solid {WARN}33;">
        <tr>
          <td style="padding:14px 18px;">
            <p style="margin:0; font-size:12px; line-height:1.5; color:{BODY};">
              <strong style="color:{DARK};">Let op:</strong> deze link verloopt over <strong>{expires_in_minutes} minuten</strong>. Heeft u geen wachtwoordreset aangevraagd? Dan kunt u deze e-mail veilig negeren — uw wachtwoord blijft ongewijzigd.
            </p>
          </td>
        </tr>
      </table>

      <p style="margin:24px 0 0; font-size:12px; line-height:1.5; color:{BODY};">
        Werkt de knop niet? Kopieer en plak de volgende link in uw browser:
      </p>
      <p style="margin:6px 0 0; font-size:11px; line-height:1.5; color:{BODY}; word-break:break-all; background:{BG}; padding:10px 12px; border-radius:6px; border:1px solid {BORDER}; font-family:'SF Mono',Menlo,monospace;">
        {reset_link}
      </p>
    """
    return email_shell(
        title="Wachtwoord opnieuw instellen",
        preheader="Klik op de link in deze e-mail om uw wachtwoord opnieuw in te stellen.",
        body_html=body,
    )