from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import random
import re
import requests

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_with_requests(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Requests failed: {e}")
        return None

def extract_college_data(soup):
    colleges = []
    cards = soup.find_all("div", id=re.compile(r'^rp_tuple_\d+'))
    if not cards:
        fallback_selectors = [
            "div.tuple-clg", "div[class*='tuple']", "div[class*='college']",
            "div[class*='card']", ".ranking-item", ".college-item"
        ]
        for selector in fallback_selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Found {len(cards)} cards with fallback selector: {selector}")
                break

    print(f"Found {len(cards)} college cards to extract.")
    for i, card in enumerate(cards):
        college_info = {}

        # College Name
        name_elem = card.find("a", class_=re.compile(r"rank_clg|tuple-clg-name|tuple-clg-heading", re.IGNORECASE))
        if not name_elem:
            name_elem = card.find("a")
        if name_elem:
            college_info["name"] = name_elem.get_text(strip=True)
        else:
            continue

        # Ranking
        rank_elem = card.find("div", class_=re.compile(r"rank", re.IGNORECASE))
        if rank_elem:
            rank_match = re.search(r'(\d+)', rank_elem.get_text(strip=True))
            college_info["ranking"] = rank_match.group(1) if rank_match else None
        else:
            college_info["ranking"] = None

        # Fees and Salary
        fees = None
        salary = None
        info_elems = card.find_all("div", class_=re.compile(r"flex_v\s+text--secondary"))
        for elem in info_elems:
            label_elem = elem.find("span")
            if label_elem:
                label_text = label_elem.get_text(strip=True).lower()
                value_text = elem.get_text(strip=True)
                if 'fees' in label_text:
                    fees_match = re.search(r'₹[\d,.\s]+(Lakh|Lac|Crore)?', value_text, re.IGNORECASE)
                    if fees_match:
                        fees = fees_match.group().replace('\xa0', ' ')
                elif 'salary' in label_text:
                    salary_match = re.search(r'₹[\d,.\s]+(Lakh|Lac|Crore)?', value_text, re.IGNORECASE)
                    if salary_match:
                        salary = salary_match.group().replace('\xa0', ' ')

        # Fallback text search (just in case)
        text = card.get_text(separator=" ", strip=True)
        if not fees:
            fees_match = re.search(r'Fees:\s*(₹[\d,.\s]+(Lakh|Lac|Crore)?)', text, re.IGNORECASE)
            if fees_match:
                fees = fees_match.group(1).replace('\xa0', ' ')
        if not salary:
            salary_match = re.search(r'Salary:\s*(₹[\d,.\s]+(Lakh|Lac|Crore)?)', text, re.IGNORECASE)
            if salary_match:
                salary = salary_match.group(1).replace('\xa0', ' ')

        college_info["fees"] = fees
        college_info["salary"] = salary

        college_info["card_index"] = i + 1
        colleges.append(college_info)

    return colleges

def main():
    print("Starting Shiksha Scraper...")

    base_url = "https://www.shiksha.com/engineering/ranking/top-engineering-colleges-in-india/44-2-0-0-0"
    all_colleges = []

    driver = setup_driver()
    for page in range(1, 5):
        url = f"{base_url}?pageNo={page}" if page > 1 else base_url
        print(f"\nScraping Page {page}: {url}")

        html_content = None
        try:
            driver.get(url)
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[id^='rp_tuple_']"))
            )
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
            html_content = driver.page_source
            print(f"Content fetched for Page {page} using Selenium")
        except Exception as e:
            print(f"Selenium failed on Page {page}: {e}")

        if not html_content:
            print("Trying with requests fallback...")
            html_content = scrape_with_requests(url)
            if html_content:
                print("Content fetched with requests.")
            else:
                print(f"Failed to fetch content for Page {page}")
                continue

        soup = BeautifulSoup(html_content, "html.parser")
        page_colleges = extract_college_data(soup)
        if page_colleges:
            for college in page_colleges:
                college["page"] = page
            all_colleges.extend(page_colleges)
            print(f"Extracted {len(page_colleges)} colleges from Page {page}")
        else:
            print(f"No colleges extracted from Page {page}")
            with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
                f.write(html_content)

    driver.quit()
    if all_colleges:
        with open("colleges_simple.json", "w", encoding="utf-8") as f:
            json.dump(all_colleges, f, indent=4, ensure_ascii=False)
        print(f"\nSuccessfully scraped {len(all_colleges)} colleges!")
    else:
        print("\nNo colleges were scraped.")

if __name__ == "__main__":
    main()
