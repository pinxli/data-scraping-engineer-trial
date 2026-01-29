import os
import json
import time
import logging

from playwright.sync_api import sync_playwright, Playwright

BASE_URL = "https://scraping-trial-test.vercel.app"
OUTPUT_FILE = "output.json"
SEARCH_QUERY = "farms corp"
DELAY = 1

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler()
    ]
)

def _manual_captcha():
    print("Please solve the CAPTCHA manually in the browser.")
    input("Press ENTER after CAPTCHA is solved...")

def _process_data(row, page):
    try:
        business_name = row.locator("td:nth-child(1)").inner_text().strip()
        registration_id = row.locator("td:nth-child(2)").inner_text().strip()
        status = row.locator("td:nth-child(3)").inner_text().strip()
        filing_date = row.locator("td:nth-child(4)").inner_text().strip()
        
        row.locator("td:nth-child(1) a").click()
        page.wait_for_selector("div.small.muted:has-text('Registered Agent')")

        agent_card = page.locator("div.small.muted", has_text="Registered Agent")
        agent_card = agent_card.locator("..")

        agent_name = agent_card.locator("div").nth(1).inner_text().strip()
        agent_address = agent_card.locator("div").nth(2).inner_text().strip()
        agent_email = agent_card.locator("code").inner_text().strip()
        page.go_back()
        page.wait_for_load_state("domcontentloaded")

        return {
            "business_name": business_name,
            "registration_id": registration_id,
            "status": status,
            "filing_date": filing_date,
            "agent_name": agent_name,
            "agent_address": agent_address,
            "agent_email": agent_email
        }
    except Exception as e:
        logging.error(f"Failed to process data. \n {e}")
        return None

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        page.goto(BASE_URL)
    except Exception as e:
        logging.error(f"Failed to load page. \n {e}")
        return
    
    # Captcha
    _manual_captcha()

    # Search
    try:
        page.fill("input[id='q']", SEARCH_QUERY)
        page.click("button:has-text('Search')")
    except Exception as e:
        logging.error(f"Failed to perform search. \n {e}")
        return

    current_page = 1
    results = []
    while True:
        logging.info(f"Processing page {current_page}...")

        page.wait_for_selector("table tbody tr")
        
        rows = page.locator("table tbody tr")
        rows_count = rows.count()
        for i in range(rows_count):
            row = rows.nth(i)
            res = _process_data(row, page)
            
            if not res:
                logging.warning(f"Failed to process record {i + 1} in page {current_page}. Skipping...")
                continue
            
            results.append(res)
            logging.info(f"Record processed. {res['business_name']}")

            time.sleep(DELAY / 5) # row delay

        next_button = page.locator("button.page-btn", has_text="Next")
        
        try:
            if next_button.is_disabled():
                logging.info("Reached last page.")
                break
        except Exception as e:
            logging.error(f"Next button not found or disabled check failed. \n {e}")
            break

        first_row_text = rows.first.inner_text()

        next_button.click()
        time.sleep(DELAY) # page delay

        current_page += 1
        
        page.wait_for_function(
            """prev => {
                const row = document.querySelector("table tbody tr");
                return row && row.innerText !== prev;
            }""",
            arg=first_row_text
        )

    browser.close()
    return results


if __name__ == "__main__":
    with sync_playwright() as playwright:
        results = run(playwright)

    logging.info(f"Scraping completed. Total records: {len(results)}")

    # Save output
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=4)
    logging.info(f"Results saved to {OUTPUT_FILE}")