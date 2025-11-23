import json
import os
from scraper.centralized_scraper import CentralizedJobScraper

def scrape_jobs_from_url(url: str):
    """Takes a job site URL, loads matching config, scrapes jobs, and returns them as a list."""

    # Resolve base directory dynamically
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_map_path = os.path.join(base_dir, "config_map.json")

    # Load mapping from JSON
    with open(config_map_path, "r") as f:
        config_map = json.load(f)

    # 🔍 Match by prefix instead of exact key
    config_name = None
    for base_url, file_name in config_map.items():
        if url.startswith(base_url):
            config_name = file_name
            break

    if not config_name:
        raise ValueError(f"No matching config found for URL: {url}")

    # Build the full config file path
    config_file = os.path.join(base_dir, config_name)
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found!")

    # Dynamically extract site name for logging
    site_name = os.path.splitext(config_name)[0].capitalize()

    scraper = CentralizedJobScraper(config_file, site_name)
    print(f"🧩 Using config: {config_file}")

    try:
        jobs = scraper.scrape_jobs(url)
        print("✅ Extracted jobs:")
        if jobs:
            scraper.save_jobs_to_file(jobs)
        return jobs
    except Exception as e:
        print("❌ Error during scraping:", e)
        return []
