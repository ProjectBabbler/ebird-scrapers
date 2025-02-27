Change Log
==========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/).
This project adheres to [PEP440](https://www.python.org/dev/peps/pep-0440/)
and by implication, [Semantic Versioning](http://semver.org/).

[Unreleased]
------------
- Renamed the package to ebird.scrapers. ebird-pages is used for another project.
- Updated get_checklist to return the checklist owner.
- Updated get_checklist to return a list of other participants.
- Updated get_checklist to return the number of observers.
- Updated get_checklist to use table for extracting protocol values.

[0.2.0] - 2024-10-23
--------------------
- Added get_recent_checklists to scrape the "Recent Checklists" page
- Updated get_checklist now works with the latest page layout

[0.1] - 2017-08-21
------------------
- Added get_checklist for scraping the data from the view checklist page.
- Added script so get_checklist can be called from the command line.
