BC Ferries Location API
----------------------

### Routes Available

* **0:** Swartz Bay - Tsawwassen
* **1:** Tsawwassen - Duke Point
* **2:** Tsawwassen - Gulf Islands
* **3:** Horseshoe Bay - Departure Bay
* **4:** Horseshoe Bay - Langdale
* **5:** Horseshoe Bay - Bowen Island
* **6:** Swartz Bay - Fulford Harbourv
* **7:** Swartz Bay - Gulf Islands
* **13:** Mid and North Coast Routes
* **16:** Mill Bay - Brentwood Bay
* **17:** Crofton - Vesuvius
* **18:** Chemainus - Thetis - Penelakut
* **19:** Nanaimo Harbour - Gabriola



### Usage

```python

from bcferries_location import ferries

vessels = ferries.fetch_route(1)  # Tsawwassen - Duke Point

print(json.dumps([v.__json__() for v in vessels]), indent=4)
```

**Output:**

```json
[
    {
        "name": "Queen of Alberni",
        "coords": {
            "x": -123.18153694736814,
            "y": 48.990681414521276
        },
        "route": null,
        "destination": "Tsawwassen",
        "heading": "E",
        "speed": "20.1 knots"
    },
    {
        "name": "Queen of New Westminster",
        "coords": {
            "x": -123.85734194736828,
            "y": 49.188942753266176
        },
        "route": null,
        "destination": "Duke Point",
        "heading": "NE",
        "speed": "19.3 knots"
    },
    {
        "name": "Coastal Inspiration",
        "coords": {
            "x": -123.8272453684209,
            "y": 49.20333088235817
        },
        "route": null,
        "destination": "Duke Point",
        "heading": "W",
        "speed": "19.2 knots"
    }
]
```