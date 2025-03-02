import datetime as dt
import re

import requests
from bs4 import BeautifulSoup

_get_area_units = {
    "hectare(s)": "ha",
    "hectares": "ha",
    "ha": "ha",
    "acre(s)": "acre",
    "acres": "acre",
}

ACRES_PER_HECTARE = 0.404686

METRES_PER_MILE = 1609

METRES_PER_KILOMETRE = 1000


def get_checklist(identifier):
    """
    Get the data for a checklist from its eBird web page.

    Args:
        identifier (str): the unique identifier for the checklist, e.g. S62633426

    Returns:
        (dict): all the fields extracted from the web page.

    """
    url = _get_url(identifier)
    content = _get_page(url)
    root = _get_tree(content)
    return _get_checklist(root)


def _get_url(identifier):
    return "https://ebird.org/checklist/%s" % identifier


def _get_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def _get_tree(content):
    return BeautifulSoup(content, "lxml")


def _get_checklist(root):
    return {
        "identifier": _get_identifier(root),
        "date": _get_date(root),
        "time": _get_time(root),
        "observer": _get_observer(root),
        "participants": _get_participants(root),
        "protocol": _get_protocol(root),
        "observer_count": _get_observer_count(root),
        "location": _get_location(root),
        "entries": _get_entries(root),
        "comment": _get_comment(root),
        "complete": _get_complete(root),
    }


def _get_location(root):
    return {
        "name": _get_location_name(root),
        "identifier": _get_location_identifier(root),
        "subnational2": _get_subnational2(root),
        "subnational2_code": _get_subnational2_code(root),
        "subnational1": _get_subnational1(root),
        "subnational1_code": _get_subnational1_code(root),
        "country": _get_country(root),
        "country_code": _get_country_code(root),
        "lat": _get_latitude(root),
        "lon": _get_longitude(root),
    }


# IMPORTANT: All the functions that extract values, start at the root of the
# tree, and each value is extracted independently. This reduces performance
# but makes updating the code when the page layout changes much much easier.
# The helper functions simplify navigating to a point in the tree where the
# data is located.


def _find_page_sections(root):
    return root.find_all("div", {"class": "Page-section"})


def _get_identifier(root):
    node = root.find("input", {"type": "hidden", "name": "subID"})
    return node["value"]


def _get_date(root):
    node = _find_page_sections(root)[1]
    value = node.find("time")["datetime"]
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M")


def _get_coordinates(root):
    link = root.find(href=re.compile("www.google.com/maps"))
    query = link["href"].split("?")[1]
    param = query.split("&")[1]
    return param.split("=")[1]


def _get_latitude(root):
    return _get_coordinates(root).split(",")[0]


def _get_longitude(root):
    return _get_coordinates(root).split(",")[1]


def _get_location_name(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Location")
    if node.find_next_sibling("a"):
        node = node.find_next_sibling("a").find("span")
    else:
        node = node.find_next_sibling("span")
    return node.text.strip()


def _get_location_identifier(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Location")
    if node.find_next_sibling("a"):
        url = node.find_next_sibling("a")["href"]
        return url.split("/")[-1]
    else:
        return ""


def _get_subnational2(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Region")
    node = node.find_next_sibling("ul").find_all("li")[0]
    return node.find("a").text.strip()


def _get_subnational2_code(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Region")
    node = node.find_next_sibling("ul").find_all("li")[0]
    url = node.find("a")["href"]
    return url.split("/")[-1]


def _get_subnational1(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Region")
    # The country might only have one level of region
    node = node.find_next_sibling("ul").find_all("li")[-1]
    return node.find("span").text.strip()


def _get_subnational1_code(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Region")
    # If the country only has one level of regionm then
    # return an empty string for subnational2
    regions = node.find_next_sibling("ul").find_all("li")
    if len(regions) == 2:
        return regions[0].find("span").text.strip()
    else:
        return ""


def _get_country(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Region")
    node = node.find_next_sibling("ul").find_all("li")[2]
    return node.find("span").text.strip()


def _get_country_code(root):
    node = _find_page_sections(root)[1]
    node = node.find("span", string="Region")
    node = node.find_next_sibling("ul").find_all("li")[2]
    url = node.find("a")["href"]
    return url.split("/")[-1]


def _point_protocol(name, root):
    return {
        "name": name,
        "duration": _get_duration(root),
    }


def _stationary_protocol(root):
    return _point_protocol("Stationary", root)


def _night_protocol(root):
    return _point_protocol("Nocturnal Flight Call Count", root)


def _cwc_point_protocol(root):
    return _point_protocol("CWC Point Count", root)


def _proalas_transect_protocol(root):
    return _distance_protocol("PROALAS Mini-transect", root)


def _proalas_2_protocol(root):
    return _point_protocol("PROALAS Point Count (2 Bands)", root)


def _proalas_3_protocol(root):
    return _point_protocol("PROALAS Point Count (3 Bands)", root)


def _waterbird_protocol(root):
    return _point_protocol("TNC California Waterbird Count", root)


def _distance_protocol(name, root):
    return {
        "name": name,
        "duration": _get_duration(root),
        "distance": _get_distance(root),
    }


def _traveling_protocol(root):
    return _distance_protocol("Traveling", root)


def _pelagic_protocol(root):
    return _distance_protocol("eBird Pelagic Protocol", root)


def _random_protocol(root):
    return _distance_protocol("Random", root)


def _blackbird_protocol(root):
    return _distance_protocol("Rusty BlackbirdSpring Migration Blitz", root)


def _pelican_protocol(root):
    return _distance_protocol("California Brown Pelican Survey", root)


def _incidental_observations(node):
    return {"name": "Incidental"}


def _historical_observations(node):
    results = {
        "name": "Historical",
    }

    if duration := _get_duration(node):
        results["duration"] = duration

    if distance := _get_distance(node):
        results["distance"] = distance

    if area := _get_area(node):
        results["area"] = area

    return results


def __area_protocol(name, root):
    results = {
        "name": name,
        "area": _get_area(root),
        "duration": _get_duration(root),
    }
    return results


def _area_protocol(root):
    return __area_protocol("Area", root)


def _banding_protocol(root):
    return __area_protocol("Banding", root)


def _cwc_area_protocol(root):
    return __area_protocol("CWC Point Count", root)


_protocols = {
    "Stationary": _stationary_protocol,
    "Traveling": _traveling_protocol,
    "Incidental": _incidental_observations,
    "Historical": _historical_observations,
    "Area": _area_protocol,
    "Banding": _banding_protocol,
    "eBird Pelagic Protocol": _pelagic_protocol,
    "Nocturnal Flight Call Count": _night_protocol,
    "Random": _random_protocol,
    "CWC Point Count": _cwc_point_protocol,
    "CWC Area Count": _cwc_area_protocol,
    "PROALAS Point Count (2 Bands)": _proalas_2_protocol,
    "PROALAS Mini-transect": _proalas_transect_protocol,
    "PROALAS Point Count (3 Bands)": _proalas_3_protocol,
    "TNC California Waterbird Count": _waterbird_protocol,
    "Rusty BlackbirdSpring Migration Blitz": _blackbird_protocol,
    "California Brown Pelican Survey": _pelican_protocol,
}


def _get_protocol(root):
    name = _get_protocol_name(root)
    return _protocols[name](root)


def _get_protocol_name(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r"^Protocol:.*")
    node = node.find("div", title=regex)
    node = node.find_all("span")[1]
    return node.text.strip()


def _get_time(root):
    return _get_date(root).time()


def _get_duration(root):
    duration = None
    section = _find_page_sections(root)[2]
    regex = re.compile(r"^Duration:.*")
    if node := section.find("span", title=regex):
        if duration_node := node.find("span", class_="Badge-label"):
            value = duration_node.text.strip()
            if "," in value:
                hours_str, mins_str = value.split(",", 1)
                hours = hours_str.strip().split(" ")[0].strip()
                mins = mins_str.strip().split(" ")[0].strip()
            elif "hr" in value:
                hours = value.split(" ")[0].strip()
                mins = "0"
            else:
                hours = "0"
                mins = value.split(" ")[0].strip()
            duration = int(hours) * 60 + int(mins)
    return duration


def _get_observer_count(root):
    count = None
    section = _find_page_sections(root)[2]
    regex = re.compile(r"^Observers:.*")
    if node := section.find("span", title=regex):
        if count_node := node.find("span", class_="Badge-label"):
            count = int(count_node.text.strip())
    return count


def _get_distance(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r"^Distance:.*")
    node = node.find("span", title=regex)
    node = node.find_all("span")[1]
    value = node.text.strip()
    distance = float(value.split(" ")[0])
    units = value.split(" ")[1]
    if units == "mi":
        distance *= METRES_PER_MILE
    elif units == "km":
        distance *= METRES_PER_KILOMETRE
    return int(distance)


def _get_area(node):
    area = None

    regex = re.compile(r"\s*[Aa]rea[:]?\s*")
    tag = node.find("dt", text=regex)

    if tag:
        field = tag.parent.dd
        values = field.text.lower().split()
        area = float(values[0])
        units = _get_area_units[values[1]]
        if units == "acre":
            area *= ACRES_PER_HECTARE
            area = int(area * 1000) / 1000

    return area


def _get_observer(node):
    observer = node.find("span", attrs={"data-participant-userid": True})
    identifier = observer["data-participant-userid"].strip()
    name = observer.find(
        "span", attrs={"data-participant-userdisplayname": True}
    ).text.strip()
    return {
        "identifier": identifier,
        "name": name,
    }


def _get_participants(node):
    results = []
    participants = node.findAll("li", attrs={"data-participant-userid": True})
    for sub_node in participants:
        results.append(_get_participant(sub_node))
    return results


def _get_participant(node):
    identifier = node["data-participant-userid"].strip()
    name = node.find(
        "span", attrs={"data-participant-userdisplayname": True}
    ).text.strip()
    participant = {
        "identifier": identifier,
        "name": name,
    }
    if link := node.find("a", attrs={"data-ga-category": "checklist"}):
        participant["checklist"] = "https://ebird.org" + link["href"].strip()
    return participant


def _get_comment(root):
    items = []
    if node := root.find(id="checklist-comments"):
        for p in node.find_next_siblings("p"):
            items.append(p.text.strip())
    return "\n".join(items)


def _get_entries(root):
    node = _find_page_sections(root)[3]
    node = node.find("div", {"id": "list"})
    tags = node.find_all("li", {"data-observation": ""})
    entries = []
    for tag in tags:
        entries.append(_get_entry(tag))
    return entries


def _get_entry(node):
    result = {
        "species": _get_species(node),
        "count": _get_count(node),
    }

    if comments := _get_entry_comments(node):
        result["comments"] = comments

    if media := _get_media(node):
        result["media"] = media

    if breeding_code := _get_breeding_code(node):
        result["breeding-code"] = breeding_code

    if age_sex := _get_age_sex(node):
        result["age-sex"] = age_sex

    return result


def _get_species(node):
    node = node.find("div", {"class": "Observation-species"})
    tag = node.find("span", {"class": "Heading-main"})
    value = " ".join(tag.text.split())
    return value


def _get_count(node):
    count = None
    node = node.find("div", class_="Observation-numberObserved")
    tag = node.find_all("span")[-1]
    value = tag.text.strip().lower()
    if value != "x":
        count = int(value)
    return count


def _get_entry_comments(node):
    result = ""
    if comments := node.find("div", {"class": "Observation-comments"}):
        paragraphs = comments.find_all("p")
        for paragraph in paragraphs:
            for br in paragraph.find_all("br"):
                br.replace_with("\n")
            result += " ".join(paragraph.text.split())
    return result


def _get_media(node):
    result = []
    if section := node.find("section", {"class": "Observation-media"}):
        media = section.find_all("div", {"data-media-id": True})
        for item in media:
            result.append({"identifier": item["data-media-id"]})
    return result


def _get_breeding_code(node):
    result = {}
    regex = re.compile(r"^Breeding.*")
    if heading := node.find("h4", string=regex):
        span = heading.find_next_sibling()
        entry = span.find("span").text.strip()
        # Depending on the portal used, the breeding code might be prefixed
        # with an integer or something resembling the code used by eBird.
        if re.match(r"^\d{1,2}\. .*", entry):
            code, name = entry.split(".", 1)
        elif re.match(r"[A-Z]{2} .*]", entry):
            code, name = entry.split(" ", 1)
        else:
            code, name = None, entry
        return {
            "code": code.strip() if code else None,
            "name": name.replace("\xa0", " ").strip(),
        }
    return result


def _get_age_sex(node):
    result = {}
    regex = re.compile(r"^Age.*")
    if heading := node.find("h4", string=regex):
        table = heading.find_next_sibling().find("tbody")
        for idx, row in enumerate(table.find_all("tr")):
            if idx == 0:
                values = []
                for child in row.findChildren(recursive=False):
                    values.append(child.text.strip())
                key = values.pop(0)
            else:
                key = ""
                values = []
                for child in row.findChildren(recursive=False):
                    value = child.text.strip()
                    if child.name == "th":
                        key = value
                    if child.name == "td":
                        value = int(value) if value else 0
                        values.append(value)
            result[key] = values

    return result


def _get_complete(root):
    node = _find_page_sections(root)[2]
    regex = re.compile(r"^Protocol:.*")
    node = node.find("div", title=regex).parent
    node = node.find_next_sibling("div")
    node = node.find("span", {"class": "Badge-label"})
    value = node.text.strip()
    return value == "Complete"
