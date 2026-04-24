from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(r"C:\Users\DELL\Downloads\sip-lab-wsl2")
OUT = ROOT / "docs" / "Kamailio-Etisalat-Vapi-Lab-Evidence.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCenter",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubCenter",
            parent=styles["BodyText"],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#444444"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0B4F6C"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Tiny",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MonoLead",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8.3,
            leading=10.3,
            leftIndent=6,
            rightIndent=6,
            borderPadding=6,
            backColor=colors.HexColor("#F7F7F7"),
            borderColor=colors.HexColor("#D8D8D8"),
            borderWidth=0.5,
            borderRadius=3,
            spaceAfter=4,
        )
    )
    return styles


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(doc.leftMargin, 10 * mm, "Kamailio SIP SBC Lab Evidence Pack")
    canvas.drawRightString(A4[0] - doc.rightMargin, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def add_paragraphs(story, styles, section, paragraphs):
    story.append(Paragraph(section, styles["Section"]))
    for text in paragraphs:
        story.append(Paragraph(text, styles["Small"]))


def add_code(story, styles, text):
    story.append(Preformatted(text.strip(), styles["MonoLead"]))


def main():
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
        title="Kamailio Etisalat Vapi Lab Evidence",
        author="OpenAI Codex",
    )

    story = []

    story.append(Paragraph("Kamailio SIP SBC — Etisalat to Vapi", styles["TitleCenter"]))
    story.append(
        Paragraph(
            "Pre-bid validation lab • 7 scenarios revalidated with packet-level tshark evidence • April 2026",
            styles["SubCenter"],
        )
    )

    add_paragraphs(
        story,
        styles,
        "Purpose",
        [
            "Before proposal submission, the target Etisalat -> Kamailio SBC -> Vapi design was built and validated in a local WSL2 lab. The goal was to prove the core signaling and media-control behavior before any production carrier onboarding.",
            "The lab does <b>not</b> claim to prove real Etisalat trunk behavior, real Vapi credential acceptance, or AWS public-network behavior. It proves the SBC logic and packet flow for the intended integration pattern.",
        ],
    )

    add_paragraphs(
        story,
        styles,
        "Lab Topology",
        [
            "Fake carrier: <b>10.10.10.20</b> • SBC under test: <b>10.10.10.10</b> • Fake Vapi A: <b>10.10.10.41</b> • Fake Vapi B: <b>10.10.10.42</b> • Untrusted source: <b>10.10.10.99</b>.",
        ],
    )

    matrix = [
        ["#", "Scenario", "Primary proof", "Result"],
        ["1", "PAI ANI extraction + custom ANI headers", "tshark decoded INVITE", "PASS"],
        ["2", "From-user ANI fallback", "tshark decoded INVITE", "PASS"],
        ["3", "Untrusted source rejected with 403", "tshark + Kamailio log", "PASS"],
        ["4", "Pike rate limiting", "tshark metrics", "PASS"],
        ["5", "Dispatcher failover on upstream 503", "tshark summary", "PASS"],
        ["6", "SDP/media anchoring via RTPEngine", "tshark + RTPEngine log", "PASS"],
        ["7", "CANCEL cleanup via RTPEngine delete", "tshark + RTPEngine log", "PASS"],
    ]
    table = Table(matrix, colWidths=[12 * mm, 78 * mm, 48 * mm, 20 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0B4F6C")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C7D1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBFD")]),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (-1, 1), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(Paragraph("Test Matrix", styles["Section"]))
    story.append(table)

    stack = [
        ["Component", "Version / mode", "Notes"],
        ["Kamailio", "5.7.4", "dispatcher, rtpengine, uac, dialog, pike, textops"],
        ["RTPEngine", "userspace daemon", "offer / answer / delete hooks validated"],
        ["SIPp", "v3.7.2 via sip-tester", "carrier UAC and Vapi UAS scenarios"],
        ["OS", "Ubuntu 24.04.4 on WSL2", "used only for local validation"],
    ]
    stack_table = Table(stack, colWidths=[28 * mm, 38 * mm, 90 * mm])
    stack_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.2),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CFCFCF")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
            ]
        )
    )
    story.append(Spacer(1, 5))
    story.append(Paragraph("Stack Under Test", styles["Section"]))
    story.append(stack_table)

    story.append(PageBreak())

    add_paragraphs(
        story,
        styles,
        "Evidence 1 — PAI extraction and custom ANI headers",
        [
            "The forwarded INVITE shows the Vapi-style credential Request-URI, the rewritten <b>From</b>, and both custom ANI headers. Wireshark marks the custom headers as unrecognised SIP headers, which is expected for custom extensions.",
        ],
    )
    add_code(
        story,
        styles,
        """
Request-Line: INVITE sip:+97145550123@localcred.sip.vapi.ai SIP/2.0
From: <sip:971501234567@etisalat.local>;tag=1
P-Asserted-Identity: <sip:971501234567@etisalat.local>
X-Original-Caller: 971501234567
X-Original_Caller: 971501234567
        """,
    )

    add_paragraphs(
        story,
        styles,
        "Evidence 2 — From-user fallback when PAI is absent",
        [
            "When <b>P-Asserted-Identity</b> is missing, ANI falls back to the <b>From</b> user and is still forwarded correctly.",
        ],
    )
    add_code(
        story,
        styles,
        """
Request-Line: INVITE sip:+97145550123@localcred.sip.vapi.ai SIP/2.0
From: <sip:971509876543@etisalat.local>;tag=1
X-Original-Caller: 971509876543
X-Original_Caller: 971509876543
        """,
    )

    add_paragraphs(
        story,
        styles,
        "Evidence 3 — Trust-boundary enforcement",
        [
            "Traffic from a non-trusted source IP is rejected with <b>403 Forbidden</b> before normal routing proceeds.",
        ],
    )
    add_code(
        story,
        styles,
        """
10.10.10.99:5063 > 10.10.10.10:5060   INVITE sip:800@lab.local
10.10.10.10:5060 > 10.10.10.99:5063   SIP/2.0 403 Forbidden
10.10.10.99:5063 > 10.10.10.10:5060   ACK sip:800@lab.local
        """,
    )

    story.append(PageBreak())

    add_paragraphs(
        story,
        styles,
        "Evidence 4 — SDP/media anchoring via RTPEngine",
        [
            "The carrier offer is rewritten so the SBC becomes the advertised media endpoint. The same happens on the answer path back toward the carrier.",
        ],
    )
    add_code(
        story,
        styles,
        """
Offer path (carrier -> SBC -> Vapi)
carrier SDP:   o=carrier 1 1 IN IP4 10.10.10.20
               c=IN IP4 10.10.10.20
               m=audio 5064 RTP/AVP 0

forwarded SDP: o=carrier 1 1 IN IP4 10.10.10.10
               c=IN IP4 10.10.10.10
               m=audio 40036 RTP/AVP 0
               a=rtcp:40037

Answer path (Vapi -> SBC -> carrier)
vapi SDP:      o=vapi 1 1 IN IP4 10.10.10.41
               c=IN IP4 10.10.10.41
               m=audio 7078 RTP/AVP 0

rewritten SDP: o=vapi 1 1 IN IP4 10.10.10.10
               c=IN IP4 10.10.10.10
               m=audio 40070 RTP/AVP 0
               a=rtcp:40071
        """,
    )

    add_paragraphs(
        story,
        styles,
        "Evidence 5 — Dispatcher failover",
        [
            "When the primary upstream returns <b>503 Service Unavailable</b>, Kamailio retries the secondary destination and the call completes.",
        ],
    )
    add_code(
        story,
        styles,
        """
10.10.10.10 -> 10.10.10.41   INVITE sip:+97145550123@localcred.sip.vapi.ai
10.10.10.41 -> 10.10.10.10   SIP/2.0 503 Service Unavailable
10.10.10.10 -> 10.10.10.42   INVITE sip:+97145550123@localcred.sip.vapi.ai
10.10.10.42 -> 10.10.10.10   SIP/2.0 200 OK
10.10.10.10 -> 10.10.10.20   SIP/2.0 200 OK
        """,
    )

    add_paragraphs(
        story,
        styles,
        "Evidence 6 — Pike flood protection",
        [
            "The trusted-source flood test confirms that Pike is active and returns visible <b>503 Rate Limit Exceeded</b> responses once the threshold is crossed.",
        ],
    )
    add_code(
        story,
        styles,
        """
carrier_invites=100
blocked_503=87
representative response: SIP/2.0 503 Rate Limit Exceeded
        """,
    )

    story.append(PageBreak())

    add_paragraphs(
        story,
        styles,
        "Evidence 7 — CANCEL cleanup via RTPEngine delete",
        [
            "The lab proves caller-side CANCEL response handling, upstream CANCEL propagation, final <b>487 Request Terminated</b> relay, and RTPEngine cleanup.",
        ],
    )
    add_code(
        story,
        styles,
        """
10.10.10.20 -> 10.10.10.10   INVITE sip:800@lab.local
10.10.10.10 -> 10.10.10.41   INVITE sip:+97145550123@localcred.sip.vapi.ai
10.10.10.41 -> 10.10.10.10   SIP/2.0 180 Ringing
10.10.10.20 -> 10.10.10.10   CANCEL sip:800@lab.local
10.10.10.10 -> 10.10.10.41   CANCEL sip:+97145550123@localcred.sip.vapi.ai
10.10.10.10 -> 10.10.10.20   SIP/2.0 200 canceling (CANCEL)
10.10.10.41 -> 10.10.10.10   SIP/2.0 200 OK (CANCEL)
10.10.10.41 -> 10.10.10.10   SIP/2.0 487 Request Terminated
10.10.10.10 -> 10.10.10.20   SIP/2.0 487 Request Terminated
RTPEngine log: offer -> delete -> delete
        """,
    )

    prod = [
        ["Area", "Production work still required"],
        ["AWS deployment", "Elastic IP, public/private address handling, security groups, service management, log rotation."],
        ["Transport", "Confirm UDP/TCP/TLS requirements with Etisalat and Vapi; add TCP/TLS listeners only as required."],
        ["RTPEngine", "Configure AWS-appropriate media address handling for public/private deployment."],
        ["Timers and health checks", "Replace lab timers with WAN-appropriate values and enable dispatcher health monitoring."],
        ["Trust model", "Replace the single-IP lab gate with the real Etisalat source allowlist model."],
        ["Vapi validation", "Confirm the canonical ANI header name and live credential behavior against the real tenant."],
    ]
    prod_table = Table(prod, colWidths=[34 * mm, 138 * mm])
    prod_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.1),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CFCFCF")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(Paragraph("What Remains For Production", styles["Section"]))
    story.append(prod_table)
    story.append(Spacer(1, 7))
    story.append(
        Paragraph(
            "The complete evidence set — current configs, SIPp scenarios, pcaps, tshark proofs, and runtime logs — is available in the accompanying project folder.",
            styles["Small"],
        )
    )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    main()
