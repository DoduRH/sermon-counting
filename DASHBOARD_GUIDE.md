# Sermon Counting Dashboard - Getting Started Guide

## What Was Created

A modern, interactive web dashboard for viewing your sermon counting visualizations. The dashboard is completely static (no backend required) and works perfectly with GitHub Pages.

### Files Created:

1. **`output/index.html`** - Main dashboard UI with:
   - Category selector (Combined, EB, ECC, EW)
   - Graph type selector (Bar, Count, Line, Stacked Bar)
   - Quick navigation buttons for common combinations
   - Keyboard shortcuts (arrow keys to navigate)
   - Responsive, mobile-friendly design
   - Modern gradient UI with smooth animations

2. **`output/.nojekyll`** - Required for GitHub Pages to serve HTML files correctly

3. **`README.md`** - Updated with usage instructions and deployment info

## How to Use Locally

1. Generate your graphs as usual (your existing code)
2. Open `output/index.html` in any web browser
3. Select a category and graph type from the dropdowns or quick buttons
4. Use arrow keys (← →) to switch between graph types
5. Click any quick button to jump to a specific visualization

## Deploy to GitHub Pages

### Prerequisites
- Node.js and npm installed (`npm --version`)
- Git repository initialized
- `gh-pages` package installed

### Installation (one-time)
```bash
npm install --save-dev gh-pages
```

### Deployment (after updating graphs)
```bash
npx gh-pages -d output
```

This command:
1. Takes everything in the `output/` folder
2. Creates/updates a `gh-pages` branch in your repo
3. Makes it available at: `https://<github-username>.github.io/sermon-counting`

### GitHub Pages Configuration

In your GitHub repository settings:
1. Go to **Settings** → **Pages**
2. Source should be set to `gh-pages` branch
3. Your site will be live at the URL shown

## Features

✨ **Interactive Controls**
- Dropdown menus for category and graph type selection
- Quick navigation buttons for common combinations
- Smooth transitions between graphs

📱 **Responsive Design**
- Works on desktop, tablet, and mobile
- Touch-friendly buttons
- Adaptive layout

⚡ **Keyboard Navigation**
- Arrow Left/Right to change graph types
- Fast and intuitive

🎨 **Modern UI**
- Purple gradient background
- Clean card-based design
- Loading indicators
- Smooth animations

## Customization

To customize the dashboard, edit `output/index.html`:

### Change Colors
Find the `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);` line and modify the hex colors.

### Add More Quick Buttons
In the quick navigation section, add buttons like:
```html
<button class="quick-select-btn" data-category="EB" data-graph="line">EB - Line</button>
```

### Adjust Graph Height
Change the `min-height: 600px;` value in the CSS section.

## Troubleshooting

**Graphs not loading?**
- Ensure your graph HTML files are in: `combined/`, `EB/`, `ECC/`, `EW/` directories
- Each should have: `bar.html`, `count.html`, `line.html`, `stacked_bar.html`
- Verify paths are correct in the file structure

**GitHub Pages not updating?**
- Run: `npx gh-pages -d output --dry-run` to preview changes
- Verify the `gh-pages` branch appears in your repository
- Clear your browser cache

**Iframe content not showing?**
- Check browser console (F12) for CORS errors
- Ensure `.nojekyll` file is in the output directory

## File Structure

```
sermon-counting/
├── output/
│   ├── index.html          ← Open this in browser!
│   ├── .nojekyll           ← Required for GitHub Pages
│   ├── combined/
│   │   ├── bar.html
│   │   ├── count.html
│   │   ├── line.html
│   │   └── stacked_bar.html
│   ├── EB/
│   ├── ECC/
│   └── EW/
├── README.md
└── (your other files)
```

## Next Steps

1. Generate your graph data as usual
2. Test locally: Open `output/index.html` in your browser
3. Deploy: Run `npx gh-pages -d output`
4. Share your dashboard URL!

Enjoy your interactive sermon counting dashboard! 📊
