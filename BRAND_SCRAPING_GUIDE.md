# Brand Scraping and Management Feature

## Overview
This feature allows users to automatically scrape furniture brand websites and add them to the application's brand database. The system intelligently discovers products, categories, and specifications from brand websites.

## Features

### 1. Intelligent Web Scraping
- **Automatic Product Discovery**: Scans brand websites to find product pages
- **Category Detection**: Identifies product categories (chairs, desks, tables, etc.)
- **Data Extraction**: Extracts product names, images, prices, descriptions, and features
- **Robots.txt Compliance**: Respects website scraping permissions
- **Rate Limiting**: Includes delays between requests to avoid overloading servers

### 2. Add Brand Interface
- **User-Friendly Modal**: Simple form to add new brands
- **Required Fields**:
  - Brand Name
  - Website URL
  - Budget Tier (Budgetary/Mid-Range/High-End)
- **Optional Fields**:
  - Country of Origin
- **Real-time Progress**: Shows scraping progress with status updates
- **Preview Results**: Displays found products and categories before saving

### 3. Database Integration
- **Automatic Format Conversion**: Converts scraped data to database format
- **Category Mapping**: Intelligently maps products to categories (seating/desking/general)
- **Model Organization**: Organizes products by subcategories
- **Persistent Storage**: Saves brands to JSON file for future use

## How to Use

### Adding a New Brand

1. **Open Value Engineering Tab**
   - Click "Generate Alternative Offers" button
   - The alternative offers table will appear

2. **Click "Add Brand" Button**
   - Located in the action buttons row
   - Purple button with ➕ icon

3. **Fill in Brand Information**
   - **Brand Name**: Enter the furniture brand name (e.g., "Herman Miller")
   - **Website URL**: Enter the main website URL (e.g., "https://www.hermanmiller.com")
   - **Country**: Enter country of origin (optional)
   - **Budget Tier**: Select appropriate tier:
     - 💰 Budgetary: Affordable brands
     - ⭐ Mid-Range: Medium-priced brands
     - 👑 High-End: Premium/luxury brands

4. **Submit and Wait**
   - Click "🔍 Scrape & Add Brand"
   - Watch the progress bar:
     - 10%: Analyzing website structure
     - 30%: Fetching product data
     - 70%: Processing results
     - 100%: Complete!
   
5. **Review Results**
   - Preview shows:
     - Brand name and country
     - Budget tier
     - Number of products found
     - Product categories discovered
   - Modal closes automatically after 3 seconds

### Using Scraped Brands

Once added, the brand immediately becomes available:
- Select from Category dropdown in alternative offers
- Choose from Brand dropdown
- Pick models from Model dropdown
- Apply to original table

## Technical Implementation

### Backend Components

#### BrandScraper Class (`utils/brand_scraper.py`)

**Main Methods:**
- `scrape_brand_website(website, brand_name)`: Main scraping orchestrator
- `find_product_pages(soup, base_url)`: Discovers product URLs
- `detect_categories(soup, base_url)`: Finds category pages
- `scrape_category_page(url, brand_name)`: Extracts products from category
- `scrape_product_page(url, brand_name)`: Gets detailed product info
- `extract_product_*()`: Various extraction methods for specific data

**Safety Features:**
- robots.txt checking
- Rate limiting (2 second delay between requests)
- User-agent headers
- Error handling and logging
- URL validation

### API Endpoints

#### POST `/api/brands/scrape`
Scrapes a brand's website without adding to database.

**Request:**
```json
{
  "brand_name": "Herman Miller",
  "website": "https://www.hermanmiller.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "brand": "Herman Miller",
    "categories": {...},
    "products": [...]
  },
  "message": "Successfully scraped 25 products"
}
```

#### POST `/api/brands/add`
Adds a brand to database with provided data.

**Request:**
```json
{
  "brand_name": "Herman Miller",
  "website": "https://www.hermanmiller.com",
  "country": "USA",
  "tier": "high_end",
  "categories": {
    "chairs": [...],
    "desks": [...]
  }
}
```

#### POST `/api/brands/scrape-and-add`
Scrapes and adds brand in one operation (recommended).

**Request:**
```json
{
  "brand_name": "Herman Miller",
  "website": "https://www.hermanmiller.com",
  "country": "USA",
  "tier": "high_end"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully scraped and added Herman Miller with 25 products",
  "brand": {...},
  "products_count": 25,
  "categories": ["chairs", "desks", "tables"]
}
```

### Frontend Components

#### Modal HTML
- Located in `templates/index.html`
- ID: `addBrandModal`
- Styled with blue/gold theme matching app

#### JavaScript Functions
- `openAddBrandModal()`: Shows the modal
- `closeAddBrandModal()`: Hides the modal
- `handleAddBrand(event)`: Processes form submission
  - Validates input
  - Makes API call
  - Updates progress
  - Shows results

## Data Flow

```
User Input
    ↓
Brand Website URL
    ↓
Web Scraper
    ↓
HTML Parsing (BeautifulSoup)
    ↓
Product Discovery
    ↓
Data Extraction
    ↓
Format Conversion
    ↓
Database Integration
    ↓
Available in Dropdowns
```

## Scraping Strategy

### 1. Homepage Analysis
- Load main website
- Find navigation menus
- Identify category links
- Detect product patterns

### 2. Category Discovery
- Look for common keywords: chairs, seating, desk, table, office
- Parse navigation elements
- Extract category URLs

### 3. Product Extraction
Uses multiple heuristics:
- URL patterns (`/product/`, `/item/`, `/chair/`, etc.)
- HTML class patterns (`product`, `item`, `card`)
- Semantic HTML (`<article>`, `<section>`)
- Meta tags (`og:product`, `product:price`)

### 4. Data Parsing
Extracts:
- **Title**: From `<h1>`, `og:title`, or `<title>`
- **Image**: From `<img>` tags, `og:image`, or `data-src` attributes
- **Price**: From price-related classes or itemprop
- **Description**: From meta description or content areas
- **Features**: From feature lists (`<ul>`, `<ol>`)

## Best Practices

### For Users
1. **Start with brand homepage**: Use main URL, not product pages
2. **Check preview**: Verify products found before closing
3. **Correct tier selection**: Choose appropriate budget tier
4. **Be patient**: Scraping takes 10-30 seconds depending on website

### For Developers
1. **Respect robots.txt**: Always check before scraping
2. **Rate limiting**: Include delays between requests
3. **Error handling**: Catch and log all exceptions
4. **Fallbacks**: Provide default values when data unavailable
5. **Testing**: Test with multiple brands to ensure compatibility

## Limitations

1. **Website Dependency**: Scraping success depends on website structure
2. **Anti-Bot Protection**: Some websites block automated access
3. **Dynamic Content**: JavaScript-rendered content may not be captured
4. **Rate Limits**: Too frequent requests may result in IP blocking
5. **Data Quality**: Extracted data quality varies by website

## Future Enhancements

1. **JavaScript Rendering**: Use Selenium/Playwright for dynamic sites
2. **API Integration**: Direct API access for brands that offer it
3. **Image Downloads**: Store product images locally
4. **Update Scheduling**: Automatic periodic updates of brand data
5. **Manual Editing**: UI for editing scraped product information
6. **Bulk Import**: CSV/Excel import for manual brand additions
7. **Brand Verification**: Quality check before adding to database

## Troubleshooting

### "Scraping not allowed by robots.txt"
- Website blocks automated scraping
- Solution: Contact brand for API access or add manually

### "Error: Failed to add brand"
- Network issues or website down
- Solution: Check URL, try again later

### "No products found"
- Website structure not recognized
- Solution: Report issue, may need custom scraper for this brand

### "Brand already exists"
- Brand already in database
- Solution: Check existing brands list, or update manually

## Testing

Run the test script to verify scraper functionality:

```bash
python test_brand_scraper.py
```

This will test scraping with sample furniture brands and display results.

## Security Considerations

1. **Rate Limiting**: Prevents server overload
2. **Robots.txt**: Respects website policies
3. **User-Agent**: Identifies scraper properly
4. **Error Handling**: Prevents crashes from malformed data
5. **Input Validation**: URL and data validation before processing

## Performance

- **Scraping Speed**: 10-30 seconds per brand
- **Products per Brand**: Typically 10-50 products
- **Database Impact**: Minimal, uses JSON file storage
- **Memory Usage**: Low, processes one product at a time

## Conclusion

The Brand Scraping feature significantly streamlines the process of expanding the furniture brand database. Users can easily add new brands without manual data entry, while the system maintains data quality and website scraping ethics.
