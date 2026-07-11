import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pandas as pd
from datetime import datetime

def generate_audit_report(G, contaminated_batches, affected_nodes, output_path="audit_report.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1A73E8'), spaceAfter=20)
    story.append(Paragraph("SupplyShield AI - Audit Report", title_style))
    
    # Date
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=12, textColor=colors.gray, spaceAfter=20)
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    
    # Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    summary_text = f"This report provides an overview of the current supply chain risk status. " \
                   f"There are currently {len(contaminated_batches)} contaminated batches detected, " \
                   f"affecting a total of {len(affected_nodes)} downstream facilities and products in the network."
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Contaminated Batches
    story.append(Paragraph("Contamination Alerts (Active)", styles['Heading2']))
    if contaminated_batches:
        for batch in contaminated_batches:
            story.append(Paragraph(f"• Batch ID: {batch} (Status: Critical Risk)", styles['Normal']))
    else:
        story.append(Paragraph("No active contamination alerts.", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Affected Nodes Table
    story.append(Paragraph("Affected Facilities & Products (Blast Radius)", styles['Heading2']))
    if affected_nodes:
        table_data = [["Node ID", "Type", "Name/Location", "Required Action"]]
        for node in list(affected_nodes)[:30]: # Limit to 30 for the PDF
            data = G.nodes[node]
            node_type = data.get('type', 'Unknown')
            name = data.get('label', 'N/A')
            action = "Stop Sale / Destroy" if node_type == 'Product' else "Sanitize / Quarantine"
            table_data.append([node, node_type, name, action])
            
        t = Table(table_data, colWidths=[100, 120, 150, 130])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A73E8')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9FA')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#DADCE0'))
        ]))
        story.append(t)
        
        if len(affected_nodes) > 30:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"...and {len(affected_nodes) - 30} more nodes. See dashboard for full list.", styles['Italic']))
    else:
        story.append(Paragraph("No facilities currently affected.", styles['Normal']))
        
    # Build PDF
    doc.build(story)
    return output_path
