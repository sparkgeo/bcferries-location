from bcferries_location import __version__, ferries

test_data_dir = "samples/"


def test_version():
    assert __version__ == "0.1.0"


def test_fetch_route():
    ROUTE_CONFIGS = {
        1: {
            "path": "/Users/dustin/projects/bcferries-location/tests/samples/route1.html",
            "x": -13833727.210434785,
            "y": 6388172.448499758,
            "w": 304.5759857310256,
            "h": 306.3788682417505,
        }
    }

    result = ferries.fetch_route(1, ROUTE_CONFIGS)
    assert len(result) == 3
