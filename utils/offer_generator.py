import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.pdfgen import canvas
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
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=12
        )

    def _get_logo_path(self):
        """Return the best available logo path."""
        candidates = [
            os.path.join('static', 'images', 'AlShaya-Logo-color@2x.png'),
            os.path.join('static', 'images', 'LOGO.png'),
            os.path.join('static', 'images', 'al-shaya-logo-white@2x.png')
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    def _draw_header_footer(self, canv: canvas.Canvas, doc):
        """Draw top-right logo and footer on every page."""
        page_width, page_height = doc.pagesize
        gold = colors.HexColor('#d4af37')
        dark = colors.HexColor('#1a365d')

        # Top separator line
        canv.setStrokeColor(gold)
        canv.setLineWidth(2)
        canv.line(doc.leftMargin, page_height - doc.topMargin + 10, page_width - doc.rightMargin, page_height - doc.topMargin + 10)

        # Logo top-right
        logo_path = self._get_logo_path()
        if logo_path and os.path.exists(logo_path):
            try:
                logo_w = 100  # px points
                logo_h = 100
                x = page_width - doc.rightMargin - logo_w
                y = page_height - doc.topMargin + 14
                canv.drawImage(logo_path, x, y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        # Footer website
        canv.setFillColor(dark)
        canv.setFont('Helvetica', 9)
        footer_text = 'https://alshayaenterprises.com'
        canv.drawRightString(page_width - doc.rightMargin, doc.bottomMargin - 12, footer_text)
        canv.setStrokeColor(gold)
        canv.setLineWidth(1)
        canv.line(doc.leftMargin, doc.bottomMargin - 8, page_width - doc.rightMargin, doc.bottomMargin - 8)
    
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
        
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                    topMargin=0.6*inch, bottomMargin=0.6*inch,
                    leftMargin=0.6*inch, rightMargin=0.6*inch)
        story = []
        
        # Title
        title = Paragraph('<font color="#1a365d">COMMERCIAL OFFER</font>', self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Company info (placeholder)
        company_info = Paragraph(
            """
            <b><font color="#1a365d">ALSHAYA ENTERPRISES</font></b><br/>
            <font color="#475569">P.O. Box 4451, Kuwait City</font><br/>
            <font color="#475569">Tel: +965 XXX XXXX | Email: info@alshayaenterprises.com</font>
        """,
            self.styles['Normal'])
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
            header = Paragraph(f"<b><font color='#1a365d'>Item List {idx + 1}</font></b>", self.header_style)
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
            
            # Headers - clean and format, exclude Action column
            headers = table_data['headers']
            # Filter out Action/Actions column
            filtered_headers = [h for h in headers if h.lower() not in ['action', 'actions']]
            header_row = [Paragraph(f"<b>{h}</b>", self.styles['Normal']) for h in filtered_headers]
            table_rows.append(header_row)
            
            # Data rows - show only final costed prices with images
            for row in table_data['rows']:
                table_row = []
                
                for h in filtered_headers:
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
                                # If image fails, show placeholder text
                                table_row.append(Paragraph("[Image]", self.styles['Normal']))
                        else:
                            # Image not found, show placeholder
                            table_row.append(Paragraph("[Image]", self.styles['Normal']))
                    else:
                        # Regular text cell - use final costed value only
                        # Strip any HTML tags that might remain
                        final_value = re.sub(r'<[^>]+>', '', str(cell_value))
                        
                        # Format numbers nicely
                        if self.is_numeric_column(h):
                            try:
                                num_val = float(re.sub(r'[^\d.-]', '', final_value))
                                final_value = f"{num_val:,.2f}"
                            except:
                                pass
                        
                        table_row.append(Paragraph(final_value, self.styles['Normal']))
                
                table_rows.append(table_row)
            
            # Create ReportLab table with appropriate column widths using filtered headers
            col_widths = self.calculate_column_widths(filtered_headers, len(filtered_headers))
            t = Table(table_rows, colWidths=col_widths, repeatRows=1)
            
            # Enhanced table styling
            table_style = TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4af37')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
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
        summary_header = Paragraph("<b><font color='#1a365d'>SUMMARY</font></b>", self.header_style)
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
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#1a365d')),
            ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#d4af37')),
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
        doc.build(story, onFirstPage=self._draw_header_footer, onLaterPages=self._draw_header_footer)
        
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
                # Remove leading slash if present
                img_relative_path = img_relative_path.lstrip('/')
                # Build absolute path from workspace root
                if img_relative_path.startswith('outputs'):
                    img_path = img_relative_path
                else:
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
