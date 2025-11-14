# 🚀 Questemate - Quick Start Guide

## ✅ Your App is Ready!

**Server Status**: 🟢 RUNNING  
**URL**: http://127.0.0.1:5000  
**Backend**: ✅ Connected  
**UI**: ✅ Revolutionary Design

---

## 🎯 Quick Test (2 minutes)

### Test Upload & Processing

1. **Open the app**
   ```
   http://127.0.0.1:5000
   ```

2. **Click the first card** (💰 Quote with Price List)
   - Card will smoothly expand to fullscreen
   - See the beautiful animations!

3. **Upload a file**
   - Drag & drop a PDF or Excel file
   - OR click the upload zone to browse
   - Supported: PDF, XLSX, XLS, JPG, PNG

4. **Click "Extract Data"**
   - Watch the loading spinner
   - AI processes your file
   - Results appear in ~10-30 seconds

5. **View Results**
   - See extracted table data
   - Review the preview
   - Check the summary

6. **Export**
   - Click "Download PDF" or "Download Excel"
   - File downloads to your computer

7. **Return Home**
   - Click the **×** button in top-right
   - Card smoothly collapses back
   - Try another workflow!

---

## 📋 All 4 Workflows Explained

### 💰 Workflow 1: Quote with Price List
**Best for**: Creating quotes from existing price lists

**Steps**:
1. Upload BOQ + Price List
2. Click "Extract Data"
3. Review extracted pricing
4. Export as PDF/Excel/Word

**Output**: Professional quotation with pricing

---

### 🎯 Workflow 2: Multi-Budget Offers
**Best for**: Providing multiple pricing options to clients

**Steps**:
1. Upload BOQ only (no prices needed!)
2. Click "Generate Budget Options"
3. AI creates 3 price tiers
4. Export all tiers or select one

**Output**: Budgetary, Mid-Range, High-End options

---

### 🎨 Workflow 3: Presentation Generator
**Best for**: Client presentations and proposals

**Steps**:
1. Upload BOQ + Product Images
2. Click "Create Presentation"
3. AI designs professional slides
4. Export as PowerPoint or PDF

**Output**: Beautiful presentation with images

---

### 📋 Workflow 4: MAS Generator
**Best for**: Material approval documentation

**Steps**:
1. Upload BOQ with material specs
2. Click "Generate Approval Sheets"
3. AI extracts material info
4. Export as PDF/Excel

**Output**: Material Approval Sheets (MAS)

---

## 🎨 UI Features to Try

### Card Animations
- **Hover over cards** → 3D tilt effect
- **Move mouse around** → Card follows cursor
- **Icons animate** → Scale and rotate
- **Gradient wave** → Radial effect appears

### Upload Zone
- **Drag files over** → Purple gradient activates
- **Drop files** → Instant upload starts
- **Success** → Green notification slides up

### Navigation
- **Click card** → Smooth expansion (0.7s)
- **Scroll workflow** → Sticky header stays
- **Click ×** → Smooth collapse back
- **Return home** → Cards ready again

### Loading States
- **Spinner rotates** → Processing indicator
- **Text updates** → Shows current step
- **Smooth transitions** → No jarring changes

---

## 🔧 Backend Integration Points

### What Happens Behind the Scenes

**When you upload**:
```
Browser → POST /upload → Flask saves file → Returns file ID
```

**When you process**:
```
Browser → POST /extract/{id} → PP-StructureV3 API → Extract tables
        → POST /stitch-tables/{id} → Combine pages → Return HTML
```

**When you export**:
```
Browser → GET /download/extracted/{id}?format=pdf
        → Flask generates PDF → Browser downloads
```

---

## 📊 File Support

### Supported Formats
✅ **PDF** - Documents with tables/images  
✅ **XLSX** - Excel spreadsheets  
✅ **XLS** - Older Excel format  
✅ **JPG/JPEG** - Product images  
✅ **PNG** - Images with transparency  

### Size Limits
- **Max file size**: 50MB per file
- **Multiple files**: Yes, unlimited
- **Total upload**: No hard limit

### What Works Best
- **Clear PDFs** with visible tables
- **Structured Excel** files
- **High-quality images** (300+ DPI)
- **Well-organized BOQs**

---

## 🎯 Tips for Best Results

### For Quotations
1. Use clear, structured BOQ files
2. Include quantity and unit columns
3. Add item descriptions
4. Include product codes if available

### For Multi-Budget
1. Upload complete BOQ
2. Include quantities and units
3. Let AI estimate pricing
4. Review and adjust if needed

### For Presentations
1. Upload high-quality product images
2. Name images clearly
3. Include BOQ with descriptions
4. Let AI match images to items

### For MAS
1. Include detailed specifications
2. Add manufacturer info if available
3. Include model numbers
4. Upload reference images

---

## 🐛 Troubleshooting

### Upload Not Working?
- ✅ Check file size < 50MB
- ✅ Verify file type (PDF, Excel, images)
- ✅ Try one file at a time
- ✅ Check browser console for errors

### Processing Stuck?
- ✅ Wait 30-60 seconds (large files take time)
- ✅ Check your internet connection
- ✅ Try refreshing the page
- ✅ Re-upload the file

### Export Not Working?
- ✅ Make sure processing completed
- ✅ Check popup blocker settings
- ✅ Try different browser
- ✅ Check download folder

### Animations Laggy?
- ✅ Update your browser
- ✅ Close other tabs
- ✅ Disable browser extensions
- ✅ Try on different device

---

## 🎨 Customization

### Change Colors
Edit `templates/index.html`, find:
```css
:root {
    --primary: #6366f1;    /* Change this */
    --secondary: #8b5cf6;  /* And this */
}
```

### Adjust Animation Speed
Find animation durations:
```css
transition: all 0.6s cubic-bezier(...);
/* Change 0.6s to your preference */
```

### Modify Text
Search for card titles/descriptions in HTML:
```html
<h2 class="card-title">Quote with Price List</h2>
<!-- Edit this text -->
```

---

## 📈 Performance

### Expected Times
- **File Upload**: < 5 seconds
- **Small PDF (< 10 pages)**: 15-30 seconds
- **Large PDF (> 50 pages)**: 1-3 minutes
- **Excel Files**: 5-15 seconds
- **Images**: 10-20 seconds each

### Optimization Tips
- Upload one file at a time for faster processing
- Use PDF instead of images when possible
- Compress images before upload
- Split very large PDFs into smaller chunks

---

## 🎓 Learning the UI

### First-Time Users
1. **Explore the home page** → Hover over all cards
2. **Click each card** → See the workflows
3. **Upload a test file** → Try the process
4. **Watch the animations** → Enjoy the experience
5. **Export results** → Complete the workflow

### Power Users
- Use keyboard for faster navigation
- Upload multiple files in batch
- Process while reviewing previous results
- Export in multiple formats simultaneously

---

## 📞 Support

### Need Help?
1. Check `BACKEND_INTEGRATION.md` for technical details
2. Review `NEW_UI_FEATURES.md` for feature list
3. See `UI_VISUAL_GUIDE.md` for visual specs
4. Check browser console for errors
5. Review Flask server logs

### Report Issues
Include:
- What you were trying to do
- What happened instead
- Browser and version
- File type and size
- Screenshots if possible

---

## 🎉 Enjoy Your New UI!

Your Questemate platform is now ready with:
- ✅ Revolutionary modern design
- ✅ AI-powered processing
- ✅ 4 complete workflows
- ✅ Beautiful animations
- ✅ Backend integration
- ✅ Multi-format export

**Start using it now**: http://127.0.0.1:5000

---

**Quick Actions**:
- 🔗 [Open App](http://127.0.0.1:5000)
- 📖 [Read Full Docs](NEW_UI_FEATURES.md)
- 🔧 [Backend Details](BACKEND_INTEGRATION.md)
- 🎨 [Visual Guide](UI_VISUAL_GUIDE.md)

**Happy Processing! 🚀**
