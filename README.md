## How to install dependencies:

1. Python 3.11+ is required for this project.
2. It's recommended to use a virtual environment before installing dependencies.
3. Install the required packages:
```bash
pip install -r requirements.txt
```
requirements.txt includes all necessary packages used in this project.

## How to run the script:
```bash
python scraper.py
```
1. Manually solve reCAPTCHA when it appears in the browser.
2. The script will search for "farms corp" and scrape all results.
3. Results are saved in output.json file.
4. Logs are saved in logs/scraper.log and also displayed in terminal.

## Libraries Used:
- **playwright** - for manually solving captcha, navigation, and scraping page elements. Manual CAPTCHA handling is required because the API that provides the details requires a CAPTCHA token, so plain requests is not an option. 
- **logging** - for structured logging of progress and errors.
- **json** - to save scraped data in JSON format.
- **time and os** - for delays between actions and managing directory/files.

## Assumptions or Limitations:
- CAPTCHA must be solved manually
- The always starts from page 1. Resume functionality is not implemented.
- Rows that fail to process are skipped. No retry logic is included.


