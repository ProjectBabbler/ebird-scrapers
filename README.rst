eBird Scrapers
==============
Although eBird has an API, not all the information from the database is
available. The API, for example, does not return links to any uploaded
photos; comments on an individual observation are also missing. eBird Scrapers
is a set of scrapers for extracting data from various pages on the eBird
web site. It complements the API, giving access to all the data that eBird
makes publicly available.

Install
-------
.. code-block:: console

    pip install ebird-scrapers

Usage
-----
Scraping the data from a page is as simple as a function call. For example
to get all the data from a checklist use get_checklist() and pass in the
unique identifier generated when the checklist was submitted to the eBird
database:

.. code-block:: python

    from ebird.scrapers import get_checklist

    data = get_checklist('S38429565')

The function returns a dict with keys for the location, date, observers, etc.

You can also get the complete list of checklists from the "Recent Checklists"
page, e.g. https://ebird.org/region/US-MA/recent-checklists. From there you
can download each checklist:

.. code-block:: python

    from ebird.scrapers import get_checklist, get_recent_checklists

    for item in get_recent_checklists("US-MA"):
        checklist = get_checklist(item["identifier"])

The data returned by ``get_checklist`` looks like this:

.. code-block:: python

    {
      "identifier": "S928130259",
      "date": datetime.datetime(2025, 2, 22, 10, 24),
      "observer": {
        "identifier": "USER000001",
        "name": "Etta Lemon"
      },
      "participants": [
        {
          "identifier": "USER000002",
          "name": "Catherine Hall",
        }
      ],
      "protocol": {
        "name": "Stationary"
      },
      "location": {
        "name": "Turkey Hill Meadow Natural Area",
        "identifier": "L11485440",
        "subnational2": "Tompkins County",
        "subnational2_code": "US-NY-109",
        "subnational1": "New York",
        "subnational1_code": "US-NY",
        "country": "United States",
        "country_code": "US",
        "lat": "42.4410439",
        "lon": "-76.430538"
      },
      "entries": [
        {
          "species": "Mourning Dove",
          "count": 3,
          "comments": "Three individuals",
          "media": [
            {"identifier": "235672715"},
            {"identifier": "235672716"},
            {"identifier": "235672718"}
          ]
        },
        {
          "species": "Red-tailed Hawk (borealis)",
          "count": 1
        },
        {
          "species": "European Starling",
          "count": 75
          "comments": "Single flock.",
        },
        {
          "species": "Eastern Bluebird",
          "count": 2,
        },
        {
          "species": "American Robin",
          "count": 24
        },
        {
          "species": "Red-winged Blackbird (Red-winged)",
          "count": 13
        },
        {
          "species": "Common Grackle (Bronzed)",
          "count": 1
        }
      ],
      "comment": "Partly cloudy 39.9°F (4.4°C) Humidity: 93%Wind: SSW 4 mph (Gusts: 6.8 mph) Barometer: 29.7 in (1006 mb) Visibility: 9 miLast Update: 25 Feb 16:45\nSubmitted from eBird for iOS, version 3.2.16",
      "complete": True
    }

Compatibility
-------------
ebird-scrapers works with all currently supported versions of Python (3.8+).

License
-------
eBird Scrapers is available under the terms of the [MIT](https://opensource.org/licenses/MIT) license.
