#!/usr/bin/env python3
"""
Luma SF Events Detailed Scraper (Mac ARM Compatible)

This script automates searching for events on Luma SF page and extracts detailed information
by clicking into each event page. It captures event title, speakers, summary, and link.

Usage:
    python luma_sf_events_detailed.py --keywords "AI"
    python luma_sf_events_detailed.py --keywords "founder,startup,tech" --max-events 20
"""

import os
import sys
import time
import logging
import argparse
import datetime
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("luma_events.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Luma SF Events Detailed Scraper')
    
    # Search parameters
    parser.add_argument('--keywords', required=True, help='Comma-separated keywords to search for events (e.g., "AI,tech,startup")')
    parser.add_argument('--max-events', type=int, default=10, help='Maximum number of events to discover (default: 10)')
    parser.add_argument('--wait-time', type=int, default=5, help='Wait time in seconds for page loading (default: 5)')
    
    # Browser parameters
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--screenshots', action='store_true', help='Save screenshots during execution')
    parser.add_argument('--chromedriver-path', help='Path to chromedriver executable (optional)')
    
    # Output parameters
    parser.add_argument('--output', help='Output file to save discovered events (default: sf_events_detailed.txt)')
    
    return parser.parse_args()

def search_for_events(driver, keywords, wait_time=5, take_screenshots=False):
    """
    Search for events using Luma's search functionality on the SF page.
    
    Args:
        driver: WebDriver instance
        keywords: Keywords to search for
        wait_time: Time to wait for page loading in seconds
        take_screenshots: Whether to save screenshots
        
    Returns:
        bool: True if search successful, False otherwise
    """
    try:
        # Navigate directly to Luma SF page
        logger.info("Navigating to Luma SF page")
        driver.get("https://lu.ma/sf")
        time.sleep(wait_time)
        
        if take_screenshots:
            driver.save_screenshot("sf_page.png")
            logger.info("Screenshot saved: sf_page.png")
        
        # Look for search button/icon
        logger.info("Looking for search button")
        search_buttons = []
        
        # Try different approaches to find the search button
        try:
            # Try to find by aria-label
            search_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'search') or contains(@aria-label, 'Search')]")
            
            if not search_buttons:
                # Try to find by icon
                search_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'search') or .//i[contains(@class, 'search')]]")
                
            if not search_buttons:
                # Try to find by SVG icon
                search_buttons = driver.find_elements(By.XPATH, "//button[.//svg[contains(@class, 'search')]]")
                
            if not search_buttons:
                # Try to find by text content
                search_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Search') or .//span[contains(text(), 'Search')]]")
                
            if not search_buttons:
                # Try to find search input directly
                search_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'search') or contains(@placeholder, 'Search') or contains(@aria-label, 'search')]")
                if search_inputs:
                    logger.info("Found search input directly")
                    search_input = search_inputs[0]
                    search_input.click()
                    time.sleep(1)
                    
                    if take_screenshots:
                        driver.save_screenshot("search_input_clicked.png")
                    
                    # Enter search keywords
                    search_input.clear()
                    search_input.send_keys(keywords)
                    time.sleep(1)
                    search_input.send_keys(Keys.ENTER)
                    logger.info(f"Entered search keywords: {keywords}")
                    
                    if take_screenshots:
                        driver.save_screenshot("search_submitted.png")
                    
                    time.sleep(wait_time)
                    return True
        except Exception as e:
            logger.error(f"Error finding search button: {str(e)}")
        
        # If we found search buttons
        if search_buttons:
            logger.info(f"Found {len(search_buttons)} potential search buttons")
            
            # Click the first search button
            search_buttons[0].click()
            logger.info("Clicked search button")
            time.sleep(1)
            
            if take_screenshots:
                driver.save_screenshot("search_button_clicked.png")
            
            # Now look for the search input field
            try:
                search_input = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'search') or contains(@placeholder, 'Search') or contains(@aria-label, 'search')]"))
                )
                
                # Enter search keywords
                search_input.clear()
                search_input.send_keys(keywords)
                time.sleep(1)
                search_input.send_keys(Keys.ENTER)
                logger.info(f"Entered search keywords: {keywords}")
                
                if take_screenshots:
                    driver.save_screenshot("search_submitted.png")
                
                time.sleep(wait_time)
                return True
                
            except TimeoutException:
                logger.error("Could not find search input field after clicking search button")
                
                if take_screenshots:
                    driver.save_screenshot("search_input_not_found.png")
                
                return False
        
        # If we couldn't find the search button, try navigating directly to the search URL
        logger.info("Could not find search button, trying direct search URL")
        
        # Format keywords for URL
        url_keywords = keywords.replace(',', '+').replace(' ', '+')
        
        # Navigate to search URL with SF filter
        search_url = f"https://lu.ma/search?q={url_keywords}&filter=sf"
        logger.info(f"Navigating to search URL: {search_url}")
        driver.get(search_url)
        
        if take_screenshots:
            driver.save_screenshot("direct_search_url.png")
        
        time.sleep(wait_time)
        return True
        
    except Exception as e:
        logger.error(f"Failed to search for events: {str(e)}")
        if take_screenshots:
            driver.save_screenshot("search_error.png")
        return False

def find_event_links(driver, max_events=10, wait_time=5, take_screenshots=False):
    """
    Find event links from the search results page.
    
    Args:
        driver: WebDriver instance
        max_events: Maximum number of events to find
        wait_time: Time to wait for page loading in seconds
        take_screenshots: Whether to save screenshots
        
    Returns:
        list: List of event URLs
    """
    try:
        logger.info(f"Finding up to {max_events} event links from search results")
        
        # Wait for search results to load
        time.sleep(wait_time)
        
        if take_screenshots:
            driver.save_screenshot("search_results.png")
        
        # Log current URL
        logger.info(f"Current URL: {driver.current_url}")
        
        event_links = []
        
        # Try different approaches to find event links
        try:
            # First try: Find event cards and extract links
            event_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'event-card') or contains(@class, 'event-item')]")
            
            if event_elements:
                logger.info(f"Found {len(event_elements)} event cards")
                
                for element in event_elements:
                    if len(event_links) >= max_events:
                        break
                    
                    try:
                        link_element = element.find_element(By.XPATH, ".//a")
                        link = link_element.get_attribute("href")
                        
                        if link and ('/events/' in link or '/e/' in link):
                            event_links.append(link)
                            logger.info(f"Added event link: {link}")
                    except Exception as e:
                        logger.error(f"Error extracting link from event card: {str(e)}")
            
            # Second try: Find direct event links
            if len(event_links) < max_events:
                direct_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/events/') or contains(@href, '/e/')]")
                
                if direct_links:
                    logger.info(f"Found {len(direct_links)} direct event links")
                    
                    for link_element in direct_links:
                        if len(event_links) >= max_events:
                            break
                        
                        link = link_element.get_attribute("href")
                        
                        # Skip if already in list
                        if link in event_links:
                            continue
                        
                        event_links.append(link)
                        logger.info(f"Added event link: {link}")
            
            # Third try: Look for any links and filter
            if len(event_links) < max_events:
                all_links = driver.find_elements(By.TAG_NAME, "a")
                
                if all_links:
                    logger.info(f"Found {len(all_links)} total links, filtering for event links")
                    
                    for link_element in all_links:
                        if len(event_links) >= max_events:
                            break
                        
                        link = link_element.get_attribute("href")
                        
                        # Skip if not an event link or already in list
                        if not link or not ('/events/' in link or '/e/' in link) or link in event_links:
                            continue
                        
                        event_links.append(link)
                        logger.info(f"Added event link: {link}")
        
        except Exception as e:
            logger.error(f"Error finding event links: {str(e)}")
        
        logger.info(f"Found {len(event_links)} event links")
        return event_links
        
    except Exception as e:
        logger.error(f"Failed to find event links: {str(e)}")
        if take_screenshots:
            driver.save_screenshot("find_links_error.png")
        return []

def extract_event_details(driver, event_url, wait_time=5, take_screenshots=False):
    """
    Extract detailed information from an event page.
    
    Args:
        driver: WebDriver instance
        event_url: URL of the event page
        wait_time: Time to wait for page loading in seconds
        take_screenshots: Whether to save screenshots
        
    Returns:
        dict: Event details including title, speakers, summary, and link
    """
    try:
        logger.info(f"Extracting details from event: {event_url}")
        
        # Navigate to event page
        driver.get(event_url)
        time.sleep(wait_time)
        
        # Take screenshot of event page
        if take_screenshots:
            event_id = event_url.split("/")[-1]
            screenshot_file = f"event_{event_id}.png"
            driver.save_screenshot(screenshot_file)
            logger.info(f"Screenshot saved: {screenshot_file}")
        
        # Extract event title
        title = "Unknown Title"
        try:
            title_elements = driver.find_elements(By.XPATH, "//h1 | //h2[contains(@class, 'title')] | //div[contains(@class, 'title') and not(contains(@class, 'subtitle'))]")
            if title_elements:
                title = title_elements[0].text.strip()
                logger.info(f"Extracted event title: {title}")
        except Exception as e:
            logger.error(f"Error extracting event title: {str(e)}")
        
        # Extract speakers
        speakers = []
        try:
            # Try different approaches to find speakers
            speaker_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'speaker') or contains(@class, 'host')]")
            
            if not speaker_elements:
                # Try alternative selectors
                speaker_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Speaker') or contains(text(), 'Host')]/following-sibling::div")
            
            if not speaker_elements:
                # Try looking for profile pictures with names
                speaker_elements = driver.find_elements(By.XPATH, "//img[contains(@alt, 'profile') or contains(@class, 'avatar')]/parent::div/parent::div")
            
            for element in speaker_elements:
                speaker_text = element.text.strip()
                if speaker_text:
                    # Try to parse name, title, company
                    lines = speaker_text.split('\n')
                    name = lines[0] if lines else "Unknown"
                    title_company = ' '.join(lines[1:]) if len(lines) > 1 else ""
                    
                    speakers.append({
                        "name": name,
                        "title_company": title_company
                    })
            
            if speakers:
                logger.info(f"Extracted {len(speakers)} speakers")
            else:
                logger.info("No speakers found")
        except Exception as e:
            logger.error(f"Error extracting speakers: {str(e)}")
        
        # Extract event summary
        summary = "No summary available"
        try:
            # Try different approaches to find summary
            summary_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'description') or contains(@class, 'summary')]")
            
            if not summary_elements:
                # Try alternative selectors
                summary_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'About') or contains(text(), 'Description')]/following-sibling::div")
            
            if not summary_elements:
                # Try looking for paragraphs in the main content
                summary_elements = driver.find_elements(By.XPATH, "//main//p")
            
            if summary_elements:
                summary = summary_elements[0].text.strip()
                # Truncate if too long
                if len(summary) > 500:
                    summary = summary[:497] + "..."
                logger.info(f"Extracted event summary: {summary[:50]}...")
        except Exception as e:
            logger.error(f"Error extracting event summary: {str(e)}")
        
        return {
            "title": title,
            "speakers": speakers,
            "summary": summary,
            "url": event_url
        }
        
    except Exception as e:
        logger.error(f"Failed to extract event details: {str(e)}")
        return {
            "title": "Error extracting details",
            "speakers": [],
            "summary": f"Error: {str(e)}",
            "url": event_url
        }

def main():
    """Main function to run the Luma SF events detailed scraper."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set default output file if not specified
    if not args.output:
        keywords_slug = args.keywords.lower().replace(",", "_").replace(" ", "_")
        args.output = f"sf_events_detailed_{keywords_slug}.txt"
    
    # Initialize WebDriver
    logger.info("Initializing WebDriver")
    options = webdriver.ChromeOptions()
    if args.headless:
        logger.info("Running in headless mode")
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    driver = None
    
    try:
        # Initialize Chrome driver
        if args.chromedriver_path:
            # Use specified ChromeDriver path
            logger.info(f"Using ChromeDriver at: {args.chromedriver_path}")
            service = Service(executable_path=args.chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Let Selenium handle driver management (better for Mac ARM)
            logger.info("Using Selenium's built-in driver management")
            driver = webdriver.Chrome(options=options)
        
        driver.implicitly_wait(args.wait_time)
        logger.info(f"WebDriver initialized with wait time: {args.wait_time} seconds")
        
        # Search for events
        if not search_for_events(driver, args.keywords, args.wait_time, args.screenshots):
            logger.error("Failed to search for events. Exiting.")
            return 1
        
        # Find event links
        logger.info(f"Finding up to {args.max_events} event links")
        event_links = find_event_links(driver, max_events=args.max_events, wait_time=args.wait_time, 
                                      take_screenshots=args.screenshots)
        
        if not event_links:
            logger.error("No event links found. Exiting.")
            return 1
        
        logger.info(f"Found {len(event_links)} event links")
        
        # Extract details from each event
        events = []
        for i, link in enumerate(event_links, 1):
            logger.info(f"Processing event {i}/{len(event_links)}: {link}")
            event_details = extract_event_details(driver, link, args.wait_time, args.screenshots)
            events.append(event_details)
            
            # Add a short delay between requests to avoid rate limiting
            if i < len(event_links):
                time.sleep(2)
        
        # Save events to file
        with open(args.output, 'w') as f:
            f.write(f"Luma SF Events Detailed Results\n")
            f.write(f"Search keywords: {args.keywords}\n")
            f.write(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, event in enumerate(events, 1):
                f.write(f"Event {i}:\n")
                f.write(f"Title: {event.get('title', 'Unknown')}\n")
                
                # Write speakers
                speakers = event.get('speakers', [])
                if speakers:
                    f.write("Speakers:\n")
                    for speaker in speakers:
                        f.write(f"  - {speaker.get('name', 'Unknown')}")
                        if speaker.get('title_company'):
                            f.write(f", {speaker.get('title_company')}")
                        f.write("\n")
                else:
                    f.write("Speakers: None listed\n")
                
                # Write summary
                f.write(f"Summary: {event.get('summary', 'No summary available')}\n")
                f.write(f"URL: {event.get('url', 'Unknown')}\n")
                f.write("\n")
        
        # Report results
        logger.info("Event scraping completed successfully")
        logger.info(f"Total events processed: {len(events)}")
        logger.info(f"Events saved to: {args.output}")
        
        print(f"\nLuma SF Event Scraping Completed Successfully")
        print(f"Search keywords: {args.keywords}")
        print(f"Total events processed: {len(events)}")
        print(f"Events saved to: {args.output}")
        
        return 0
        
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        logger.error("This might be a ChromeDriver compatibility issue. Try specifying the path to a compatible ChromeDriver with --chromedriver-path.")
        return 1
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    finally:
        # Clean up
        if driver:
            logger.info("Closing WebDriver")
            driver.quit()

if __name__ == "__main__":
    sys.exit(main())
