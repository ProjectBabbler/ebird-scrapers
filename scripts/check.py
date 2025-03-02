"""
Simple script to verify the Recent Checklists and Checklist pages
can be scraped successfully.

Run this script via cron, with email enabled, to get a daily, weekly,
etc. report that format of the webpages has not changed.


"""

from faker import Faker

from ebird.scrapers import get_checklist, get_recent_checklists

fake = Faker()


if __name__ == "__main__":
    region = fake.country_code()
    print("Scraping Recent Checklists page:", region)
    for checklist in get_recent_checklists(region)[:10]:
        identifier = checklist["identifier"]
        print("Scraping Checklist page:", identifier)
        get_checklist(identifier)
    print("Pages scraped successfully")
