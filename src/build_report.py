
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
CHARTS = REPORTS / "charts"
OUTPUT = REPORTS / "olist_weekly_business_review.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverTitle",
    parent=styles["Title"],
    fontSize=25,
    leading=30,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#17324D"),
    spaceAfter=8 * mm,
))
styles.add(ParagraphStyle(
    name="SectionHeading",
    parent=styles["Heading1"],
    fontSize=17,
    leading=21,
    textColor=colors.HexColor("#17324D"),
    spaceAfter=4 * mm,
))
styles.add(ParagraphStyle(
    name="SubHeading",
    parent=styles["Heading2"],
    fontSize=11,
    leading=14,
    textColor=colors.HexColor("#276678"),
    spaceBefore=3 * mm,
    spaceAfter=2 * mm,
))
styles.add(ParagraphStyle(
    name="BodyCompact",
    parent=styles["BodyText"],
    fontSize=9,
    leading=13,
    spaceAfter=2.5 * mm,
))
styles.add(ParagraphStyle(
    name="SmallNote",
    parent=styles["BodyText"],
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor("#555555"),
))
styles.add(ParagraphStyle(
    name="MetricValue",
    parent=styles["BodyText"],
    fontSize=15,
    leading=18,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#17324D"),
))
styles.add(ParagraphStyle(
    name="MetricLabel",
    parent=styles["BodyText"],
    fontSize=8,
    leading=10,
    alignment=TA_CENTER,
))


def paragraph(text, style="BodyCompact"):
    return Paragraph(text, styles[style])


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D7E0E8"))
    canvas.line(15 * mm, 13 * mm, PAGE_WIDTH - 15 * mm, 13 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(15 * mm, 8 * mm, "Olist Marketplace | Historical dataset analysis")
    canvas.drawRightString(
        PAGE_WIDTH - 15 * mm,
        8 * mm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def chart(path, width, height):
    if not path.exists():
        raise FileNotFoundError(f"Missing chart: {path}")
    return Image(str(path), width=width, height=height, kind="proportional")


def metric_card(label, value):
    table = Table(
        [
            [paragraph(value, "MetricValue")],
            [paragraph(label, "MetricLabel")],
        ],
        colWidths=[40 * mm],
        rowHeights=[12 * mm, 10 * mm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F8")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D7E0E8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def build():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=19 * mm,
        title="Olist Marketplace Business Review",
        author="Analytics",
    )

    story = []

    # PAGE 1 — Executive summary and scorecard
    story.append(Spacer(1, 8 * mm))
    story.append(paragraph(
        "WEEKLY BUSINESS REVIEW",
        "CoverTitle",
    ))
    story.append(paragraph(
        "Olist Brazilian E-Commerce Marketplace",
        "Heading2",
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(paragraph(
        "Historical dataset review | Revenue, retention, demand, and delivery experience",
        "BodyCompact",
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(paragraph("Executive summary", "SectionHeading"))
    story.append(paragraph(
        "The observed dataset contains <b>R$13.22 million in delivered product "
        "revenue</b> across 24 calendar months. Delivery performance is a notable "
        "customer-experience concern: late-delivered orders averaged "
        "<b>2.57/5</b> in review scores, compared with <b>4.29/5</b> for early "
        "deliveries. This 1.72-point difference supports further investigation "
        "of fulfilment delays.",
    ))

    cards = Table(
        [[
            metric_card("Delivered product revenue", "R$13.22M"),
            metric_card("Repeat-purchase rate", "3.12%"),
        ], [
            metric_card("Late-delivery rate", "8.11%"),
            metric_card("Late-order review score", "2.57 / 5"),
        ]],
        colWidths=[83 * mm, 83 * mm],
        hAlign="LEFT",
    )
    cards.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    story.append(cards)
    story.append(Spacer(1, 5 * mm))

    story.append(paragraph("North Star and supporting metrics", "SectionHeading"))
    kpi_rows = [
        ["Metric", "Definition / interpretation"],
        ["North Star: delivered product revenue",
         "Sum of item prices for delivered orders; freight excluded."],
        ["Order demand",
         "Daily order count and seven-calendar-day rolling average."],
        ["Repeat-purchase rate",
         "Unique customers with at least two distinct orders ÷ all unique customers."],
        ["Late-delivery rate",
         "Late delivered orders ÷ delivered orders with a valid delivery delay."],
        ["Customer satisfaction",
         "Average review score by delivery-performance group."],
    ]
    kpi_table = Table(
        [[paragraph(str(cell), "SmallNote") for cell in row] for row in kpi_rows],
        colWidths=[48 * mm, 118 * mm],
        repeatRows=1,
    )
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E0E8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(kpi_table)
    story.append(PageBreak())

    # PAGE 2 — Revenue and category performance
    story.append(paragraph("Commercial performance", "SectionHeading"))
    story.append(paragraph(
        "Delivered product revenue is the primary outcome metric. The category "
        "chart highlights the leading product category in each of the ten "
        "highest-revenue customer states.",
    ))
    story.append(chart(
        CHARTS / "01_monthly_revenue.png",
        175 * mm,
        84 * mm,
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(chart(
        CHARTS / "02_top_categories_by_state.png",
        175 * mm,
        106 * mm,
    ))
    story.append(PageBreak())

    # PAGE 3 — Demand and delivery experience
    story.append(paragraph("Demand and customer experience", "SectionHeading"))
    story.append(paragraph(
        "The rolling average smooths day-to-day demand fluctuations. The "
        "delivery comparison indicates a strong association between lateness "
        "and lower review scores; it does not establish causation.",
    ))
    story.append(chart(
        CHARTS / "03_rolling_7day_orders.png",
        175 * mm,
        88 * mm,
    ))
    story.append(Spacer(1, 5 * mm))
    story.append(chart(
        CHARTS / "04_delivery_reviews.png",
        145 * mm,
        91 * mm,
    ))
    story.append(PageBreak())

    # PAGE 4 — VP memo and methodology
    story.append(paragraph("VP memo: decisions and next actions", "SectionHeading"))
    story.append(paragraph("Key finding", "SubHeading"))
    story.append(paragraph(
        "Late-delivered orders averaged <b>2.57/5</b>, compared with "
        "<b>4.29/5</b> for early deliveries. The late-delivery rate was "
        "<b>8.11%</b> among 96,470 delivered orders with valid delay data.",
    ))
    story.append(paragraph("Recommended actions", "SubHeading"))
    story.append(paragraph(
        "<b>1. Investigate delivery drivers.</b> Segment delays by seller, "
        "customer state, product category, and estimated lead time."
    ))
    story.append(paragraph(
        "<b>2. Prioritize at-risk shipments.</b> Test proactive monitoring "
        "and escalation for orders approaching their estimated delivery date."
    ))
    story.append(paragraph(
        "<b>3. Improve repeat purchasing.</b> Investigate barriers to repeat "
        "orders and test post-purchase retention initiatives."
    ))
    story.append(paragraph(
        "<b>4. Review trade-offs monthly.</b> Track delivered product revenue "
        "alongside late-delivery rate and customer review score."
    ))
    story.append(paragraph("Methodology and limitations", "SubHeading"))
    story.append(paragraph(
        "Revenue is the sum of item prices for delivered orders, excluding "
        "freight. Repeat purchase uses customer_unique_id and counts distinct "
        "orders; the observed rate is 3.12%. Delivery analysis excludes "
        "delivered orders without a calculable delay. The source dataset is "
        "historical and may not represent current performance. The relationship "
        "between delivery timing and review score is observational."
    ))
    story.append(paragraph(
        "Data quality: 789 duplicated review-ID groups and two payment records "
        "with zero installments were retained as documented warnings; these "
        "records were not silently removed or altered. Product weights missing "
        "in two rows remain NULL.",
        "SmallNote",
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(paragraph(
        "Decision requested: prioritize a targeted delivery-performance "
        "investigation and report back with seller/state-level drivers and "
        "a measurable improvement plan.",
    ))

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer,
    )

    print(f"PDF created: {OUTPUT}")
    print(f"PDF size: {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()

