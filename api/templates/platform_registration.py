"""
Platform registration flow — emails sent when a prospect applies for the
Ideaalnet platform via the Botpress chatbot.

Flow:
  1. support_notification — sent to customer support with all registration details
  2. customer_autoreply   — sent to the prospect confirming receipt

Optional fields (anything besides `naam`) are only rendered if they have a value.
This keeps the email tidy when the prospect skips questions.
"""

from .brand import (
    email_shell,
    primary_button,
    info_pill,
    DARK,
    BODY,
    BORDER,
    BG,
    PRIMARY,
    SUCCESS,
    SUCCESS_BG,
    WHITE,
    GRADIENT_BG,
    GRADIENT_BG_FLAT,
)


def _detail_row(label: str, value: str | None) -> str:
    """Render one row of the registration details table. Returns empty string
    if the value is missing/blank — that's how optional fields disappear."""
    if not value or not str(value).strip():
        return ""
    return f"""
      <tr>
        <td style="padding:14px 22px; border-bottom:1px solid {BORDER}; vertical-align:top; width:38%;">
          <p style="margin:0; font-size:11px; font-weight:600; color:{BODY}; text-transform:uppercase; letter-spacing:0.06em;">{label}</p>
        </td>
        <td style="padding:14px 22px; border-bottom:1px solid {BORDER};">
          <p style="margin:0; font-size:14px; font-weight:500; color:{DARK};">{value}</p>
        </td>
      </tr>
    """


def _details_table(rows: list[tuple[str, str | None]]) -> str:
    """Render a clean details table, skipping any rows with no value.

    Also strips the bottom border from the last visible row so it doesn't
    look weird against the rounded card.
    """
    rendered = [_detail_row(label, value) for label, value in rows]
    rendered = [r for r in rendered if r]  # drop empties

    if not rendered:
        return ""

    # Remove the bottom border from the final row
    rendered[-1] = rendered[-1].replace(
        f"border-bottom:1px solid {BORDER};",
        "border-bottom:none;",
    )

    return f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BG}; border-radius:10px; border:1px solid {BORDER}; margin:20px 0; overflow:hidden;">
      {"".join(rendered)}
    </table>
    """


def support_notification(
    *,
    naam: str,
    email: str,
    rol: str | None = None,
    schoolnaam: str | None = None,
    onderwijsniveau: str | None = None,
    regio: str | None = None,
    info: str | None = None,
) -> str:
    """Email #1 — customer support is notified of a new platform registration."""

    rows = [
        ("Naam", naam),
        ("E-mailadres", email),
        ("Rol", rol),
        ("School / Organisatie", schoolnaam),
        ("Onderwijsniveau", onderwijsniveau),
        ("Regio", regio),
    ]

    # Free-text "info" field gets its own styled block since it can be long
    info_block = ""
    if info and info.strip():
        info_block = f"""
        <p style="margin:24px 0 8px; font-size:11px; font-weight:600; color:{BODY}; text-transform:uppercase; letter-spacing:0.06em;">
          Aanvullende informatie
        </p>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BG}; border-radius:10px; border:1px solid {BORDER};">
          <tr>
            <td style="padding:16px 20px;">
              <p style="margin:0; font-size:13px; line-height:1.6; color:{DARK}; white-space:pre-wrap;">{info}</p>
            </td>
          </tr>
        </table>
        """

    body = f"""
      <p style="margin:0 0 10px;">{info_pill("Nieuwe registratie", "info")}</p>
      <h1 style="margin:0 0 14px; font-size:24px; font-weight:700; color:{DARK}; letter-spacing:-0.3px;">
        Nieuwe platform-aanmelding
      </h1>
      <p style="margin:0; font-size:14px; line-height:1.6; color:{BODY};">
        Er heeft zich een nieuwe gebruiker aangemeld voor het Ideaalnet-platform via de chatbot. Neem contact op met de aanmelder om het proces te vervolgen.
      </p>

      {_details_table(rows)}
      {info_block}

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px; background:{BG}; border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <p style="margin:0; font-size:12px; line-height:1.5; color:{BODY};">
              <strong style="color:{DARK};">Volgende stap:</strong> de aanmelder heeft een automatische bevestiging ontvangen en verwacht binnen korte termijn contact.
            </p>
          </td>
        </tr>
      </table>
    """
    return email_shell(
        title=f"Nieuwe aanmelding: {naam}",
        preheader=f"{naam} heeft zich aangemeld voor het Ideaalnet-platform.",
        body_html=body,
    )


def customer_autoreply(*, naam: str) -> str:
    """Email #2 — auto-reply to the prospect confirming we received their registration."""

    body = f"""
      <p style="margin:0 0 10px;">{info_pill("Aanmelding ontvangen", "success")}</p>
      <h1 style="margin:0 0 14px; font-size:24px; font-weight:700; color:{DARK}; letter-spacing:-0.3px;">
        Bedankt voor uw aanmelding, {naam}!
      </h1>
      <p style="margin:0 0 12px; font-size:14px; line-height:1.6; color:{BODY};">
        Leuk dat u interesse heeft in het Ideaalnet-platform. Wij hebben uw gegevens goed ontvangen.
      </p>
      <p style="margin:0; font-size:14px; line-height:1.6; color:{BODY};">
        Een van onze collega's neemt zo spoedig mogelijk contact met u op om uw aanmelding te bespreken en de vervolgstappen door te nemen.
      </p>

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:28px 0; background:{SUCCESS_BG}; border-radius:10px; border:1px solid {SUCCESS}33;">
        <tr>
          <td style="padding:18px 22px;">
            <p style="margin:0 0 6px; font-size:13px; font-weight:600; color:{SUCCESS};">
              ✓ Uw aanmelding is succesvol ontvangen
            </p>
            <p style="margin:0; font-size:12.5px; line-height:1.5; color:{BODY};">
              Houd uw inbox (en eventueel uw spam-map) in de gaten — we reageren meestal binnen één werkdag.
            </p>
          </td>
        </tr>
      </table>

      <p style="margin:24px 0 0; font-size:13px; line-height:1.6; color:{BODY};">
        Heeft u in de tussentijd vragen? Beantwoord deze e-mail en wij helpen u graag verder.
      </p>
    """
    return email_shell(
        title="Aanmelding ontvangen",
        preheader=f"Bedankt voor uw aanmelding, {naam}. Wij nemen spoedig contact op.",
        body_html=body,
    )