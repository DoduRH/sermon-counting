# Quick Start Guide - Sermon Counting Dashboard

## 🎯 What You Built

An interactive web dashboard that displays your sermon counting graphs. No coding needed to use it!

## 🚀 Get Started in 2 Minutes

### Step 1: View Locally
Your dashboard is already accessible at: `http://localhost:8000/`

1. Open the link in your browser
2. You'll see a beautiful dashboard with:
   - Purple gradient background
   - Category selector (top-left dropdown)
   - Graph type selector (top-right dropdown)
   - Quick navigation buttons
   - Large display area for graphs

### Step 2: Try It Out
- **Click a dropdown** to select a different category or graph type
- **Click a quick button** to jump to a specific visualization
- **Press arrow keys** (← →) to switch between graph types
- **Watch graphs load** smoothly in the display area

### Step 3: Deploy to GitHub Pages (Optional)

When ready to share with your team:

```bash
./deploy.sh
```

That's it! Your dashboard will be online at:
```
https://<username>.github.io/sermon-counting
```

## 📊 Features Explained

| Feature | How to Use |
|---------|-----------|
| **Category Selector** | Top-left dropdown - Choose Combined, EB, ECC, or EW |
| **Graph Type Selector** | Top-right dropdown - Choose Bar, Count, Line, or Stacked Bar |
| **Quick Buttons** | Click any button to jump directly to that combination |
| **Keyboard Navigation** | Press ← or → arrow keys to switch graph types |
| **Interactive Graphs** | Plotly graphs with zoom, pan, and export options |

## 🎨 What's Included

✅ **Modern UI** - Professional gradient design with smooth animations  
✅ **Responsive** - Works perfectly on desktop, tablet, and mobile  
✅ **No Backend** - Pure HTML/JavaScript, works offline  
✅ **GitHub Pages Ready** - Deploy with one command  
✅ **Fast Loading** - Lightweight CSS and instant navigation  
✅ **Keyboard Shortcuts** - Arrow keys for quick navigation  

## 📁 File Structure

Your graphs are organized like this:
```
output/
├── index.html          ← The dashboard (open this!)
├── .nojekyll           ← GitHub Pages helper
├── combined/
│   ├── bar.html        ← Combined category graphs
│   ├── count.html
│   ├── line.html
│   └── stacked_bar.html
├── EB/                 ← Emmanuel Bristol graphs
├── ECC/                ← Emmanuel City Church graphs
└── EW/                 ← Emmanuel Wales graphs
```

## 💡 Tips & Tricks

**Want to customize colors?**
- Edit `output/index.html`
- Find `background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);`
- Change the hex colors to your preference

**Want to add more quick buttons?**
- Find the "Quick Navigation" section in `output/index.html`
- Add new button: `<button class="quick-select-btn" data-category="EB" data-graph="line">EB - Line</button>`

**Need to update graphs?**
- Regenerate your graphs as usual
- Run `./deploy.sh` to push updated graphs to GitHub Pages

## 🔗 Useful Links

- **Local Dashboard**: `http://localhost:8000/`
- **Main README**: `README.md`
- **Detailed Guide**: `DASHBOARD_GUIDE.md`
- **Full Summary**: `DASHBOARD_SUMMARY.md`

## ❓ FAQ

**Q: Do I need to restart the server?**  
A: No! Just refresh your browser. The server keeps running in the background.

**Q: Can I customize the dashboard?**  
A: Yes! Edit `output/index.html` - it's well-commented and easy to modify.

**Q: Will GitHub Pages work?**  
A: Yes! Run `./deploy.sh` and your dashboard will be live. Share the URL with anyone.

**Q: Can I access it offline?**  
A: After deploying to GitHub Pages, yes! The site is fully static.

**Q: How do I update graphs?**  
A: Regenerate them as usual, then run `./deploy.sh` to update the live site.

## 🎓 What Happens When You Deploy

1. You run: `./deploy.sh`
2. The script uploads everything in `output/` to GitHub's `gh-pages` branch
3. GitHub automatically serves it as a website
4. Your dashboard is now live and shareable!

## 🎉 You're All Set!

Your sermon counting dashboard is ready to go. 

**Next Steps:**
1. Visit `http://localhost:8000` to see it in action
2. Play around with the graphs and selections
3. When ready, run `./deploy.sh` to go live
4. Share your dashboard URL with your team!

---

**Questions?** Check out `DASHBOARD_GUIDE.md` for more detailed information.

Enjoy your new dashboard! 📊✨
