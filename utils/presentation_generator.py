import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import re

class PresentationGenerator:
    """Generate eye-catching technical presentations - 1 page per item"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for presentations"""
        self.title_style = ParagraphStyle(
            'PresentationTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.item_title_style = ParagraphStyle(
            'ItemTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.spec_heading_style = ParagraphStyle(
            'SpecHeading',
            fontSize=14,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        self.spec_text_style = ParagraphStyle(
            'SpecText',
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
    
    def generate(self, file_id, session):
        """
        Generate technical presentation with 1 page per item
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
        
        # Parse tables to get items
        items = self.parse_items_from_extraction(extraction_result)
        
        # Create output directory
        session_id = session['session_id']
        output_dir = os.path.join('outputs', session_id, 'presentations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF
        output_file = os.path.join(output_dir, f'presentation_{file_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        
        doc = SimpleDocTemplate(output_file, pagesize=A4, 
                                topMargin=0.5*inch, bottomMargin=0.5*inch,
                                leftMargin=0.75*inch, rightMargin=0.75*inch)
        story = []
        
        # Cover page
        story.extend(self.create_cover_page())
        story.append(PageBreak())
        
        # Create one page per item
        for idx, item in enumerate(items):
            story.extend(self.create_item_page(item, idx + 1))
            if idx < len(items) - 1:
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        return output_file
    
    def parse_items_from_extraction(self, extraction_result):
        """
        Parse individual items from extraction result
        Returns: list of item dictionaries
        """
        items = []
        
        for layout_result in extraction_result.get('layoutParsingResults', []):
            markdown_text = layout_result.get('markdown', {}).get('text', '')
            images = layout_result.get('markdown', {}).get('images', {})
            
            # Parse tables from markdown
            table_rows = self.extract_table_rows(markdown_text)
            
            for row in table_rows:
                item = {
                    'sn': row.get('sn', row.get('sl.no', '')),
                    'description': row.get('description', row.get('item', '')),
                    'qty': row.get('qty', row.get('quantity', '')),
                    'unit': row.get('unit', ''),
                    'unit_rate': row.get('unit rate', row.get('unit price', row.get('rate', ''))),
                    'total': row.get('total', row.get('amount', '')),
                    'image': self.find_item_image(row, images),
                    'brand': self.extract_brand(row.get('description', '')),
                    'specifications': self.extract_specifications(row.get('description', ''))
                }
                items.append(item)
        
        return items
    
    def extract_table_rows(self, markdown_text):
        """Extract table rows from markdown text"""
        lines = markdown_text.split('\n')
        rows = []
        headers = []
        
        for line in lines:
            if '|' in line:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                
                if not headers and cells:
                    # First row is headers
                    headers = [h.lower() for h in cells]
                elif headers and cells and not all(c in '-: ' for c in ''.join(cells)):
                    # Data row
                    if len(cells) == len(headers):
                        row = dict(zip(headers, cells))
                        rows.append(row)
        
        return rows
    
    def find_item_image(self, row, images):
        """Find image associated with this item"""
        # Try to find image reference in row
        for key, value in row.items():
            if 'image' in key.lower():
                # Check if value references an image
                for img_path, img_url in images.items():
                    if value in img_path or img_path in value:
                        return img_url
        
        # Return first available image if no specific match
        if images:
            return list(images.values())[0]
        
        return None
    
    def extract_brand(self, description):
        """Extract brand name from description (simple heuristic)"""
        # Common brand patterns - this is simplified
        brands = ['Sedus', 'Narbutas', 'Sokoa', 'B&T', 'Herman Miller', 'Steelcase', 'Haworth', 'Knoll']
        
        for brand in brands:
            if brand.lower() in description.lower():
                return brand
        
        # Try to extract first capitalized word
        words = description.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                return word
        
        return 'Premium Brand'
    
    def extract_specifications(self, description):
        """Extract specifications from description"""
        # Split description into bullet points
        specs = []
        
        # Look for dimensions
        dimension_pattern = r'\d+\s*[xX×]\s*\d+\s*[xX×]?\s*\d*\s*(mm|cm|m|inch|in|")'
        dimensions = re.findall(dimension_pattern, description)
        if dimensions:
            specs.append(f"Dimensions: {', '.join(dimensions)}")
        
        # Look for materials
        materials = ['wood', 'metal', 'steel', 'aluminum', 'fabric', 'leather', 'plastic', 'glass', 'laminate']
        found_materials = [mat for mat in materials if mat in description.lower()]
        if found_materials:
            specs.append(f"Materials: {', '.join(found_materials).title()}")
        
        # Look for colors
        colors_list = ['black', 'white', 'grey', 'gray', 'brown', 'blue', 'red', 'green', 'beige']
        found_colors = [col for col in colors_list if col in description.lower()]
        if found_colors:
            specs.append(f"Available Colors: {', '.join(found_colors).title()}")
        
        if not specs:
            # Use description as-is if no specific specs found
            specs.append(description[:200])
        
        return specs
    
    def create_cover_page(self):
        """Create presentation cover page"""
        story = []
        
        # Title
        title = Paragraph("TECHNICAL PROPOSAL", self.title_style)
        story.append(Spacer(1, 2*inch))
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            alignment=TA_CENTER
        )
        subtitle = Paragraph("Furniture, Fixtures & Equipment", subtitle_style)
        story.append(subtitle)
        story.append(Spacer(1, 1*inch))
        
        # Company info
        company_info = f"""
            <para align="center">
                <b>Prepared By:</b><br/>
                <font size="14" color="#667eea"><b>Your Company Name</b></font><br/>
                <br/>
                Date: {datetime.now().strftime('%B %d, %Y')}<br/>
            </para>
        """
        story.append(Paragraph(company_info, self.styles['Normal']))
        
        return story
    
    def create_item_page(self, item, page_num):
        """Create one page for an item with eye-catching design"""
        story = []
        
        # Item number and title
        item_title = f"Item {page_num}: {item['description'][:60]}"
        story.append(Paragraph(item_title, self.item_title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Create two-column layout using table
        left_content = []
        right_content = []
        
        # Left column - Image
        if item['image']:
            try:
                # For now, placeholder - in production, download and embed image
                img_placeholder = Paragraph(
                    f'<para align="center"><b>[Product Image]</b><br/>{item["image"][:50]}...</para>',
                    self.styles['Normal']
                )
                left_content.append(img_placeholder)
            except:
                left_content.append(Paragraph('[Image Not Available]', self.styles['Normal']))
        else:
            left_content.append(Paragraph('[Image Not Available]', self.styles['Normal']))
        
        # Right column - Specifications
        specs_html = f"""
            <para>
                <b><font size="14" color="#667eea">Product Details</font></b><br/>
                <br/>
                <b>Brand:</b> {item['brand']}<br/>
                <b>Quantity:</b> {item['qty']} {item['unit']}<br/>
                <b>Unit Rate:</b> {item['unit_rate']}<br/>
                <b>Total Amount:</b> {item['total']}<br/>
                <br/>
                <b><font color="#667eea">Specifications:</font></b><br/>
            </para>
        """
        right_content.append(Paragraph(specs_html, self.spec_text_style))
        
        # Add specifications as bullet points
        for spec in item['specifications']:
            spec_bullet = f"• {spec}"
            right_content.append(Paragraph(spec_bullet, self.spec_text_style))
            right_content.append(Spacer(1, 0.1*inch))
        
        # Additional info
        additional_info = """
            <para>
                <br/>
                <b><font color="#667eea">Additional Information:</font></b><br/>
                • Country of Origin: Various<br/>
                • Warranty: As per manufacturer standard<br/>
                • Lead Time: 4-6 weeks<br/>
                • Finish: As specified or equivalent<br/>
            </para>
        """
        right_content.append(Paragraph(additional_info, self.spec_text_style))
        
        # Create two-column table
        data = [[left_content, right_content]]
        
        col_widths = [3*inch, 3.5*inch]
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Bottom section - Key features
        features_title = Paragraph('<b><font size="12" color="#667eea">KEY FEATURES</font></b>', self.styles['Normal'])
        story.append(features_title)
        story.append(Spacer(1, 0.1*inch))
        
        features = [
            "✓ Premium quality construction",
            "✓ Modern ergonomic design",
            "✓ Environmentally friendly materials",
            "✓ Easy maintenance and durability"
        ]
        
        features_text = '<br/>'.join(features)
        story.append(Paragraph(features_text, self.spec_text_style))
        
        return story
