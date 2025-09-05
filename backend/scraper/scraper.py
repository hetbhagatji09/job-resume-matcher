import json
import os
from main import CentralizedJobScraper
def scrape_jobs_from_url(url: str):
    """Takes a job site URL, loads matching config, scrapes jobs, and returns them as a list."""

    # Load mapping
    with open("config_map.json", "r") as f:
        config_map = json.load(f)

    # Lookup config file
    config_file = config_map.get(url)
    if not config_file:
        raise ValueError(f"No config found for URL: {url}")

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found!")

    scraper = CentralizedJobScraper(config_file)
    jobs = []

    try:
        jobs = scraper.scrape_jobs()
        if jobs:
            scraper.save_jobs_to_file(jobs)
        return jobs
    finally:
        scraper.close()