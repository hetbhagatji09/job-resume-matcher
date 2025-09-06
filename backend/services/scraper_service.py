from scraper.scraper_func import scrape_jobs_from_url
def scrape_jobs(url:str):
    jobs=scrape_jobs_from_url(url)
    return jobs
    
    