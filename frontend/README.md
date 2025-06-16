# Employee Activity Tracker - Frontend

A modern, responsive web interface for the Employee Activity Tracking System with LLM integration.

## Features

- **Natural Language Queries**: Ask questions in plain English about employee activities
- **Real-time Results**: Get instant responses with SQL query execution
- **Interactive Examples**: Click on example queries to get started quickly
- **Benchmark Testing**: Run comprehensive performance tests
- **Employee Management**: View all employees and their details
- **Activity Monitoring**: Browse recent employee activities
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Getting Started

### Prerequisites

- The FastAPI backend server must be running on `http://localhost:8000`
- Modern web browser with JavaScript enabled

### Running the Frontend

#### Option 1: Through FastAPI Server (Recommended)

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

#### Option 2: Direct File Access

1. Open `frontend/index.html` directly in your browser
2. Make sure the backend server is running on `http://localhost:8000`

## Usage

### Natural Language Queries

Type questions in the search box such as:
- "Who worked the most hours last week?"
- "What is the total sales revenue for the Sales department?"
- "Which employees were hired during 2023?"
- "Compare hours worked by Wei Zhang and Tao Huang"

### Example Queries

Click on any of the example query buttons to automatically fill and execute common questions:
- Sales Manager Contact
- Top Sales Performance
- Overtime Workers
- Department Revenue
- Customer Retention
- Employee Comparison

### Quick Actions

Use the action cards to:
- **View All Employees**: See complete employee directory
- **Run Benchmark**: Execute all 20 test queries and see performance metrics
- **Recent Activities**: Browse latest employee activity records
- **Export Data**: (Coming soon) Download data in various formats

## Features Overview

### Query Interface
- Clean, modern search interface
- Auto-complete and suggestions
- Real-time query execution
- Loading indicators and progress feedback

### Results Display
- Formatted query responses
- Execution time tracking
- Confidence scoring
- SQL query visibility
- Error handling and display

### Performance Monitoring
- Query counter in header
- Execution time metrics
- Success rate tracking
- Benchmark testing capabilities

### User Experience
- Toast notifications for feedback
- Smooth animations and transitions
- Responsive grid layouts
- Mobile-optimized interface

## Technical Details

### Architecture
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Modern CSS with Flexbox/Grid, custom animations
- **Icons**: Font Awesome 6.0
- **Fonts**: Inter font family for clean typography

### API Integration
- RESTful API communication
- JSON data exchange
- Error handling and retry logic
- CORS support for cross-origin requests

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Customization

### Styling
Edit `styles.css` to customize:
- Color scheme and branding
- Layout and spacing
- Animations and transitions
- Responsive breakpoints

### Functionality
Edit `script.js` to modify:
- API endpoints and configuration
- Query processing logic
- UI interactions and behaviors
- Data display formatting

### Content
Edit `index.html` to change:
- Page structure and layout
- Example queries and descriptions
- Static text and labels
- Meta information

## Troubleshooting

### Common Issues

1. **"Connection Error" messages**
   - Ensure backend server is running on `http://localhost:8000`
   - Check browser console for detailed error messages
   - Verify CORS configuration in backend

2. **Queries not executing**
   - Check network connectivity
   - Verify API endpoints are accessible
   - Look for JavaScript errors in browser console

3. **Styling issues**
   - Clear browser cache and reload
   - Check if CSS files are loading properly
   - Verify Font Awesome CDN is accessible

### Development Tips

- Use browser developer tools for debugging
- Check Network tab for API request/response details
- Monitor Console for JavaScript errors
- Use responsive design mode for mobile testing

## Future Enhancements

- Data export functionality
- Advanced filtering and search
- Real-time data updates
- User authentication and authorization
- Dashboard and analytics views
- Offline capability with service workers 