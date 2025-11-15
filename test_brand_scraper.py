"""
Test script for brand scraper functionality
"""

from utils.brand_scraper import BrandScraper
import json

def test_scraper():
    """Test the brand scraper with a real website"""
    
    scraper = BrandScraper()
    
    # Test with a furniture brand
    test_brands = [
        {
            'name': 'IKEA',
            'website': 'https://www.ikea.com'
        },
        {
            'name': 'Steelcase',
            'website': 'https://www.steelcase.com'
        }
    ]
    
    for brand in test_brands:
        print(f"\n{'='*60}")
        print(f"Testing: {brand['name']}")
        print(f"Website: {brand['website']}")
        print('='*60)
        
        try:
            # Check robots.txt
            allowed = scraper.check_robots_allowed(brand['website'])
            print(f"Robots.txt allows scraping: {allowed}")
            
            if allowed:
                # Scrape the website
                print("\nStarting scrape...")
                result = scraper.scrape_brand_website(brand['website'], brand['name'])
                
                if 'error' in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"\nResults:")
                    print(f"- Categories found: {len(result.get('categories', {}))}")
                    print(f"- Products found: {len(result.get('products', []))}")
                    
                    # Show sample category
                    if result.get('categories'):
                        cat_name = list(result['categories'].keys())[0]
                        cat_products = result['categories'][cat_name]
                        print(f"\nSample category: {cat_name}")
                        print(f"  Products: {len(cat_products)}")
                        if cat_products:
                            print(f"  First product: {cat_products[0]}")
                    
                    # Show sample product
                    if result.get('products'):
                        print(f"\nSample product:")
                        print(json.dumps(result['products'][0], indent=2))
            
        except Exception as e:
            print(f"Error testing {brand['name']}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_scraper()
