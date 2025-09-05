from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import re

class CentralizedJobScraper:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, self.config['wait_time'])
    
    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        selenium_config = self.config['selenium_config']
        
        if 'chrome_options' in selenium_config:
            for option in selenium_config['chrome_options']:
                options.add_argument(option)
        
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(150)
        
        # Set user agent to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def scrape_jobs(self, url=None):
        if not url:
            url = self.config['base_url']
        
        print(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(self.config['scroll_pause_time'])
        
        # Handle any pop-ups or overlays
        self._handle_popups()
        
        # Scroll to load content if needed
        self._scroll_to_load_all()
        
        # Extract jobs using config-driven approach
        jobs = self._extract_jobs_from_config()
        
        return jobs
    
    def _handle_popups(self):
        """Handle common popups that might block content"""
        popup_selectors = [
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Close')]", 
            "//button[@aria-label='Close']",
            "//*[@class='close']",
            "//div[@class='modal']//button"
        ]
        
        for selector in popup_selectors:
            try:
                popup = self.driver.find_element(By.XPATH, selector)
                if popup.is_displayed():
                    popup.click()
                    time.sleep(1)
                    break
            except:
                continue
    
    def _extract_jobs_from_config(self):
        jobs = []
        container_config = self.config['selectors']['job_container']
        
        try:
            # Wait for page to load
            time.sleep(3)
            
            # Find job containers using config selector
            if container_config['selector_type'] == 'xpath':
                job_containers = self.driver.find_elements(By.XPATH, container_config['selector'])
            else:
                job_containers = self.driver.find_elements(By.CSS_SELECTOR, container_config['selector'])
            
            print(f"Found {len(job_containers)} job containers using selector: {container_config['selector']}")
            
            # If no containers found, try alternative detection
            if not job_containers:
                print("No job containers found, trying alternative detection...")
                job_containers = self._find_alternative_job_containers()
            
            for i, container in enumerate(job_containers, 1):
                try:
                    job_data = self._extract_job_data_from_container(container, i)
                    
                    if job_data and job_data.get('job_role') and job_data['job_role'] != 'Not specified':
                        jobs.append(job_data)
                        print(f"Extracted job {i}: {job_data['job_role']}")
                        
                except Exception as e:
                    print(f"Error extracting job {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding job containers: {e}")
        
        return jobs
    
    def _find_alternative_job_containers(self):
        """Try alternative methods to find job containers"""
        alternative_selectors = [
            "//div[contains(@class, 'job')]",
            "//article[contains(@class, 'job')]",
            "//li[contains(@class, 'job')]",
            ".job-item",
            ".job-listing",
            ".career-item",
            "div[data-job]"
        ]
        
        for selector in alternative_selectors:
            try:
                if selector.startswith('//'):
                    containers = self.driver.find_elements(By.XPATH, selector)
                else:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if containers:
                    print(f"Found {len(containers)} containers with alternative selector: {selector}")
                    return containers
            except:
                continue
        
        return []
    
    def _extract_job_data_from_container(self, container, job_index):
        job_data = {}
        selectors = self.config['selectors']
        
        # Extract required fields: job_role, job_experience, job_location
        required_fields = ['job_role', 'job_experience', 'job_location']
        
        for field_name in required_fields:
            if field_name in selectors:
                field_config = selectors[field_name]
                value = self._extract_field_value(container, field_config, field_name, job_index)
                
                # Clean and process the extracted value
                value = self._clean_text(value)
                
                job_data[field_name] = value
        
        return job_data
    
    def _extract_field_value(self, container, field_config, field_name, job_index):
        # Handle static values
        if field_config.get('type') == 'static':
            return field_config.get('value', 'Not specified')
        
        # Try primary selector
        value = self._try_extract_with_selector(container, field_config['primary'], field_name)
        
        # Try fallback selectors
        if not value and 'fallback' in field_config:
            for i, fallback in enumerate(field_config['fallback']):
                value = self._try_extract_with_selector(container, fallback, f"{field_name}_fallback_{i}")
                if value:
                    break
        
        # Try smart extraction based on context
        if not value:
            value = self._smart_extract_field(container, field_name)
        
        return value if value else 'Not specified'
    
    def _try_extract_with_selector(self, container, selector_config, debug_name):
        try:
            selector = selector_config['selector']
            selector_type = selector_config['selector_type']
            
            if selector_type == 'xpath':
                elements = container.find_elements(By.XPATH, selector)
            else:
                elements = container.find_elements(By.CSS_SELECTOR, selector)
            
            if elements:
                text = elements[0].text.strip()
                
                # Try getting text from attribute if text is empty
                if not text and 'attribute' in selector_config:
                    text = elements[0].get_attribute(selector_config['attribute'])
                
                if text:
                    return text
                    
        except Exception as e:
            pass  # Silently fail and try next selector
            
        return None
    
    def _smart_extract_field(self, container, field_name):
        """Smart extraction based on common patterns"""
        try:
            container_text = container.text.lower()
            
            if field_name == 'job_experience':
                # Look for experience patterns
                experience_patterns = [
                    r'(\d+[\-\+\s]*(?:to\s*)?(?:\d+)?\s*(?:years?|yrs?))',
                    r'experience[:\s]*(\d+[\-\+\s]*(?:to\s*)?(?:\d+)?\s*(?:years?|yrs?))',
                    r'(\d+[\-\+]\s*years?)',
                    r'(fresher|entry.level)',
                    r'(senior|lead|principal)',
                ]
                
                for pattern in experience_patterns:
                    match = re.search(pattern, container_text, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
            
            elif field_name == 'job_location':
                # Look for location patterns
                location_patterns = [
                    r'(ahmedabad|mumbai|delhi|bangalore|chennai|hyderabad|pune)',
                    r'(wfo|wfh|work\s+from\s+office|work\s+from\s+home|remote)',
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, container_text, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
        
        except:
            pass
        
        return None
    
    def _clean_text(self, text):
        """Clean extracted text"""
        if not text or text == 'Not specified':
            return 'Not specified'
        
        # Remove extra whitespace and clean up
        text = ' '.join(text.split())
        
        # Remove common prefixes
        prefixes_to_remove = ['Experience:', 'Location:', 'Role:', 'Position:', '-']
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text if text else 'Not specified'
    
    def _scroll_to_load_all(self):
        """Scroll to load all content"""
        if self.config.get('infinite_scroll', False):
            # For infinite scroll pages
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.config['scroll_pause_time'])
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        else:
            # Regular scroll for static content
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.config['scroll_pause_time'])
    
    def save_jobs_to_file(self, jobs, filename=None):
        """Save jobs to JSON file"""
        if not filename:
            site_name = self.config['site_name'].replace(' ', '_').lower()
            filename = f"{site_name}_jobs.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'site_name': self.config['site_name'],
                'scrape_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_jobs': len(jobs),
                'jobs': jobs
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Jobs saved to {filename}")
    
    def close(self):
        self.driver.quit()

# Usage
if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "motadata_careers_config.json"  # Default config

    if not os.path.exists(config_file):
        print(f"Config file {config_file} not found!")
        sys.exit(1)

    scraper = CentralizedJobScraper(config_file)
    
    try:
        jobs = scraper.scrape_jobs()
        
        print(f"\n{'='*80}")
        print(f"SCRAPING RESULTS FOR: {scraper.config['site_name']}")
        print(f"{'='*80}")
        print(f"Found {len(jobs)} jobs:")
        
        if jobs:
            for i, job in enumerate(jobs, 1):
                print(f"\n{i}. Role: {job.get('job_role', 'N/A')}")
                print(f"   Experience: {job.get('job_experience', 'N/A')}")
                print(f"   Location: {job.get('job_location', 'N/A')}")
        else:
            print("\nNo jobs found. Please check the configuration file.")
        
        # Save to file
        if jobs:
            scraper.save_jobs_to_file(jobs)
        
        print(f"\nTotal jobs scraped: {len(jobs)}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()