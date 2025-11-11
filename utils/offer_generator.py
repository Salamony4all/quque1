import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import json
from datetime import datetime
import re

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
        
        # Tables with images
        for idx, table_data in enumerate(costed_data['tables']):
            header = Paragraph(f"<b>Item List {idx + 1}</b>", self.header_style)
            story.append(header)
            story.append(Spacer(1, 0.2*inch))
            
            # Get session and file info for images
            session_id = session['session_id']
            file_info = None
            uploaded_files = session.get('uploaded_files', [])
            for f in uploaded_files:
                if f['id'] == file_id:
                    file_info = f
                    break
            
            # Prepare table data with images
            table_rows = []
            
            # Headers - clean and format
            headers = table_data['headers']
            header_row = [Paragraph(f"<b>{h}</b>", self.styles['Normal']) for h in headers]
            table_rows.append(header_row)
            
            # Data rows - show only final costed prices with images
            for row in table_data['rows']:
                table_row = []
                
                for h in headers:
                    cell_value = row.get(h, '')
                    
                    # Skip original price fields
                    if '_original' in h:
                        continue
                    
                    # Check if this cell contains an image reference
                    if self.contains_image(cell_value):
                        # Extract image path and create image element
                        image_path = self.extract_image_path(cell_value, session_id, file_id)
                        if image_path and os.path.exists(image_path):
                            try:
                                # Create image with proper sizing
                                img = RLImage(image_path, width=1*inch, height=1*inch)
                                table_row.append(img)
                            except Exception as e:
                                # If image fails, show text instead
                                table_row.append(Paragraph(str(cell_value), self.styles['Normal']))
                        else:
                            table_row.append(Paragraph(str(cell_value), self.styles['Normal']))
                    else:
                        # Regular text cell - use final costed value only
                        final_value = str(cell_value)
                        
                        # Format numbers nicely
                        if self.is_numeric_column(h):
                            try:
                                num_val = float(re.sub(r'[^\d.-]', '', final_value))
                                final_value = f"{num_val:,.2f}"
                            except:
                                pass
                        
                        table_row.append(Paragraph(final_value, self.styles['Normal']))
                
                table_rows.append(table_row)
            
            # Create ReportLab table with appropriate column widths
            col_widths = self.calculate_column_widths(headers, len(headers))
            t = Table(table_rows, colWidths=col_widths, repeatRows=1)
            
            # Enhanced table styling
            table_style = TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 1), (-1, -1), 5),
                ('RIGHTPADDING', (0, 1), (-1, -1), 5),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                
                # Alternating row colors for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ])
            
            t.setStyle(table_style)
            story.append(t)
            story.append(Spacer(1, 0.4*inch))
        
        # Summary with updated VAT (5%)
        summary_header = Paragraph("<b>SUMMARY</b>", self.header_style)
        story.append(summary_header)
        story.append(Spacer(1, 0.2*inch))
        
        # Calculate totals
        subtotal = self.calculate_subtotal(costed_data['tables'])
        vat = subtotal * 0.05  # 5% VAT
        grand_total = subtotal + vat
        
        summary_data = [
            ['Subtotal:', f'{subtotal:,.2f}'],
            ['VAT (5%):', f'{vat:,.2f}'],
            ['', ''],  # Empty row for spacing
            ['Grand Total:', f'{grand_total:,.2f}']
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 2), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 2), 11),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#667eea')),
            ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#667eea')),
            ('TOPPADDING', (0, 3), (-1, 3), 10),
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
                    # Look for total/amount columns, exclude original values
                    if ('total' in key.lower() or 'amount' in key.lower()) and '_original' not in key:
                        try:
                            num_value = float(str(value).replace(',', '').replace('OMR', '').replace('$', '').strip())
                            subtotal += num_value
                        except:
                            pass
        
        return subtotal
    
    def contains_image(self, cell_value):
        """Check if cell contains an image reference"""
        return '<img' in str(cell_value).lower() or 'img_in_' in str(cell_value).lower()
    
    def extract_image_path(self, cell_value, session_id, file_id):
        """Extract image path from cell value"""
        try:
            # Look for img src pattern
            import re
            match = re.search(r'src=["\']([^"\']+)["\']', str(cell_value))
            if match:
                img_relative_path = match.group(1)
                # Convert to absolute path
                img_path = os.path.join('outputs', session_id, file_id, img_relative_path)
                return img_path
            
            # Try to find image reference in text
            if 'img_in_' in str(cell_value):
                match = re.search(r'(imgs/img_in_[^"\s<>]+\.jpg)', str(cell_value))
                if match:
                    img_relative_path = match.group(1)
                    img_path = os.path.join('outputs', session_id, file_id, img_relative_path)
                    return img_path
        except Exception as e:
            pass
        
        return None
    
    def is_numeric_column(self, header):
        """Check if column likely contains numeric values"""
        numeric_keywords = ['qty', 'quantity', 'rate', 'price', 'amount', 'total', 'cost']
        return any(keyword in header.lower() for keyword in numeric_keywords)
    
    def calculate_column_widths(self, headers, num_cols):
        """Calculate appropriate column widths based on headers"""
        total_width = 7.5 * inch  # A4 page width minus margins
        
        # Identify column types
        widths = []
        for header in headers:
            h_lower = header.lower()
            if 'si' in h_lower or 'no' in h_lower or '#' in h_lower:
                widths.append(0.5 * inch)  # Serial number - narrow
            elif 'img' in h_lower or 'image' in h_lower or 'ref' in h_lower:
                widths.append(1.2 * inch)  # Image column - wider
            elif 'description' in h_lower or 'item' in h_lower:
                widths.append(2.5 * inch)  # Description - widest
            elif 'qty' in h_lower or 'unit' in h_lower:
                widths.append(0.7 * inch)  # Quantity/Unit - narrow
            elif 'rate' in h_lower or 'price' in h_lower:
                widths.append(1.0 * inch)  # Rate - medium
            elif 'amount' in h_lower or 'total' in h_lower:
                widths.append(1.1 * inch)  # Total - medium
            else:
                widths.append(1.0 * inch)  # Default
        
        # Normalize to fit total width
        current_total = sum(widths)
        if current_total > total_width:
            scale_factor = total_width / current_total
            widths = [w * scale_factor for w in widths]
        
        return widths
