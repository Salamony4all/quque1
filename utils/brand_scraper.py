"""
Web scraper for furniture brand websites
Extracts product information, images, and descriptions
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import re
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlencode
import urllib.robotparser

logger = logging.getLogger(__name__)


class BrandScraper:
    """Web scraper for furniture brand websites with intelligent product detection"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.rate_limit_delay = 2  # seconds between requests
        
    def scrape_brand_website(self, website: str, brand_name: str) -> Dict:
        """
        Intelligently scrape a brand's website to discover products
        Returns structured data about categories and products
        """
        try:
            logger.info(f"Starting intelligent scrape of {brand_name} ({website})")
            
            # Check robots.txt
            if not self.check_robots_allowed(website):
                logger.warning(f"Scraping not allowed by robots.txt for {website}")
                return {'error': 'Scraping not allowed by robots.txt'}
            
            # Get homepage
            response = self.session.get(website, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Detect website structure
            product_links = self.find_product_pages(soup, website)
            categories = self.detect_categories(soup, website)
            
            products_data = {
                'brand': brand_name,
                'website': website,
                'categories': {},
                'products': []
            }
            
            # Scrape product categories
            for category_name, category_url in categories.items():
                logger.info(f"Scraping category: {category_name}")
                time.sleep(self.rate_limit_delay)
                
                category_products = self.scrape_category_page(category_url, brand_name)
                if category_products:
                    products_data['categories'][category_name] = category_products
            
            # Also scrape direct product links
            for product_url in product_links[:20]:  # Limit to 20 products
                logger.info(f"Scraping product: {product_url}")
                time.sleep(self.rate_limit_delay)
                
                product = self.scrape_product_page(product_url, brand_name)
                if product:
                    products_data['products'].append(product)
            
            return products_data
            
        except Exception as e:
            logger.error(f"Error scraping {brand_name}: {e}")
            return {'error': str(e)}
    
    def find_product_pages(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find product page URLs using various heuristics"""
        product_urls = set()
        
        # Common product URL patterns
        product_patterns = [
            r'/product[s]?/',
            r'/item[s]?/',
            r'/chair[s]?/',
            r'/desk[s]?/',
            r'/seating/',
            r'/furniture/',
            r'/catalog/',
            r'/collection[s]?/'
        ]
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Check if URL matches product patterns
            if any(re.search(pattern, full_url, re.I) for pattern in product_patterns):
                product_urls.add(full_url)
        
        return list(product_urls)
    
    def detect_categories(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Detect product categories from navigation"""
        categories = {}
        
        # Common category keywords
        category_keywords = [
            'chairs', 'seating', 'desk', 'table', 'office',
            'executive', 'task', 'conference', 'lounge', 'workstation'
        ]
        
        # Look in navigation menus
        nav_elements = soup.find_all(['nav', 'menu', 'ul'], class_=re.compile(r'(nav|menu|category)', re.I))
        
        for nav in nav_elements:
            for link in nav.find_all('a', href=True):
                text = link.get_text(strip=True).lower()
                href = link['href']
                
                # Check if link text contains category keywords
                if any(keyword in text for keyword in category_keywords):
                    category_name = link.get_text(strip=True)
                    category_url = urljoin(base_url, href)
                    categories[category_name] = category_url
        
        return categories
    
    def scrape_category_page(self, url: str, brand_name: str) -> List[Dict]:
        """Scrape products from a category page"""
        products = []
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product cards/items
            product_containers = soup.find_all(['div', 'article'], class_=re.compile(r'(product|item|card)', re.I))
            
            for container in product_containers[:10]:  # Limit to 10 per category
                product = self.extract_product_from_container(container, url, brand_name)
                if product:
                    products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"Error scraping category {url}: {e}")
            return []
    
    def scrape_product_page(self, url: str, brand_name: str) -> Optional[Dict]:
        """Scrape detailed product information from product page"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            title = self.extract_product_title(soup)
            description = self.extract_product_description(soup)
            image_url = self.extract_product_image(soup, url)
            price = self.extract_product_price(soup)
            features = self.extract_product_features(soup)
            
            if title:
                return {
                    'brand': brand_name,
                    'model': title,
                    'description': description,
                    'image_url': image_url,
                    'price': price,
                    'features': features,
                    'source_url': url
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error scraping product {url}: {e}")
            return None
    
    def extract_product_from_container(self, container: BeautifulSoup, base_url: str, brand_name: str) -> Optional[Dict]:
        """Extract product info from a container element"""
        try:
            # Find title
            title_elem = container.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'(title|name|product)', re.I))
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Find image
            img = container.find('img')
            image_url = None
            if img:
                image_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if image_url:
                    image_url = urljoin(base_url, image_url)
            
            # Find price
            price_elem = container.find(['span', 'div'], class_=re.compile(r'price', re.I))
            price = self.parse_price(price_elem.get_text(strip=True)) if price_elem else None
            
            # Find link
            link_elem = container.find('a', href=True)
            product_url = urljoin(base_url, link_elem['href']) if link_elem else None
            
            if title:
                return {
                    'brand': brand_name,
                    'model': title,
                    'image_url': image_url,
                    'price': price,
                    'source_url': product_url
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting product from container: {e}")
            return None
    
    def extract_product_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title from page"""
        # Try common title patterns
        selectors = [
            ('h1', {'class_': re.compile(r'(product|title|name)', re.I)}),
            ('h1', {}),
            ('meta', {'property': 'og:title'}),
            ('title', {})
        ]
        
        for tag, attrs in selectors:
            if tag == 'meta':
                elem = soup.find(tag, attrs)
                if elem:
                    return elem.get('content')
            else:
                elem = soup.find(tag, attrs)
                if elem:
                    return elem.get_text(strip=True)
        
        return None
    
    def extract_product_description(self, soup: BeautifulSoup) -> str:
        """Extract product description"""
        # Try meta description first
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try common description containers
        desc_containers = soup.find_all(['div', 'p'], class_=re.compile(r'(description|detail|overview)', re.I))
        
        for container in desc_containers[:3]:
            text = container.get_text(strip=True)
            if len(text) > 50:  # Minimum length for valid description
                return text[:500]  # Limit length
        
        return ""
    
    def extract_product_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract main product image URL"""
        # Try various image sources
        img_selectors = [
            soup.find('img', class_=re.compile(r'(product|main|primary|hero)', re.I)),
            soup.find('meta', property='og:image'),
            soup.find('img', {'itemprop': 'image'}),
            soup.find('img')
        ]
        
        for selector in img_selectors:
            if selector:
                if selector.name == 'meta':
                    img_url = selector.get('content')
                else:
                    img_url = selector.get('src') or selector.get('data-src') or selector.get('data-lazy-src')
                
                if img_url:
                    return urljoin(base_url, img_url)
        
        return None
    
    def extract_product_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product price"""
        price_selectors = [
            soup.find(['span', 'div', 'p'], class_=re.compile(r'price', re.I)),
            soup.find(['span', 'div', 'p'], {'itemprop': 'price'})
        ]
        
        for elem in price_selectors:
            if elem:
                price_text = elem.get_text(strip=True)
                price = self.parse_price(price_text)
                if price:
                    return price
        
        return None
    
    def extract_product_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features/specifications"""
        features = []
        
        # Look for feature lists
        feature_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'(feature|spec|benefit)', re.I))
        
        for feature_list in feature_lists[:2]:  # Limit to 2 lists
            for item in feature_list.find_all('li')[:5]:  # Max 5 features per list
                text = item.get_text(strip=True)
                if text and len(text) < 100:
                    features.append(text)
        
        return features
    
    def parse_price(self, text: str) -> Optional[float]:
        """Parse price from text"""
        try:
            # Remove currency symbols and extract numbers
            price_match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
            if price_match:
                return float(price_match.group())
        except:
            pass
        return None
    
    def check_robots_allowed(self, website: str) -> bool:
        """Check if scraping is allowed by robots.txt"""
        try:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = urljoin(website, '/robots.txt')
            rp.set_url(robots_url)
            rp.read()
            
            # Check if our user agent can fetch the site
            return rp.can_fetch(self.headers['User-Agent'], website)
        except Exception as e:
            logger.warning(f"Could not read robots.txt: {e}")
            return True  # Allow by default if robots.txt is not accessible
    
    def get_product_image(self, brand_name: str, model_name: str, website: str) -> Optional[str]:
        """
        Search for product image on brand website
        """
        try:
            logger.info(f"Searching image for {brand_name} - {model_name}")
            
            # Build search query
            search_terms = f"{brand_name} {model_name}"
            
            # Try to find product page
            response = self.session.get(website, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search for product link containing model name
            for link in soup.find_all('a', href=True):
                if model_name.lower() in link.get_text().lower():
                    product_url = urljoin(website, link['href'])
                    product = self.scrape_product_page(product_url, brand_name)
                    if product and product.get('image_url'):
                        return product['image_url']
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching image: {e}")
            return None
    
    def get_product_description(self, brand_name: str, model_name: str, website: str) -> str:
        """
        Get detailed product description from brand website
        """
        try:
            logger.info(f"Fetching description for {brand_name} - {model_name}")
            
            # Try to find and scrape product page
            response = self.session.get(website, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Search for product link
            for link in soup.find_all('a', href=True):
                if model_name.lower() in link.get_text().lower():
                    product_url = urljoin(website, link['href'])
                    product = self.scrape_product_page(product_url, brand_name)
                    if product and product.get('description'):
                        return product['description']
            
            # Fallback to generic description
            return f"{brand_name} {model_name} - Premium office furniture with superior ergonomics and modern design"
            
        except Exception as e:
            logger.error(f"Error fetching description: {e}")
            return f"{brand_name} {model_name}"
