import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

class ValueEngineer:
    """Generate value-engineered alternatives using AI product search"""
    
    def __init__(self):
        self.architonic_base_url = "https://www.architonic.com"
        self.budget_multipliers = {
            'budgetary': 0.7,
            'medium': 1.0,
            'high_end': 1.5
        }
    
    def generate_alternatives(self, file_id, budget_option, session):
        """
        Generate value-engineered alternatives for items
        Returns: list of alternatives with pricing
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
        
        # Get costed data if available
        costed_data = file_info.get('costed_data', None)
        
        # Parse items
        items = self.parse_items(extraction_result, costed_data)
        
        # Generate alternatives for each item
        alternatives = []
        for item in items:
            item_alternatives = self.find_alternatives(item, budget_option)
            alternatives.append({
                'original_item': item,
                'alternatives': item_alternatives,
                'budget_option': budget_option
            })
        
        # Store alternatives in session
        file_info['value_engineering'] = {
            'budget_option': budget_option,
            'alternatives': alternatives,
            'generated_at': datetime.now().isoformat()
        }
        session.modified = True
        
        return alternatives
    
    def parse_items(self, extraction_result, costed_data=None):
        """Parse items from extraction result"""
        items = []
        
        for layout_result in extraction_result.get('layoutParsingResults', []):
            markdown_text = layout_result.get('markdown', {}).get('text', '')
            
            # Parse tables
            rows = self.extract_table_rows(markdown_text)
            
            for row in rows:
                item = {
                    'description': row.get('description', row.get('item', '')),
                    'qty': self.parse_number(row.get('qty', row.get('quantity', '0'))),
                    'unit': row.get('unit', ''),
                    'unit_rate': self.parse_number(row.get('unit rate', row.get('unit price', row.get('rate', '0')))),
                    'total': self.parse_number(row.get('total', row.get('amount', '0'))),
                    'category': self.categorize_item(row.get('description', ''))
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
    
    def parse_number(self, value):
        """Parse numeric value from string"""
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.-]', '', str(value))
        
        try:
            return float(cleaned)
        except:
            return 0.0
    
    def categorize_item(self, description):
        """Categorize item based on description"""
        description_lower = description.lower()
        
        categories = {
            'seating': ['chair', 'seat', 'sofa', 'bench', 'stool', 'armchair'],
            'tables': ['table', 'desk', 'workstation', 'counter'],
            'storage': ['cabinet', 'drawer', 'shelf', 'cupboard', 'storage', 'locker'],
            'lighting': ['light', 'lamp', 'fixture', 'luminaire'],
            'partitions': ['partition', 'screen', 'divider', 'panel'],
            'accessories': ['accessories', 'decor', 'artwork', 'plant']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def find_alternatives(self, item, budget_option):
        """
        Find alternative products based on budget option
        Uses architonic.com as reference (simplified simulation)
        """
        alternatives = []
        
        # Get budget multiplier
        multiplier = self.budget_multipliers.get(budget_option, 1.0)
        original_price = item['unit_rate']
        target_price = original_price * multiplier
        
        # Simulate finding alternatives (in production, this would scrape/API call)
        # For now, generate simulated alternatives based on budget
        
        if budget_option == 'budgetary':
            alternatives = self.generate_budget_alternatives(item, target_price)
        elif budget_option == 'medium':
            alternatives = self.generate_medium_alternatives(item, target_price)
        else:  # high_end
            alternatives = self.generate_premium_alternatives(item, target_price)
        
        return alternatives
    
    def generate_budget_alternatives(self, item, target_price):
        """Generate budget-friendly alternatives"""
        category = item['category']
        
        # Simulated budget brands
        budget_brands = {
            'seating': ['Ikea Business', 'Office Depot', 'Staples'],
            'tables': ['Ikea Business', 'Office Depot', 'HON'],
            'storage': ['Bisley', 'Ikea Business', 'Office Depot'],
            'lighting': ['Philips', 'Osram', 'Generic LED'],
        }
        
        brands = budget_brands.get(category, ['Budget Brand'])
        
        alternatives = []
        for idx, brand in enumerate(brands[:3]):
            alt = {
                'brand': brand,
                'model': f'{category.title()} Model B{idx+1}',
                'description': f'Budget-friendly {item["description"][:50]} alternative',
                'unit_rate': round(target_price * (0.9 + idx * 0.1), 2),
                'total': round(target_price * item['qty'] * (0.9 + idx * 0.1), 2),
                'specs': [
                    'Basic functionality',
                    'Standard warranty (1 year)',
                    'Limited color options',
                    'Good value for money'
                ],
                'source': 'Simulated - Budget Option',
                'lead_time': '2-3 weeks'
            }
            alternatives.append(alt)
        
        return alternatives
    
    def generate_medium_alternatives(self, item, target_price):
        """Generate medium-range alternatives"""
        category = item['category']
        
        # Simulated medium brands
        medium_brands = {
            'seating': ['Sedus', 'Narbutas', 'Sokoa'],
            'tables': ['Narbutas', 'Sedus', 'Vitra'],
            'storage': ['Bisley', 'Sedus', 'Steelcase'],
            'lighting': ['Artemide', 'Flos', 'Louis Poulsen'],
        }
        
        brands = medium_brands.get(category, ['Medium Brand'])
        
        alternatives = []
        for idx, brand in enumerate(brands[:3]):
            alt = {
                'brand': brand,
                'model': f'{category.title()} Model M{idx+1}',
                'description': f'Mid-range {item["description"][:50]} alternative',
                'unit_rate': round(target_price * (0.95 + idx * 0.05), 2),
                'total': round(target_price * item['qty'] * (0.95 + idx * 0.05), 2),
                'specs': [
                    'Excellent build quality',
                    'Extended warranty (3-5 years)',
                    'Multiple finish options',
                    'Ergonomic design',
                    'Sustainable materials'
                ],
                'source': 'Simulated - Medium Range',
                'lead_time': '4-6 weeks'
            }
            alternatives.append(alt)
        
        return alternatives
    
    def generate_premium_alternatives(self, item, target_price):
        """Generate high-end premium alternatives"""
        category = item['category']
        
        # Simulated premium brands
        premium_brands = {
            'seating': ['Herman Miller', 'Knoll', 'Vitra'],
            'tables': ['Vitra', 'Knoll', 'USM'],
            'storage': ['USM', 'Vitra', 'Walter Knoll'],
            'lighting': ['Flos', 'Artemide', 'Louis Poulsen'],
        }
        
        brands = premium_brands.get(category, ['Premium Brand'])
        
        alternatives = []
        for idx, brand in enumerate(brands[:3]):
            alt = {
                'brand': brand,
                'model': f'{category.title()} Model P{idx+1}',
                'description': f'Premium {item["description"][:50]} alternative',
                'unit_rate': round(target_price * (1.0 + idx * 0.1), 2),
                'total': round(target_price * item['qty'] * (1.0 + idx * 0.1), 2),
                'specs': [
                    'Exceptional craftsmanship',
                    'Lifetime warranty',
                    'Fully customizable',
                    'Award-winning design',
                    'Sustainable & certified',
                    'Premium materials'
                ],
                'source': 'Simulated - Premium Option',
                'lead_time': '6-8 weeks'
            }
            alternatives.append(alt)
        
        return alternatives
    
    def search_architonic(self, query, budget_option):
        """
        Search architonic.com for products (placeholder for future implementation)
        Note: Actual scraping should respect robots.txt and terms of service
        """
        # This is a placeholder - in production, implement proper API or scraping
        # with rate limiting and respect for website policies
        
        try:
            # Simulated search results
            results = {
                'query': query,
                'budget': budget_option,
                'results': [],
                'note': 'This is a simulated search. Implement actual API integration.'
            }
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return {'results': [], 'error': str(e)}
