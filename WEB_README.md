# LinkedIn Job Search Agent - Web Interface

🎨 **Material Design 3 Web Application** for the LinkedIn Job Search Agent

## ✨ Features

- **🎨 Material Design 3 Interface** - Modern, responsive design following Google's latest design system
- **🌙 Dark/Light Theme Toggle** - Automatic theme switching with user preferences
- **📱 Fully Responsive** - Works perfectly on desktop, tablet, and mobile devices
- **⚡ Real-time Search Progress** - Live updates during job search with progress indicators
- **🔍 Advanced Filtering** - Filter jobs by title, company, location, salary, and remote work
- **💾 Multiple Export Formats** - Export results as CSV, JSON, or Excel files
- **🚀 Fast & Intuitive** - Smooth animations and instant feedback
- **♿ Accessible** - Screen reader friendly with proper ARIA labels and keyboard navigation

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd linkedin_job_agent
pip install -r requirements.txt
```

### 2. Start the Web Server
```bash
python web_app.py
```

### 3. Access the Interface
Open your browser and navigate to: **http://localhost:5000**

## 🎯 How to Use

### Search for Jobs
1. **Enter Keywords**: Type job titles, skills, or keywords (e.g., "Python Developer", "Data Scientist")
2. **Set Location**: Specify location or leave empty for all locations
3. **Apply Filters** (optional):
   - Experience Level (Entry, Mid-Senior, Director, etc.)
   - Job Type (Full-time, Part-time, Contract, etc.)
   - Date Posted (Past 24h, Week, Month)
4. **Configure Options**:
   - Set maximum number of jobs (1-100)
   - Enable "Get detailed descriptions" for more complete data (slower)
5. **Click "Search Jobs"**

### Monitor Progress
- Watch real-time progress with status updates
- See live job count as they're discovered
- Progress indicator shows search completion

### View Results
- **Browse Job Cards**: Scroll through attractive job listings
- **Filter Results**: Use the search bar to filter by keywords
- **Quick Filters**: Use chips to filter by salary info or remote jobs
- **Export Data**: Download results in CSV, JSON, or Excel format

### Theme Customization
- Click the theme toggle button (🌙/☀️) in the top-right corner
- Theme preference is automatically saved

## 🎨 Material Design 3 Features

### Color System
- **Dynamic Color**: Adaptive color palettes based on Material You
- **High Contrast Support**: Enhanced visibility for accessibility
- **Dark Theme**: Full dark mode with proper contrast ratios

### Typography
- **Material Design Type Scale**: Consistent typography hierarchy
- **Responsive Text**: Scales appropriately on different screen sizes
- **Readable Fonts**: Optimized for web readability

### Components
- **Elevated Cards**: Job listings with proper elevation and hover effects
- **Material Buttons**: Filled, outlined, and text buttons with ripple effects
- **Form Fields**: Outlined text fields with floating labels
- **Progress Indicators**: Circular progress with smooth animations
- **Chips**: Filter chips with selection states
- **Snackbars**: Toast notifications for user feedback

## 🔧 API Endpoints

The web app provides RESTful API endpoints:

- `GET /` - Main web interface
- `POST /api/search` - Start job search
- `GET /api/status` - Get search progress
- `GET /api/results` - Get job results
- `GET /api/export/{format}` - Export data (csv/json/excel)
- `GET /api/clear` - Clear current results
- `GET /health` - Health check

## 📱 Responsive Design

### Desktop (1200px+)
- Full-width layout with sidebar navigation
- Multi-column job cards grid
- Advanced filter sidebar

### Tablet (768px - 1199px)
- Adapted layout with collapsible navigation
- Two-column job cards grid
- Simplified filter interface

### Mobile (< 768px)
- Single-column layout
- Stack job cards vertically
- Touch-optimized interactions
- Collapsible search form

## 🎨 Customization

### Theme Colors
Edit `web/static/css/styles.css` to customize colors:
```css
:root {
  --md-sys-color-primary: #your-color;
  --linkedin-blue: #0a66c2;
  --success-green: #4caf50;
}
```

### Layout
Modify `web/templates/index.html` for layout changes:
- Add new sections
- Modify component structure
- Update Material Design components

### Functionality
Extend `web/static/js/app.js` for new features:
- Add custom filters
- Implement additional export formats
- Create new interactive elements

## 🔧 Development

### File Structure
```
linkedin_job_agent/
├── web_app.py              # Flask application
├── web/
│   ├── templates/
│   │   └── index.html      # Main HTML template
│   └── static/
│       ├── css/
│       │   └── styles.css  # Material Design 3 styles
│       └── js/
│           └── app.js      # Frontend JavaScript
└── requirements.txt        # Updated with Flask dependencies
```

### Adding New Features

1. **Backend API**: Add routes to `web_app.py`
2. **Frontend Logic**: Update `app.js` with new functionality
3. **UI Components**: Add Material Design components to `index.html`
4. **Styling**: Update `styles.css` with new styles

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**:
```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

**Module Not Found**:
```bash
# Ensure you're in the correct directory
cd linkedin_job_agent
pip install -r requirements.txt
```

**Browser Compatibility**:
- Modern browsers required (Chrome 90+, Firefox 88+, Safari 14+)
- Material Web Components require ES6 module support

**Search Not Working**:
- Check Chrome/Chromium installation
- Verify LinkedIn accessibility (not blocked)
- Check browser console for JavaScript errors

## 🔒 Security Notes

- **CORS**: Configured for local development
- **Rate Limiting**: Built-in delays to prevent IP blocking
- **Data Validation**: Input sanitization on both client and server
- **XSS Protection**: HTML escaping for user-generated content

## 🚀 Production Deployment

For production deployment:

1. **Environment Variables**:
   ```bash
   export FLASK_ENV=production
   export FLASK_DEBUG=False
   ```

2. **WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
   ```

3. **Reverse Proxy**: Use Nginx or Apache for static files
4. **HTTPS**: Enable SSL/TLS certificates
5. **Security Headers**: Add security middleware

## 📄 License

This web interface is part of the LinkedIn Job Search Agent project and is intended for educational and personal use. Please respect LinkedIn's terms of service.

---

**🎨 Built with Material Design 3 • 🚀 Powered by Flask • 💝 Made with Love**