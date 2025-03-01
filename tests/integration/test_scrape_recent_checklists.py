import time

import pytest

from ebird.scrapers import get_checklist, get_recent_checklists


def get_identifiers():
    for checklist in get_recent_checklists("US-NY-109"):
        yield checklist["identifier"]


@pytest.mark.parametrize("identifier", get_identifiers())
def test_scrape_recent_checklists(identifier):
    get_checklist(identifier)
    time.sleep(10)
