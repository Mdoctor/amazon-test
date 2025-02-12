# Amazon Product Scraper

A high-performance parallel web scraper for Amazon product data using Python. This scraper is designed to efficiently collect product information from multiple Amazon category pages simultaneously.

## Features

- Parallel scraping using multiple workers
- Configurable scraping parameters
- Robust error handling and logging
- Automated web driver management
- Support for multiple Amazon categories
- Data persistence capabilities

## Prerequisites

- Python 3.11+
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd amazon-test
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

The scraper can be configured through `config.py`. Key configuration options include:

- `MAX_WORKERS`: Number of parallel scraping workers
- `RETRY_COUNT`: Number of retry attempts for failed requests
- `TIMEOUT`: Request timeout duration
- `USER_AGENT`: Custom user agent string
- Other scraping parameters

## Usage

1. Basic usage:
```python
from parallel_scraper import ParallelScraper
from config import ScraperConfig

# Initialize scraper
scraper = ParallelScraper(ScraperConfig.MAX_WORKERS)

# Define target URLs
category_urls = [
    "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/",
    "https://www.amazon.com/Best-Sellers-Amazon-Renewed/zgbs/amazon-renewed/"
]

# Run scraper
results = scraper.run_parallel(category_urls)
```

2. Run from command line:
```bash
python main.py
```

## Project Structure

```
amazon-test/
├── main.py              # Main entry point
├── parallel_scraper.py  # Parallel scraping implementation
├── scraper.py          # Core scraping logic
├── config.py           # Configuration settings
├── logger.py           # Logging setup
├── driver_manager.py   # Webdriver management
├── data_saver.py       # Data persistence
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## Output

The scraper collects the following data for each product:
- Product details
- Pricing information
- Category information
- Other relevant metadata

Results are logged and can be saved in various formats.

## Error Handling

The scraper includes robust error handling:
- Automatic retry for failed requests
- Detailed error logging
- Exception management for common scraping issues

## Logging

Comprehensive logging is implemented through `logger.py`:
- Success/failure statistics
- Error details
- Scraping progress updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Disclaimer

This scraper is for educational purposes only. Ensure compliance with Amazon's terms of service and robots.txt when using this tool.

## Support

For issues, questions, or contributions, please create an issue in the repository.