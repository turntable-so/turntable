import intellisense.syntax.scrapers as scrapers

if __name__ == "__main__":
    for dialect in [
        "snowflake",
        "bigquery",
        "databricks",
        "redshift",
    ]:
        scraper_ = getattr(scrapers, f"{dialect.upper()}scraper")()
        scraper_.scrape_keywords()
        scraper_.scrape_functions()
        scraper_.to_json(f"intellisense/syntax/outputs/{dialect}.json")
        del scraper_  # closes connection
