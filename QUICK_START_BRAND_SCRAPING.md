# Quick Start Guide - Add Brand Feature

## 🎯 What This Feature Does

Automatically scrapes furniture brand websites and adds their products to your database - no manual data entry needed!

## 🚀 5-Minute Quick Start

### Step 1: Open Value Engineering
1. Upload and extract a BOQ file
2. Click **"Generate Alternative Offers"** button
3. The alternative offers table appears

### Step 2: Click "Add Brand"
Look for the **purple button** that says **"➕ Add Brand"**

Location: In the row with other action buttons (Apply, Export, Download)

### Step 3: Fill the Form
The modal opens with 4 fields:

```
┌─────────────────────────────────────────┐
│  ➕ Add New Brand                    ×  │
├─────────────────────────────────────────┤
│                                          │
│  Brand Name *                            │
│  ┌────────────────────────────────────┐ │
│  │ e.g., Herman Miller               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Website URL *                           │
│  ┌────────────────────────────────────┐ │
│  │ https://www.example.com           │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Country                                 │
│  ┌────────────────────────────────────┐ │
│  │ e.g., USA                         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Budget Tier *                           │
│  ┌────────────────────────────────────┐ │
│  │ ⭐ Mid-Range               ▼      │ │
│  └────────────────────────────────────┘ │
│                                          │
│     [Cancel]  [🔍 Scrape & Add Brand]  │
└─────────────────────────────────────────┘
```

### Step 4: Watch the Magic ✨

After clicking "Scrape & Add Brand", you'll see:

```
Progress Bar:
─────────────────────────────────────
🔍 Analyzing website structure... 10%
█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

📡 Fetching product data...       30%
████████████░░░░░░░░░░░░░░░░░░░░░░

💾 Processing results...          70%
████████████████████████░░░░░░░░░░

✅ Brand added successfully!     100%
████████████████████████████████████
```

### Step 5: See Results

Preview shows:
```
┌─────────────────────────────┐
│ Preview:                    │
├─────────────────────────────┤
│ Herman Miller               │
│ Country: USA                │
│ Tier: MID RANGE             │
│ Products Found: 25          │
│ Categories: chairs, desks   │
└─────────────────────────────┘
```

Modal auto-closes after 3 seconds!

### Step 6: Use New Brand

Your brand is now available:
1. In the **Category** dropdown
2. In the **Brand** dropdown  
3. In the **Model** dropdown
4. Ready to apply to your table!

## 💡 Pro Tips

### Best URLs to Use
✅ **Good**: Main homepage
   - `https://www.steelcase.com`
   - `https://www.hermanmiller.com`
   - `https://www.narbutas.com`

❌ **Avoid**: Product pages, search results
   - `https://www.example.com/products/chair-123`
   - `https://www.example.com/search?q=desk`

### Budget Tier Guide

**💰 Budgetary** (Choose for):
- Value brands
- Budget-conscious clients
- Cost-effective options
- Examples: IKEA, Office Depot

**⭐ Mid-Range** (Choose for):
- Quality brands
- Balanced price/quality
- Standard commercial
- Examples: Steelcase, Kinwai

**👑 High-End** (Choose for):
- Premium brands
- Luxury projects
- Top quality
- Examples: Herman Miller, Vitra

## 🎯 Real-World Examples

### Example 1: Add Steelcase
```
Brand Name:    Steelcase
Website URL:   https://www.steelcase.com
Country:       USA
Budget Tier:   High-End
Result:        ~30 office chairs found
Time:          20 seconds
```

### Example 2: Add Narbutas
```
Brand Name:    Narbutas
Website URL:   https://www.narbutas.com
Country:       Lithuania
Budget Tier:   Mid-Range
Result:        ~25 furniture items found
Time:          15 seconds
```

### Example 3: Add Local Brand
```
Brand Name:    Local Office Supplies
Website URL:   https://www.localoffice.ae
Country:       UAE
Budget Tier:   Budgetary
Result:        ~18 products found
Time:          12 seconds
```

## ⚡ What Happens Behind the Scenes

```
1. System checks robots.txt ✅
   └─ Makes sure scraping is allowed

2. Loads brand's homepage 🌐
   └─ Analyzes website structure

3. Finds navigation menus 🗺️
   └─ Looks for: Chairs, Desks, Tables, etc.

4. Discovers product pages 🔍
   └─ Searches for: /product/, /item/, /chair/

5. Extracts product data 📊
   └─ Gets: Name, Image, Price, Features

6. Organizes into categories 📁
   └─ Maps to: Seating, Desking, General

7. Saves to database 💾
   └─ Adds to: brand_database_custom.json

8. Updates UI dropdowns 🔄
   └─ Immediately available!
```

## 🎨 Visual Guide

### Where to Find the Button

```
┌──────────────────────────────────────────────┐
│ 💡 Alternative Offers - Value Engineering   │
├──────────────────────────────────────────────┤
│                                              │
│  Select Budget Tier:                         │
│  [💰 Budgetary] [⭐ Mid-Range] [👑 High-End]│
│                                              │
│  ┌────────┐ ┌───────────┐ ┌──────────┐     │
│  │✓ Apply │ │➕ Add Brand│ │💾 Export │     │  ← CLICK HERE
│  └────────┘ └───────────┘ └──────────┘     │
│                                              │
│  [Table with alternatives...]                │
└──────────────────────────────────────────────┘
```

### Modal Appearance

```
      Dark Background (Semi-transparent)
┌──────────────────────────────────────────────┐
│                                              │
│   ┌──────────────────────────────────────┐  │
│   │  ➕ Add New Brand              ×    │  │
│   ├──────────────────────────────────────┤  │
│   │                                      │  │
│   │  Enter brand's website URL           │  │
│   │  and we'll automatically scrape      │  │
│   │  and add their products              │  │
│   │                                      │  │
│   │  [Form fields here...]               │  │
│   │                                      │  │
│   │     [Cancel] [Scrape & Add Brand]    │  │
│   └──────────────────────────────────────┘  │
│                                              │
└──────────────────────────────────────────────┘
```

## ⚠️ Common Issues & Solutions

### "Scraping not allowed by robots.txt"
**Cause**: Website blocks automated scraping
**Solution**: 
- Contact brand for API access
- Add products manually
- Try brand's different domain (.com vs .eu)

### "No products found"
**Cause**: Website structure not recognized
**Solution**:
- Check if URL is correct
- Try main homepage instead of subpage
- Website might use JavaScript (not supported yet)

### "Error: Failed to add brand"
**Cause**: Network issue or website down
**Solution**:
- Check your internet connection
- Try again in a few minutes
- Verify URL works in browser

### "Brand already exists"
**Cause**: Brand already in database
**Solution**:
- Check existing brands in dropdown
- Use different tier if needed
- Contact support to update existing brand

## 📊 Performance Expectations

**Typical Results**:
- ⏱️ **Time**: 10-30 seconds
- 📦 **Products**: 10-50 per brand
- 📁 **Categories**: 2-5 discovered
- 🎯 **Success Rate**: 70-80% of websites

**Factors Affecting Speed**:
- Website size
- Number of products
- Internet speed
- Server location

## 🔒 Privacy & Ethics

**We respect websites**:
- ✅ Check robots.txt before scraping
- ✅ Wait 2 seconds between requests
- ✅ Use proper identification
- ✅ Don't overload servers
- ✅ Store only necessary data

**Your data**:
- 🔒 Saved locally in JSON file
- 🔒 No data sent to external services
- 🔒 Only you have access

## 📞 Need Help?

### In-App Help
1. Hover over ⓘ icons for tooltips
2. Check console for detailed logs (F12)
3. Error messages show specific issues

### Documentation
- **Full Guide**: `BRAND_SCRAPING_GUIDE.md`
- **Technical**: `IMPLEMENTATION_SUMMARY.md`
- **General**: `README.md`

### Testing
Run test script to verify:
```bash
python test_brand_scraper.py
```

## 🎓 Tips for Best Results

### 1. Start with Popular Brands
Test with well-known brands first:
- Steelcase, Herman Miller, Haworth
- They usually have well-structured websites

### 2. Use Correct Tier
Match tier to brand positioning:
- Budget brands → Budgetary
- Standard brands → Mid-Range  
- Luxury brands → High-End

### 3. Fill Country Field
Helps with:
- Better categorization
- Origin labeling
- Future filtering

### 4. Wait for Completion
Don't close modal until:
- Progress reaches 100%
- Preview appears
- Success message shows

### 5. Verify Results
Check dropdowns to ensure:
- Brand appears
- Models are listed
- Categories correct

## 🎉 Success Checklist

After adding a brand, verify:

- [ ] Progress bar reached 100%
- [ ] Preview showed products found
- [ ] Success message appeared
- [ ] Modal closed automatically
- [ ] Brand appears in Category dropdown
- [ ] Models show in Model dropdown
- [ ] Can select and apply alternatives
- [ ] Products have correct tier pricing

## 🚀 What's Next?

After adding brands:
1. **Use them**: Select in dropdowns
2. **Test**: Try different categories
3. **Compare**: Check pricing tiers
4. **Apply**: Update your BOQ
5. **Export**: Download results

---

**You're ready to go!** 🎊

Click that **➕ Add Brand** button and start expanding your furniture database!

---

**Quick Reference Card**

```
┌─────────────────────────────────────┐
│ ADD BRAND - QUICK REFERENCE         │
├─────────────────────────────────────┤
│ 1. Click "Generate Alternative      │
│    Offers"                           │
│ 2. Click "➕ Add Brand" (purple)    │
│ 3. Enter brand website URL           │
│ 4. Select budget tier                │
│ 5. Click "Scrape & Add Brand"        │
│ 6. Wait 10-30 seconds                │
│ 7. Brand now in dropdowns!           │
│                                      │
│ Tips:                                │
│ • Use main homepage URL              │
│ • Match tier to brand level          │
│ • Wait for 100% completion           │
│ • Check preview before close         │
│                                      │
│ Troubleshooting:                     │
│ • robots.txt error → Try different   │
│   domain or add manually             │
│ • No products → Check URL, retry     │
│ • Slow → Normal for large sites      │
└─────────────────────────────────────┘
```
