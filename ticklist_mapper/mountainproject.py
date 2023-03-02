import re
import urllib.parse
from enum import Enum
from typing import NamedTuple, Optional, Tuple

import requests
import requests_cache

requests_cache.install_cache("requests_cache")


class SearchType(Enum):
    route = "Route"
    area = "Area"


class Route(NamedTuple):
    name: str
    grade: str
    area: str
    coordinates: Tuple[float, float]
    url: str
    area_url: Optional[str]

    def dict(self) -> dict:
        d = self._asdict()
        # TODO: Figure out a more dynamic way to add propertyies to the dict
        d["youtube_beta_url"] = self.youtube_beta_url
        return d

    @property
    def youtube_beta_url(self) -> str:
        query = urllib.parse.quote_plus(f"{self.name} {self.grade}")
        return f"https://www.youtube.com/results?search_query={query}"


def search(query: str, search_type: SearchType = SearchType.route) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://www.mountainproject.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "q": query,
        "from": "0",
    }

    data = '{"types":["%s"],"filter":[],"sort":[]}' % search_type.value

    response = requests.post(
        "https://www.mountainproject.com/api/v2/search",
        params=params,
        headers=headers,
        data=data,
    )
    response.raise_for_status()
    data = response.json().get("hits")
    if not isinstance(data, list) and len(data) < 1:
        raise ValueError(f"No route found for query: '{query}'")

    if len(data) == 1:
        return data[0]["_source"]

    # If there are multiple results, try to find the one that's a boulder
    for d in data:
        if (
            "boulder" in d["_source"]["description"].lower()
            or "boulder" in d["_source"]["breadcrumbs"].lower()
        ):
            return d["_source"]

    raise ValueError(f"No boulder route found for query: '{query}'")


def get_area_from_breadcrumbs(breadcrumbs: str) -> str:
    return breadcrumbs.split(">")[-1].strip()


def get_coordinates(url: str) -> list:
    r = requests.get(url)
    r.raise_for_status()
    # Looks for a url like 'http://maps.google.com/maps?q=37.3388,-118.5776&t=h&hl=en' and
    # extract the coordinates from the page
    regex = (
        r"maps\.google\.com\/maps\?q=([+-]?[0-9]*[.]?[0-9]+),([+-]?[0-9]*[.]?[0-9]+)"
    )
    matches = re.search(regex, r.content.decode("utf-8"))
    return [float(matches.group(1)), float(matches.group(2))]


def get_route_info(route_query: str) -> Optional[Route]:
    try:
        route_response = search(route_query, SearchType.route)
    except ValueError as e:
        print(e)
        # TODO: Return an empty Route object instead so the user can be informed that a
        # route wasn't found
        return None

    area = get_area_from_breadcrumbs(route_response["breadcrumbs"])
    area_url = None

    try:
        # Not sure why the coordinates in the area response are wrong... need to get it from
        # the url page instead
        area_response = search(area, SearchType.area)
        coordinates = get_coordinates(area_response["url"])
        area_url = area_response.get("url")
    except Exception as e:
        print(f"Couldn't get coordinates: {e}")
        # Fallback to using the ones in the route
        # Lat/long are reversed for some reason
        coordinates = route_response["location"][::-1]

    return Route(
        name=route_response["title"],
        grade=route_response["difficulty"]["string"],
        area=area,
        coordinates=coordinates,
        url=route_response["url"],
        area_url=area_url,
    )


# route = get_route_info("north face direct bishop")
# print(route)
