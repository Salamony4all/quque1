import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

class MASGenerator:
    """Generate Material Approval Sheets (MAS) with company template"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for MAS"""
        self.title_style = ParagraphStyle(
            'MASTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.header_style = ParagraphStyle(
            'MASHeader',
            fontSize=12,
            textColor=colors.black,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'MASNormal',
            fontSize=10,
            textColor=colors.black
        )
    
    def generate(self, file_id, session):
        """
        Generate Material Approval Sheet
        Returns: path to generated PDF
        """
        # Get file info and extracted data
        uploaded_files = session.get('uploaded_files', [])
        file_info = None
        
        for f in uploaded_files:
            if f['id'] == file_id:
                file_info = f
                break
        
        if not file_info or 'extraction_result' not in file_info:
            raise Exception('Extraction result not found. Please extract tables first.')
        
        extraction_result = file_info['extraction_result']
        
        # Parse items from extraction
        items = self.parse_items(extraction_result)
        
        # Create output directory
        session_id = session['session_id']
        output_dir = os.path.join('outputs', session_id, 'mas')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF
        output_file = os.path.join(output_dir, f'mas_{file_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                                topMargin=0.75*inch, bottomMargin=0.75*inch,
                                leftMargin=0.75*inch, rightMargin=0.75*inch)
        story = []
        
        # Company header
        story.extend(self.create_header())
        
        # MAS Title
        title = Paragraph("MATERIAL APPROVAL SHEET", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Project information
        story.extend(self.create_project_info())
        story.append(Spacer(1, 0.3*inch))
        
        # Create MAS table for each item
        for idx, item in enumerate(items):
            if idx > 0:
                story.append(PageBreak())
            story.extend(self.create_mas_item(item, idx + 1))
        
        # Build PDF
        doc.build(story)
        
        return output_file
    
    def create_header(self):
        """Create company header for MAS"""
        story = []
        
        # Company logo placeholder and info
        header_data = [
            ['[LOGO]', 'Your Company Name\nAddress Line 1\nAddress Line 2\nTel: +XXX XXX XXXX\nEmail: info@company.com']
        ]
        
        header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Horizontal line
        line_data = [['_' * 100]]
        line_table = Table(line_data, colWidths=[6.5*inch])
        story.append(line_table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def create_project_info(self):
        """Create project information section"""
        story = []
        
        project_data = [
            ['Project Name:', '[Project Name]', 'MAS No:', 'MAS-001'],
            ['Client:', '[Client Name]', 'Date:', datetime.now().strftime('%d/%m/%Y')],
            ['Location:', '[Project Location]', 'Rev:', '00'],
        ]
        
        project_table = Table(project_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
        project_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(project_table)
        
        return story
    
    def create_mas_item(self, item, item_num):
        """Create MAS entry for one item"""
        story = []
        
        # Item title
        item_title = Paragraph(f"<b>Item {item_num}: {item.get('description', 'N/A')}</b>", self.header_style)
        story.append(item_title)
        story.append(Spacer(1, 0.15*inch))
        
        # Item details table
        details_data = [
            ['Item Description:', item.get('description', 'N/A')],
            ['Brand/Manufacturer:', item.get('brand', 'N/A')],
            ['Model/Reference:', item.get('model', 'N/A')],
            ['Quantity:', f"{item.get('qty', 'N/A')} {item.get('unit', '')}"],
            ['Finish/Color:', item.get('finish', 'As specified')],
            ['Dimensions:', item.get('dimensions', 'As per manufacturer')],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Image placeholder
        image_section = Paragraph(
            '<para align="center"><b>[Product Image/Technical Drawing]</b><br/>'
            'Image will be embedded here<br/>'
            f'{item.get("image", "No image available")}</para>',
            self.normal_style
        )
        story.append(image_section)
        story.append(Spacer(1, 0.2*inch))
        
        # Specifications
        spec_title = Paragraph('<b>Technical Specifications:</b>', self.header_style)
        story.append(spec_title)
        story.append(Spacer(1, 0.1*inch))
        
        specifications = item.get('specifications', [])
        if specifications:
            for spec in specifications:
                spec_para = Paragraph(f"• {spec}", self.normal_style)
                story.append(spec_para)
                story.append(Spacer(1, 0.05*inch))
        else:
            story.append(Paragraph('• As per manufacturer standard specifications', self.normal_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Approval section
        approval_data = [
            ['Submitted By:', '', 'Date:', ''],
            ['', '', '', ''],
            ['Approved By:', '', 'Date:', ''],
            ['', '', '', ''],
        ]
        
        approval_table = Table(approval_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1.5*inch])
        approval_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 2), (2, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (1, 1), (1, 1), 1, colors.black),
            ('LINEABOVE', (3, 1), (3, 1), 1, colors.black),
            ('LINEABOVE', (1, 3), (1, 3), 1, colors.black),
            ('LINEABOVE', (3, 3), (3, 3), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))
        
        story.append(approval_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Remarks
        remarks = Paragraph('<b>Remarks:</b> _________________________________', self.normal_style)
        story.append(remarks)
        
        return story
    
    def parse_items(self, extraction_result):
        """Parse items from extraction result"""
        items = []
        
        for layout_result in extraction_result.get('layoutParsingResults', []):
            markdown_text = layout_result.get('markdown', {}).get('text', '')
            images = layout_result.get('markdown', {}).get('images', {})
            
            # Parse tables
            rows = self.extract_table_rows(markdown_text)
            
            for row in rows:
                item = {
                    'description': row.get('description', row.get('item', 'N/A')),
                    'qty': row.get('qty', row.get('quantity', 'N/A')),
                    'unit': row.get('unit', ''),
                    'brand': self.extract_brand(row.get('description', '')),
                    'model': 'As specified',
                    'finish': 'As specified',
                    'dimensions': self.extract_dimensions(row.get('description', '')),
                    'specifications': self.extract_specifications(row.get('description', '')),
                    'image': list(images.values())[0] if images else None
                }
                items.append(item)
        
        return items
    
    def extract_table_rows(self, markdown_text):
        """Extract table rows from markdown"""
        lines = markdown_text.split('\n')
        rows = []
        headers = []
        
        for line in lines:
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                
                if not headers and cells:
                    headers = [h.lower() for h in cells]
                elif headers and cells and not all(c in '-: ' for c in ''.join(cells)):
                    if len(cells) == len(headers):
                        row = dict(zip(headers, cells))
                        rows.append(row)
        
        return rows
    
    def extract_brand(self, description):
        """Extract brand from description"""
        brands = ['Sedus', 'Narbutas', 'Sokoa', 'B&T', 'Herman Miller', 'Steelcase']
        for brand in brands:
            if brand.lower() in description.lower():
                return brand
        
        words = description.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                return word
        
        return 'To be specified'
    
    def extract_dimensions(self, description):
        """Extract dimensions from description"""
        import re
        pattern = r'\d+\s*[xX×]\s*\d+\s*[xX×]?\s*\d*\s*(mm|cm|m|inch|in)'
        match = re.search(pattern, description)
        return match.group(0) if match else 'As per manufacturer'
    
    def extract_specifications(self, description):
        """Extract specifications from description"""
        specs = []
        
        # Basic specifications
        specs.append('Material: As specified in description')
        specs.append('Finish: Factory standard or as specified')
        specs.append('Color: As per approved sample')
        specs.append('Warranty: Manufacturer standard warranty')
        
        return specs
