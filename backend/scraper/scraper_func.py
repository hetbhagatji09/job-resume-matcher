import json
import os
from scraper.centralized_scraper import CentralizedJobScraper

def scrape_jobs_from_url(url: str):
    """Takes a job site URL, loads matching config, scrapes jobs, and returns them as a list."""

    # Resolve base directory dynamically
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_map_path = os.path.join(base_dir, "config_map.json")

    with open(config_map_path, "r") as f:
        config_map = json.load(f)

    config_name = config_map.get(url)
    if not config_name:
        raise ValueError(f"No config found for URL: {url}")

    config_file = os.path.join(base_dir, config_name)
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found!")

    scraper = CentralizedJobScraper(config_file, "Motadata")
    print("my config is this →", config_file)

    try:
        jobs = scraper.scrape_jobs(url)
        print("those are the jobs →", jobs)
        if jobs:
            scraper.save_jobs_to_file(jobs)
        return jobs
    except Exception as e:
        print("❌ Error during scraping:", e)
        return []
