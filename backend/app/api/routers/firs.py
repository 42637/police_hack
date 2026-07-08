from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.database.session import get_database
from app.api.deps import get_admin_user
from app.models.fir import FIRResponse
from bson import ObjectId
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

router = APIRouter(prefix="/firs", tags=["FIR Records"])

def generate_fir_pdf_bytes(fir: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'FIRTitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12,
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'FIRSubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    h2_style = ParagraphStyle(
        'FIRH2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=14,
        spaceAfter=8,
        borderPadding=4
    )
    
    label_style = ParagraphStyle(
        'FIRLabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#334155')
    )
    
    value_style = ParagraphStyle(
        'FIRValueStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#0F172A')
    )
    
    crime_banner_style = ParagraphStyle(
        'FIRCrimeBannerStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#B91C1C') # Red Crimson
    )

    story = []
    
    # 1. Header/Seal area
    story.append(Paragraph("FIRST INFORMATION REPORT", title_style))
    story.append(Paragraph("Registered under Section 154 Cr.P.C // PRAKASAM POLICE DEPARTMENT IT DIVISION", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 2. Main metadata table (FIR Num, Date, Location)
    reported_date_str = fir["reported_date"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(fir["reported_date"], "strftime") else str(fir["reported_date"])
    meta_data = [
        [Paragraph("FIR NUMBER:", label_style), Paragraph(fir["fir_number"], ParagraphStyle('boldval', parent=value_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#0F172A'))),
         Paragraph("DATE REGISTERED:", label_style), Paragraph(reported_date_str, value_style)],
        [Paragraph("INCIDENT LOCATION:", label_style), Paragraph(fir["location"], value_style),
         Paragraph("STATUS:", label_style), Paragraph(fir["status"], ParagraphStyle('greenval', parent=value_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#16A34A')))]
    ]
    t1 = Table(meta_data, colWidths=[1.5*inch, 2.0*inch, 1.5*inch, 2.0*inch])
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # 3. Offense Description
    story.append(Paragraph("Offense Registration & Sections of Law", h2_style))
    offense_data = [
        [Paragraph("PRIMARY OFFENSE:", label_style), Paragraph(fir["offense"], crime_banner_style)],
        [Paragraph("APPLICABLE SECTIONS:", label_style), Paragraph(fir["sections"], value_style)],
        [Paragraph("RISK LEVEL FLAGGED:", label_style), Paragraph(f"{fir['risk_level']} (Threat Index: {fir['risk_score']}%)", ParagraphStyle('riskval', parent=value_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#B91C1C') if fir['risk_level'] in ['Critical', 'High'] else colors.HexColor('#CA8A04')))]
    ]
    t2 = Table(offense_data, colWidths=[1.8*inch, 5.2*inch])
    t2.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))
    
    # 4. Registered Vehicle Details
    story.append(Paragraph("Registered Vehicle Registry Details", h2_style))
    vehicle_data = [
        [Paragraph("REGISTRATION NUMBER:", label_style), Paragraph(fir["registration_number"], ParagraphStyle('regbold', parent=value_style, fontName='Helvetica-Bold')),
         Paragraph("REGISTERED OWNER:", label_style), Paragraph(fir["owner_name"], value_style)],
        [Paragraph("VEHICLE BRAND:", label_style), Paragraph(fir["vehicle_brand"], value_style),
         Paragraph("VEHICLE MODEL:", label_style), Paragraph(fir["vehicle_model"], value_style)],
        [Paragraph("VEHICLE COLOR:", label_style), Paragraph(fir["vehicle_color"], value_style),
         Paragraph("VEHICLE TYPE:", label_style), Paragraph(fir.get("vehicle_type", "car").upper(), value_style)]
    ]
    t3 = Table(vehicle_data, colWidths=[1.8*inch, 1.7*inch, 1.5*inch, 2.0*inch])
    t3.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F8FAFC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t3)
    story.append(Spacer(1, 30))
    
    # 5. Officer Notes & Signature Lines
    story.append(Paragraph("Police Department Verification Check", h2_style))
    desc_p = Paragraph(
        "This document constitutes a digitally-generated First Information Report (FIR) created automatically "
        "by the Sentinel AI cyber-physical traffic control node. The machine learning pipeline detected a visual "
        "or spatial cloning mismatch (impossible speed or physical model mismatch). "
        "This record is locked under state police evidence collection protocols.",
        ParagraphStyle('descp', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor('#475569'))
    )
    story.append(desc_p)
    story.append(Spacer(1, 40))
    
    sig_data = [
        [Paragraph("_____________________________<br/>Assigned Investigating Officer", ParagraphStyle('sig1', parent=label_style, alignment=0)),
         Paragraph("_____________________________<br/>IT Division Supervisor Stamp", ParagraphStyle('sig2', parent=label_style, alignment=2))]
    ]
    t4 = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
    t4.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t4)
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

@router.get("", response_model=list[FIRResponse])
async def list_firs(
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    cursor = db.firs.find({}).sort("reported_date", -1)
    firs = []
    async for f in cursor:
        f["_id"] = str(f["_id"])
        firs.append(f)
    return firs

@router.get("/{fir_id}/pdf")
async def download_fir_pdf(
    fir_id: str,
    db = Depends(get_database),
    current_user = Depends(get_admin_user)
):
    try:
        oid = ObjectId(fir_id)
        fir = await db.firs.find_one({"_id": oid})
    except Exception:
        fir = await db.firs.find_one({"_id": fir_id})

    if not fir:
        # Fall back lookup by fir_number
        fir = await db.firs.find_one({"fir_number": fir_id})
        
    if not fir:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FIR record not found."
        )
        
    pdf_content = generate_fir_pdf_bytes(fir)
    
    return StreamingResponse(
        BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=FIR_{fir['fir_number']}.pdf"
        }
    )
