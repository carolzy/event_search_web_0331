#!/usr/bin/env python3
"""
Simple Luma Event Scraper

This is a simplified version of the Luma event scraper that just searches for events
and prints the results without trying to add them to a calendar.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the simple Luma event scraper."""
    # Initialize WebDriver
    logger.info("Initializing WebDriver")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        wait = WebDriverWait(driver, 20)
        
        # Navigate to Luma discover page
        logger.info("Navigating to Luma discover page")
        driver.get("https://lu.ma/discover")
        time.sleep(3)
        
        # Wait for discover page to load
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Discover') or contains(text(), 'Events')]"))
        )
        
        logger.info("Successfully navigated to discover page")
        
        # Find events
        logger.info("Finding events")
        event_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'event-card') or contains(@class, 'event-item')]")
        
        if not event_elements:
            logger.info("No events found using primary selector, trying alternative")
            # Try alternative selectors
            event_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/event/')]")
        
        logger.info(f"Found {len(event_elements)} events")
        
        # Extract event details
        events = []
        for i, element in enumerate(event_elements[:5]):  # Limit to first 5 events
            try:
                # Extract event title
                title_element = element.find_element(By.XPATH, ".//h2 | .//h3 | .//div[contains(@class, 'title')]")
                title = title_element.text.strip()
                
                # Extract event URL
                url = element.get_attribute("href")
                if not url:
                    url_element = element.find_element(By.XPATH, ".//a")
                    url = url_element.get_attribute("href")
                
                # Add to events list
                events.append({
                    "title": title,
                    "url": url
                })
                
                logger.info(f"Event {i+1}: {title} - {url}")
                
            except Exception as e:
                logger.error(f"Error extracting event data: {str(e)}")
                continue
        
        # Print summary
        print("\nLuma Events Summary:")
        print(f"Total events found: {len(events)}")
        for i, event in enumerate(events):
            print(f"{i+1}. {event['title']}")
            print(f"   URL: {event['url']}")
            print()
        
        return 0
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1
        
    finally:
        # Clean up
        if driver:
            logger.info("Closing WebDriver")
            driver.quit()

if __name__ == "__main__":
    main()
