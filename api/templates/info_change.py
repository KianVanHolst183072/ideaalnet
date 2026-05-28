"""
Info change flow — emails sent when a customer changes their account info
(name, phone, address, email, etc.) via the Botpress chatbot.

Flow:
  1. user_confirm  — sent to customer asking them to confirm the change
  2. support_review — sent to customer support after user confirms
  3. user_final    — sent to customer once support approves
"""

from .brand import (
    email_shell,
    change_summary_box,
    primary_button,
    info_pill,
    DARK,
    BODY,
    BORDER,
    SUCCESS,
    SUCCESS_BG,
    BG,
    PRIMARY,
)


def user_confirm(field: str, oldfield: str, newfield: str, confirm_link: str) -> str:
    """Email #1 — asks the customer to confirm a change they requested."""
    body = f"""
      <p style="margin:0 0 10px;">{info_pill("Bevestiging vereist", "warn")}</p>
      <h1 style="margin:0 0 14px; font-size:24px; font-weight:700; color:{DARK}; letter-spacing:-0.3px;">
        Bevestig uw wijziging
      </h1>
      <p style="margin:0 0 8px; font-size:14px; line-height:1.6; color:{BODY};">
        Wij hebben een verzoek ontvangen om uw <strong style="color:{DARK};">{field}</strong> te wijzigen.
      </p>
      <p style="margin:0; font-size:14px; line-height:1.6; color:{BODY};">
        Bevestig deze wijziging door op de onderstaande knop te klikken.
      </p>

      {change_summary_box(field, oldfield, newfield)}

      {primary_button("Bevestig wijziging", confirm_link)}

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:24px; background:{BG}; border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <p style="margin:0; font-size:12px; line-height:1.5; color:{BODY};">
              <strong style="color:{DARK};">Let op:</strong> deze link verloopt over <strong>15 minuten</strong>. Heeft u deze wijziging niet aangevraagd? Dan kunt u deze e-mail negeren — er gebeurt dan niets.
            </p>
          </td>
        </tr>
      </table>
    """
    return email_shell(
        title=f"Bevestig uw {field} wijziging",
        preheader=f"Bevestig de wijziging van uw {field} door op de link te klikken.",
        body_html=body,
    )


def support_review(customer_email: str, field: str, oldfield: str, newfield: str, approve_link: str) -> str:
    """Email #2 — notifies customer support that a confirmed change is awaiting approval."""
    body = f"""
      <p style="margin:0 0 10px;">{info_pill("Wijziging ter goedkeuring", "info")}</p>
      <h1 style="margin:0 0 14px; font-size:24px; font-weight:700; color:{DARK}; letter-spacing:-0.3px;">
        Klant wil een wijziging
      </h1>
      <p style="margin:0; font-size:14px; line-height:1.6; color:{BODY};">
        De klant heeft de wijziging via e-mail bevestigd. Controleer en keur de wijziging hieronder goed.
      </p>

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:20px 0; background:{BG}; border-radius:10px; border:1px solid {BORDER};">
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 4px; font-size:10px; font-weight:600; color:{BODY}; text-transform:uppercase; letter-spacing:0.06em;">Klant</p>
            <p style="margin:0; font-size:14px; font-weight:600; color:{DARK};">{customer_email}</p>
          </td>
        </tr>
      </table>

      {change_summary_box(field, oldfield, newfield)}

      {primary_button("Goedkeuren in dashboard", approve_link)}

      <p style="margin:20px 0 0; font-size:12px; line-height:1.5; color:{BODY};">
        U kunt deze aanvraag ook beoordelen in het <a href="#" style="color:{PRIMARY}; text-decoration:none; font-weight:600;">klantenservice-dashboard</a>.
      </p>
    """
    return email_shell(
        title=f"Wijzigingsverzoek: {field}",
        preheader=f"{customer_email} wil hun {field} wijzigen.",
        body_html=body,
    )


def user_final(field: str, oldfield: str, newfield: str) -> str:
    """Email #3 — confirms to the customer that the change has been applied."""
    body = f"""
      <p style="margin:0 0 10px;">{info_pill("Wijziging doorgevoerd", "success")}</p>
      <h1 style="margin:0 0 14px; font-size:24px; font-weight:700; color:{DARK}; letter-spacing:-0.3px;">
        Uw wijziging is doorgevoerd
      </h1>
      <p style="margin:0; font-size:14px; line-height:1.6; color:{BODY};">
        Goed nieuws — uw verzoek is goedgekeurd en de wijziging is verwerkt in uw account.
      </p>

      {change_summary_box(field, oldfield, newfield)}

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:24px; background:{SUCCESS_BG}; border-radius:10px; border:1px solid {SUCCESS}33;">
        <tr>
          <td style="padding:14px 18px;">
            <p style="margin:0; font-size:13px; line-height:1.5; color:{SUCCESS};">
              <strong>✓ Klaar.</strong> De wijziging is direct actief in uw account.
            </p>
          </td>
        </tr>
      </table>

      <p style="margin:24px 0 0; font-size:13px; line-height:1.6; color:{BODY};">
        Vragen? Beantwoord deze e-mail en ons team helpt u graag verder.
      </p>
    """
    return email_shell(
        title=f"Uw {field} is bijgewerkt",
        preheader=f"Uw {field} is succesvol gewijzigd in uw account.",
        body_html=body,
    )
