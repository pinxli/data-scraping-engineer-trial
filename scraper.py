
import json
# import logging

from playwright.sync_api import sync_playwright, Playwright

# To Do:
# - add error handling

BASE_URL = "https://scraping-trial-test.vercel.app"
OUTPUT_FILE = "output.json"
SEARCH_QUERY = "farms corp"
DELAY = 1

# logging.basicConfig(
#     filename="logs/scraper.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )


def _process_data(row, page):
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

    res = {
        "business_name": business_name,
        "registration_id": registration_id,
        "status": status,
        "filing_date": filing_date,
        "agent_name": agent_name,
        "agent_address": agent_address,
        "agent_email": agent_email
    }
    return res

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto(BASE_URL)
    
    # Captcha
    print("Please solve the CAPTCHA manually in the browser.")
    input("Press ENTER after CAPTCHA is solved...")

    # Search
    page.fill("input[id='q']", SEARCH_QUERY)
    page.click("button:has-text('Search')")

    results = []
    while True:
        page.wait_for_selector("table tbody tr")
        
        rows = page.locator("table tbody tr")
        rows_count = rows.count()
        for i in range(rows_count):
            row = rows.nth(i)
            res = _process_data(row, page)
            
            results.append(res)
            print("\n\n", res)

        next_button = page.locator("button.page-btn", has_text="Next")
        
        if next_button.is_disabled():
            print("Next button is disabled. Reached last page.")
            break

        next_button.click()
        page.wait_for_selector(".table-wrap")

    browser.close()



if __name__ == "__main__":
    with sync_playwright() as playwright:
        results = run(playwright)

    # logging.info(f"Scraping completed. Total records: {len(results)}")

    # # Save output
    # with open(OUTPUT_FILE, "w") as f:
    #     json.dump(all_records, f, indent=4)
    # logging.info(f"Results saved to {OUTPUT_FILE}")