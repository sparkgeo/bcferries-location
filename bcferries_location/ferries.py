import re
from collections import Iterable, namedtuple

import requests

from pyproj import Proj, transform

from .route_configs import (
    ROUTE_0,
    ROUTE_1,
    ROUTE_2,
    ROUTE_3,
    ROUTE_4,
    ROUTE_5,
    ROUTE_6,
    ROUTE_7,
    ROUTE_13,
    ROUTE_19,
)

ROUTE_CONFIGS = {
    0: ROUTE_0,
    1: ROUTE_1,
    2: ROUTE_2,
    3: ROUTE_3,
    4: ROUTE_4,
    5: ROUTE_5,
    6: ROUTE_6,
    7: ROUTE_7,
    13: ROUTE_13,
    19: ROUTE_19,
}


METADATA_MAP = {"Destination": "destination", "Speed": "speed", "Heading": "heading"}


__all__ = (
    "ROUTE_CONFIGS",
    "Coordinate",
    "RouteNotAvailableError",
    "RouteSourceError",
    "TemporarilyOfflineError",
    "RoutePageFormatError",
    "Vessel",
    "fetch_route",
)


# Patterns
pixel_coord_pattern = re.compile(r"x >= \d+ && y >= \d+ && x <= \d+ && y <= \d+")
vessel_details_pattern = re.compile(
    r"x >= \d+ && y >= \d+ && x <= \d+ && y <= \d+.*?ferryInfo\.innerHTML", re.S | re.I
)
tr_pattern = re.compile(r"<tr.*?>*?</tr>", re.I | re.S)
td_pattern = re.compile(r"<td>.*?</td>", re.I | re.S)
b_pattern = re.compile(r"<b.*?>*?</b>", re.I | re.S)


# Exceptions


class RouteNotAvailableError(Exception):
    pass


class RouteSourceError(Exception):
    pass


class TemporarilyOfflineError(Exception):
    pass


class RoutePageFormatError(Exception):
    pass


# -//- Exceptions -//-


class Coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __json__(self):
        return dict(x=self.x, y=self.y)

    def __iter__(self):
        return iter([self.x, self.y])


class Vessel(object):
    def __init__(self, name, coords, route, destination=None, heading=None, speed=None):
        self.name = name
        self.coords = coords
        self.route = route
        self.destination = destination
        self.heading = heading
        self.speed = speed

    def __json__(self):
        return dict(
            name=self.name,
            coords=self.coords.__json__(),
            route=self.route,
            destination=self.destination,
            heading=self.heading,
            speed=self.speed,
        )

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, val):
        if isinstance(val, Coordinate):
            self._coords = val
        elif isinstance(val, collections.Iterable):
            self._coords = Coordinate(*val)


def _fetch_route_page(url):
    response = requests.get(url)
    status_code = response.status_code
    content = response.text
    if status_code == 404:
        raise RouteNotAvailableError("Route currently not available")
    elif status_code != 200:
        raise RouteSourceError(content)

    if _is_offline(content):
        raise TemporarilyOfflineError()

    return content


def _fetch_local_file(path):
    with open(path) as f:
        return f.read()


def _find_vessel_details(s, route_config):

    x, y = _parse_pixel_coords(s)  # Web Mercator
    coords_3857 = _pixel_to_coords(
        x, y, route_config["x"], route_config["y"], route_config["w"], route_config["h"]
    )
    coords_4326 = _to_wgs84(coords_3857)

    # Metdata
    tds = re.findall(td_pattern, s)
    metadata = dict([_parse_td(td) for td in tds])

    return Vessel(
        name=metadata.get(""),
        destination=metadata.get("destination"),
        heading=metadata.get("heading"),
        speed=metadata.get("speed"),
        coords=coords_4326,
        route=route_config.get("name"),
    )


def _find_vessels(s, route_config):
    result = re.findall(vessel_details_pattern, s)
    output = []
    for r in result:
        output.append(_find_vessel_details(r, route_config))

    return output


def _is_offline(s):

    # Method 1
    offline_pattern = re.compile(r"<td>Temporarily Off Line</td>", re.I)
    if re.match(offline_pattern, s) is not None:
        return True

    # Method 2
    vessel_status_index = s.find('id="vessel_status"')
    if vessel_status_index == -1:
        raise RoutePageFormatError()
    sample = s[vessel_status_index:]
    return len(re.findall(tr_pattern, sample)) == 3


def _parse_pixel_coords(s):
    result = re.match(pixel_coord_pattern, s)
    parts = [m.strip() for m in result.group(0).split("&&")]

    # example: x >= 391 && y >= 368 && x <= 405 && y <= 382

    # x >= 391
    x1 = float(parts[0][4:])
    # x <= 405
    x2 = float(parts[2][4:])
    # y >= 368
    y1 = float(parts[1][4:])
    # y <= 382
    y2 = float(parts[3][4:])

    x = int((x2 - x1) / 2 + x1)
    y = int((y2 - y1) / 2 + y1)

    return x, y


def _parse_td(s):
    key = re.sub(b_pattern, "", s)
    if key is not None:
        key = key[4:-5].replace(":", "").strip()
    val = re.search(b_pattern, s)
    if val is not None:
        val = val.group(0)[3:-4].strip()

    return (METADATA_MAP.get(key) or "", val)


def _pixel_to_coords(pixelX, pixelY, coord0X, coord0Y, pixelWidth, pixelHeight):
    coordX = coord0X + (pixelX * pixelWidth)
    coordY = coord0Y - (pixelY * pixelHeight)
    return Coordinate(coordX, coordY)


def _to_wgs84(coords):
    inProj = Proj(init="epsg:3857")
    outProj = Proj(init="epsg:4326")
    return Coordinate(*transform(inProj, outProj, *coords))


def fetch_route(route, route_configs=None):
    route_config = (route_configs or ROUTE_CONFIGS).get(route)
    if route_config is None:
        raise ValueError("Route not available")

    if "url" in route_config:
        page_content = _fetch_route_page(route_config["url"])
    elif "path" in route_config:
        page_content = _fetch_local_file(route_config["path"])
    else:
        raise ValueError("Missing 'url' or 'path' in route config")

    return _find_vessels(page_content, route_config)
