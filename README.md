# URL Status Code Checker - Streamlit App

A web-based URL status code checker built with Streamlit. Check HTTP status codes and track redirect chains for multiple URLs with a user-friendly interface.

## Features

- Upload CSV files with URLs or enter URLs manually
- Check HTTP status codes with redirect chain tracking (up to 5 redirects)
- Parallel processing with configurable worker threads
- Real-time progress tracking
- Default Chrome-like headers (configurable)
- Custom headers support (JSON format)
- Visual status code indicators with color coding
- Filter and search results
- Download results as CSV
- Summary statistics and status distribution

## Installation

1. Navigate to the app directory:
```bash
cd st-status-checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. The app will open in your default browser at `http://localhost:8501`

### Upload CSV Mode

1. Prepare a CSV file with a column named `URLs To Check`
2. Upload the CSV file using the file uploader
3. Adjust settings in the sidebar if needed:
   - Max Parallel Workers (1-20, default: 10)
   - Delay Between Requests (0-2 seconds, default: 0.1)
   - Request Timeout (5-60 seconds, default: 10)
4. Click "Start Checking URLs"
5. View results and download as CSV

### Manual Entry Mode

1. Switch to the "Manual Entry" tab
2. Enter URLs (one per line)
3. Adjust settings in the sidebar if needed
4. Click "Check URLs"
5. View results and download as CSV

## Headers Configuration

### Default Headers
The app uses Chrome-like headers by default:
- User-Agent: Chrome 123 on Windows
- Accept: HTML/XHTML/XML content types
- Accept-Language: English (US)
- Accept-Encoding: gzip, deflate, br
- DNT: 1 (Do Not Track)
- Connection: keep-alive

### Custom Headers
1. Enable "Use Custom Headers" in the sidebar
2. Paste your custom headers in JSON format
3. The app will validate the JSON format
4. Custom headers will be used for all requests

Example custom headers:
```json
{
  "User-Agent": "MyCustomBot/1.0",
  "Accept": "text/html",
  "Custom-Header": "value"
}
```

## Results

The app displays:
- Total URLs processed
- Success count (2xx status codes)
- Redirect count (3xx status codes)
- Error count (4xx/5xx status codes)
- Status code distribution table
- Detailed results with all redirect URLs
- Color-coded status indicators:
  - 🟢 2xx (Success)
  - 🟡 3xx (Redirect)
  - 🟠 4xx (Client Error)
  - 🔴 5xx (Server Error)
  - ⚪ Timeout/Error

## CSV Format

### Input CSV
```csv
URLs To Check
https://example.com
https://google.com
https://redirect-site.com
```

### Output CSV
The results include:
- URLs To Check
- Status Code
- Final URL
- URL 1 through URL 5 (redirect chain)

## Tips

- Adjust the delay between requests to be respectful to servers
- Increase max workers for faster processing (but be mindful of rate limits)
- Use custom headers if you need to authenticate or identify your requests
- Filter results by status code to focus on specific issues

## Requirements

- Python 3.8+
- streamlit >= 1.28.0
- pandas >= 1.5.0
- curl-cffi >= 0.5.0

## License

Free to use and modify.
