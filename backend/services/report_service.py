from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


DISCLAIMER = (
    "This report is an automated pre-clearance assessment based on the "
    "configured catalog and licensing data. It does not constitute legal "
    "clearance, a licensing contract, or confirmation of rights ownership. "
    "Final licensing must be verified with the relevant rights holder."
)


def _text(value: object, fallback: str = "") -> str:
    """Convert catalog/user text into ReportLab-safe plain text."""
    return escape(str(value)) if value is not None else fallback


def generate_clearance_report(
    scene_description: str,
    budget: float,
    territory: str,
    scene_analysis: dict,
    recommendations: list,
    rejected_candidates: list,
) -> BytesIO:

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
    )

    story = []

    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    story.append(Paragraph("SYNCAGENT", title_style))

    story.append(
        Paragraph(
            "AI Music Pre-Clearance Report",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            subtitle_style,
        )
    )

    # --------------------------------------------------
    # Project information
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PROJECT REQUIREMENTS",
            section_style,
        )
    )

    project_data = [
        ["Budget", f"${budget:,.2f}"],
        ["Territory", territory],
        ["Scene", _text(scene_description)],
    ]

    project_table = Table(
        project_data,
        colWidths=[40 * mm, 130 * mm],
    )

    project_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    story.append(project_table)

    # --------------------------------------------------
    # Scene analysis
    # --------------------------------------------------

    story.append(
        Paragraph(
            "SCENE ANALYSIS",
            section_style,
        )
    )

    mood = _text(", ".join(scene_analysis.get("mood", [])))
    genres = _text(", ".join(scene_analysis.get("genres", [])))
    instrumentation = ", ".join(
        scene_analysis.get("instrumentation", [])
    )
    instrumentation = _text(instrumentation)

    bpm_min = scene_analysis.get("bpm_min", "-")
    bpm_max = scene_analysis.get("bpm_max", "-")

    analysis_data = [
        ["Mood", mood or "Not specified"],
        ["Energy", str(scene_analysis.get("energy", "-"))],
        ["Tempo", f"{bpm_min}–{bpm_max} BPM"],
        ["Genre", genres or "Not specified"],
        [
            "Instrumentation",
            instrumentation or "Not specified",
        ],
        [
            "Pacing",
            str(scene_analysis.get("pacing", "-")),
        ],
    ]

    analysis_table = Table(
        analysis_data,
        colWidths=[45 * mm, 125 * mm],
    )

    analysis_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("PADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )

    story.append(analysis_table)

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    story.append(
        Paragraph(
            "RECOMMENDED TRACKS",
            section_style,
        )
    )

    if not recommendations:
        story.append(
            Paragraph(
                "No catalog tracks satisfied all configured "
                "pre-clearance constraints.",
                body_style,
            )
        )
    else:
        recommendation_data = [
            [
                "Track",
                "Match",
                "License",
                "Status",
            ]
        ]

        for track in recommendations:
            recommendation_data.append(
                [
                    _text(track.get("title", "Unknown")),
                    f"{track.get('match_score', 0):.0f}%",
                    (
                        f"${track.get('license_cost', 0):,.2f}"
                        if track.get("license_cost") is not None
                        else "N/A"
                    ),
                    "PASSED CONFIGURED CHECKS",
                ]
            )

        recommendation_table = Table(
            recommendation_data,
            colWidths=[
                65 * mm,
                30 * mm,
                35 * mm,
                40 * mm,
            ],
            repeatRows=1,
        )

        recommendation_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        story.append(recommendation_table)

        for track in recommendations:

            story.append(Spacer(1, 8))

            title = _text(track.get("title", "Unknown"))
            artist = _text(track.get("artist", "Catalog artist"))
            reason = _text(track.get("reason", ""))
            score = track.get("match_score", 0)

            story.append(
                Paragraph(
                    f"<b>{title}</b><br/>Artist: {artist} — {score:.0f}% creative match",
                    body_style,
                )
            )

            if reason:
                story.append(
                    Paragraph(
                        reason,
                        body_style,
                    )
                )

    # --------------------------------------------------
    # Rejected candidates
    # --------------------------------------------------

    story.append(
        Paragraph(
            "REJECTED CANDIDATES",
            section_style,
        )
    )

    if not rejected_candidates:

        story.append(
            Paragraph(
                "No rejected candidates were reported.",
                body_style,
            )
        )

    else:

        rejected_data = [
            [
                "Track",
                "Creative Match",
                "Reason",
            ]
        ]

        for track in rejected_candidates:

            score = track.get("match_score")

            score_text = (
                f"{score:.0f}%"
                if score is not None
                else "N/A"
            )

            rejected_data.append(
                [
                    _text(track.get("title", "Unknown")),
                    score_text,
                    _text(track.get(
                        "reason",
                        "Constraint failed.",
                    )),
                ]
            )

        rejected_table = Table(
            rejected_data,
            colWidths=[
                50 * mm,
                35 * mm,
                85 * mm,
            ],
            repeatRows=1,
        )

        rejected_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        story.append(rejected_table)

    # --------------------------------------------------
    # Disclaimer
    # --------------------------------------------------

    story.append(
        Paragraph(
            "IMPORTANT",
            section_style,
        )
    )

    story.append(
        Paragraph(
            DISCLAIMER,
            body_style,
        )
    )

    # --------------------------------------------------
    # Build
    # --------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return buffer