from io import BytesIO
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
    KeepTogether
)


def generate_pdf_report(report) -> bytes:
    """
    Generate a downloadable PDF from a Pydantic SecurityReport.

    Returns:
        bytes: Generated PDF content.
    """

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
        fontSize=20,
        spaceAfter=15,
    )

    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    story = []

    # 1. Report title
    story.append(
        Paragraph("DevGuard Security Report", title_style)
    )

    story.append(
        Paragraph(
            f"<b>Project:</b> {escape(str(report.project_name))}",
            normal_style,
        )
    )

    story.append(Spacer(1, 12))

    # 2. Analysis summary
    story.append(
        Paragraph("Analysis Summary", heading_style)
    )

    story.append(
        Paragraph(
            escape(str(report.summary)),
            normal_style,
        )
    )

    story.append(Spacer(1, 12))

    # 3. Security findings overview
    story.append(
        Paragraph("Security Findings", heading_style)
    )

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }

    for finding in report.findings:
        severity = finding.severity.lower()

        if severity in severity_counts:
            severity_counts[severity] += 1

    overview_data = [
        ["Metric", "Count"],
        ["Total Findings", str(len(report.findings))],
        ["Critical", str(severity_counts["critical"])],
        ["High", str(severity_counts["high"])],
        ["Medium", str(severity_counts["medium"])],
        ["Low", str(severity_counts["low"])],
        ["Info", str(severity_counts["info"])],
        ["Failed Chunks", str(len(report.failed_chunks))],
        ["Warnings", str(len(report.warnings))],
    ]

    overview_table = Table(
        overview_data,
        colWidths=[85 * mm, 65 * mm],
    )

    overview_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263746")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )

    story.append(overview_table)
    story.append(Spacer(1, 15))

    # 4. Individual findings
    for index, finding in enumerate(report.findings, start=1):

        story.append(
            Paragraph(
                f"{index}. {escape(str(finding.title))}",
                heading_style,
            )
        )

        finding_details = [
            ("Severity", finding.severity),
            ("Category", finding.category),
            ("File", finding.file_path or "N/A"),
            ("Line", finding.line_number or "Unavailable"),
            ("Confidence", f"{finding.confidence * 100:.0f}%"),
        ]

        for label, value in finding_details:
            story.append(
                Paragraph(
                    f"<b>{escape(str(label))}:</b> "
                    f"{escape(str(value))}",
                    normal_style,
                )
            )

        story.append(Spacer(1, 5))

        for label, value in [
            ("Description", finding.description),
            ("Evidence", finding.evidence),
            ("Recommendation", finding.recommendation),
        ]:
            story.append(
                Paragraph(f"<b>{label}:</b>", normal_style)
            )

            story.append(
                Paragraph(
                    escape(str(value)).replace("\n", "<br/>"),
                    normal_style,
                )
            )

            story.append(Spacer(1, 7))

    # 5. General recommendations
    story.append(
        Paragraph("General Recommendations", heading_style)
    )

    if report.recommendations:
        for recommendation in report.recommendations:
            story.append(
                Paragraph(
                    f"- {escape(str(recommendation))}",
                    normal_style,
                )
            )
            story.append(Spacer(1, 4))
    else:
        story.append(
            Paragraph("No general recommendations.", normal_style)
        )

    # 6. Failed chunks
    story.append(
        Paragraph("Failed Chunks", heading_style)
    )

    if report.failed_chunks:
        for failed in report.failed_chunks:
            story.append(
                Paragraph(
                    f"<b>File:</b> {escape(str(failed.file_path))}",
                    normal_style,
                )
            )

            story.append(
                Paragraph(
                    f"<b>Lines:</b> {failed.start_line}-{failed.end_line}",
                    normal_style,
                )
            )

            story.append(
                Paragraph(
                    f"<b>Error:</b> {escape(str(failed.error))}",
                    normal_style,
                )
            )

            story.append(Spacer(1, 7))
    else:
        story.append(
            Paragraph("No failed chunks.", normal_style)
        )

    # 7. Analysis warnings
    story.append(
        Paragraph("Analysis Warnings", heading_style)
    )

    if report.warnings:
        for warning in report.warnings:
            story.append(
                Paragraph(
                    f"- {escape(str(warning))}",
                    normal_style,
                )
            )
    else:
        story.append(
            Paragraph("No analysis warnings.", normal_style)
        )

    # Build PDF
    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes