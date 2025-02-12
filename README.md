# Amazon Best Sellers Scraper

A robust and efficient web scraper designed to extract product information from Amazon's Best Sellers categories. Built with Python, Selenium, and undetected-chromedriver for reliable data collection.

## Features

- Scrapes multiple Amazon Best Sellers categories
- Extracts detailed product information including:
  - Title
  - Price
  - Rating
  - Review Count
  - Product Description
  - ASIN (Amazon Standard Identification Number)
- Anti-detection measures implemented
- Automatic data export to Excel/CSV
- Configurable scraping parameters
- Comprehensive logging system
- Robust error handling and retry mechanisms

## Requirements

```
fake_useragent==2.0.3
pandas==2.2.3
selenium==4.28.1
undetected_chromedriver==3.5.5
```

## Project Structure

- `main.py` - Entry point of the application
- `scraper.py` - Core scraping functionality
- `config.py` - Configuration settings
- `logger.py` - Logging setup
- `driver_manager.py` - Selenium WebDriver management
- `data_saver.py` - Data export functionality

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd amazon-test
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Basic usage:
```python
python main.py
```

2. Configure category URLs in `main.py`:
```python
category_urls = [
    "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_amazon-devices_0",
    "https://www.amazon.com/Best-Sellers-Amazon-Renewed/zgbs/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0",
    # Add more categories as needed
]
```

3. Adjust scraping parameters in `config.py` if needed.

## Configuration

You can customize various parameters in `config.py`:

- `WAIT_TIME` - Maximum wait time for elements
- `MIN_SLEEP` - Minimum delay between actions
- `MAX_SLEEP` - Maximum delay between actions
- `SCROLL_STEPS` - Number of page scrolls
- Various selector configurations for different elements

## Output

The scraper saves data in two formats:

1. Excel (.xlsx) - Primary output format with formatted columns
2. CSV - Backup format if Excel export fails

Files are saved with the following naming pattern:
`{category_name}_bestsellers_{timestamp}.xlsx`

## Logging

- Logs are saved to `scraper.log`
- Console output is also provided
- Includes detailed information about:
  - Scraping progress
  - Errors and exceptions
  - Success/failure statistics

## Anti-Detection Features

- Uses undetected-chromedriver
- Random user agent generation
- Configurable delays between actions
- Browser fingerprint manipulation
- Incognito mode support

## Error Handling

- Automatic retry mechanism for failed requests
- Throttling detection and handling
- Multiple fallback selectors for each element
- Graceful degradation for missing data

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Disclaimer

This tool is for educational purposes only. Make sure to comply with Amazon's terms of service and robots.txt when using this scraper.