import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import json
from datetime import datetime

class OfferGenerator:
    """Generate offer documents with costing factors applied"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12
        )
    
    def generate(self, file_id, session):
        """
        Generate offer document
        Returns: path to generated PDF
        """
        # Get file info and costed data
        uploaded_files = session.get('uploaded_files', [])
        file_info = None
        
        for f in uploaded_files:
            if f['id'] == file_id:
                file_info = f
                break
        
        if not file_info or 'costed_data' not in file_info:
            raise Exception('Costed data not found. Please apply costing first.')
        
        costed_data = file_info['costed_data']
        
        # Create output directory
        session_id = session['session_id']
        output_dir = os.path.join('outputs', session_id, 'offers')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF
        output_file = os.path.join(output_dir, f'offer_{file_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("COMMERCIAL OFFER", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Company info (placeholder)
        company_info = Paragraph("""
            <b>Company Name</b><br/>
            Address Line 1<br/>
            Address Line 2<br/>
            Tel: +XXX XXX XXXX<br/>
            Email: info@company.com
        """, self.styles['Normal'])
        story.append(company_info)
        story.append(Spacer(1, 0.3*inch))
        
        # Date
        date_text = Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 0.5*inch))
        
        # Costing factors applied
        factors = costed_data['factors']
        factors_text = f"""
            <b>Costing Factors Applied:</b><br/>
            Net Margin: {factors.get('net_margin', 0)}%<br/>
            Freight: {factors.get('freight', 0)}%<br/>
            Customs: {factors.get('customs', 0)}%<br/>
            Installation: {factors.get('installation', 0)}%<br/>
            Exchange Rate: {factors.get('exchange_rate', 1.0)}<br/>
            Additional: {factors.get('additional', 0)}%
        """
        story.append(Paragraph(factors_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Tables
        for idx, table_data in enumerate(costed_data['tables']):
            header = Paragraph(f"Item List {idx + 1}", self.header_style)
            story.append(header)
            
            # Create table
            table_rows = []
            
            # Headers
            table_rows.append(table_data['headers'])
            
            # Data rows
            for row in table_data['rows']:
                table_row = [row.get(h, '') for h in table_data['headers']]
                table_rows.append(table_row)
            
            # Create ReportLab table
            t = Table(table_rows, repeatRows=1)
            
            # Style the table
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            t.setStyle(table_style)
            story.append(t)
            story.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_header = Paragraph("SUMMARY", self.header_style)
        story.append(summary_header)
        
        # Calculate totals
        subtotal = self.calculate_subtotal(costed_data['tables'])
        vat = subtotal * 0.15
        grand_total = subtotal + vat
        
        summary_data = [
            ['Subtotal:', f'{subtotal:.2f}'],
            ['VAT (15%):', f'{vat:.2f}'],
            ['<b>Grand Total:</b>', f'<b>{grand_total:.2f}</b>']
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_style = TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ])
        summary_table.setStyle(summary_style)
        story.append(summary_table)
        
        # Terms and conditions
        story.append(Spacer(1, 0.5*inch))
        terms = Paragraph("""
            <b>Terms and Conditions:</b><br/>
            1. Prices are valid for 30 days from the date of this offer.<br/>
            2. Delivery time: 4-6 weeks from order confirmation.<br/>
            3. Payment terms: 50% advance, 50% before delivery.<br/>
            4. Warranty: As per manufacturer's warranty.<br/>
        """, self.styles['Normal'])
        story.append(terms)
        
        # Build PDF
        doc.build(story)
        
        return output_file
    
    def calculate_subtotal(self, tables):
        """Calculate subtotal from all tables"""
        subtotal = 0.0
        
        for table in tables:
            for row in table['rows']:
                for key, value in row.items():
                    if 'total' in key.lower() and '_original' not in key:
                        try:
                            num_value = float(str(value).replace(',', ''))
                            subtotal += num_value
                        except:
                            pass
        
        return subtotal
