from selectorlib import Extractor
import requests
import json
import os
import time

class CentralizedJobScraper:
    def __init__(self, yml_file, site_name):
        self.extractor = Extractor.from_yaml_file(yml_file)
        self.site_name = site_name

    def scrape_jobs(self, url):
        response = requests.get(url)
        response.encoding = "utf-8"
        html = response.text
        data = self.extractor.extract(html)
        return data['jobs'] if 'jobs' in data else data

    def save_jobs_to_file(self, jobs):
        save_dir = os.path.join("scraped_jobs")
        os.makedirs(save_dir, exist_ok=True)
        filename = f"{self.site_name.lower().replace(' ', '_')}_jobs.json"
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'site_name': self.site_name,
                'scrape_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_jobs': len(jobs) if isinstance(jobs, list) else 1,
                'jobs': jobs
            }, f, indent=2, ensure_ascii=False)
        print(f"✅ Jobs saved to {filepath}")

# # Usage
# scraper = CentralizedJobScraper("motadata.yml", "Motadata")
# jobs = scraper.scrape_jobs("https://www.motadata.com/careers/")
# scraper.save_jobs_to_file(jobs)
