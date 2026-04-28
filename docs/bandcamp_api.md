# py_bandcamp — Developer Reference

py_bandcamp scrapes Bandcamp pages to provide search, streaming, and metadata access without an official API.

---

## BandCamp (main interface)

```python
from py_bandcamp import BandCamp
```

### Search

```python
# Search across all types (returns generator, auto-paginates up to max_pages)
for result in BandCamp.search("black metal", albums=True, tracks=True,
                               artists=True, labels=False, max_pages=10):
    print(type(result).__name__, result)

# Single-type convenience wrappers
for t in BandCamp.search_tracks("astronaut problems"):
    print(t.title, t.url)

for a in BandCamp.search_albums("iii"):
    print(a.title, a.data.get("artist"))

for ar in BandCamp.search_artists("Perturbator"):
    print(ar.name, ar.genre)

for lb in BandCamp.search_labels("Nuclear Blast"):
    print(lb.name, lb.location)
```

`search()` paginates automatically and yields `BandcampTrack`, `BandcampAlbum`,
`BandcampArtist`, or `BandcampLabel` instances. Results are deduplicated by URL
across pages. `max_pages` (default 10) caps how many Bandcamp pages are fetched.

When only one result type is requested, the Bandcamp `item_type` filter is sent
so the results are more precise.

### Tag search

```python
# Search by genre tag (wraps search() with the tag as query)
for result in BandCamp.search_tag("black-metal", albums=True, tracks=True,
                                   artists=True, labels=False, max_pages=5):
    print(result)

# Get all known genre/subgenre tag names
tags = BandCamp.tags()                  # flat list of strings
tags = BandCamp.tags(tag_list=False)    # {"genres": [...], "subgenres": {...}}
print("black-metal" in BandCamp.tags()) # True
```

### Streaming

```python
# Get a direct MP3-128 stream URL for a track page
stream_url = BandCamp.get_stream_url("https://artist.bandcamp.com/track/song")
# Returns the CDN token URL, or the original URL if no stream is available.
# Note: stream URLs are time-limited tokens (~1 hour).

# Batch
urls = BandCamp.get_streams(["https://a.bandcamp.com/track/x",
                              "https://b.bandcamp.com/track/y"])
```

### Recommendations & related artists

```python
# Albums Bandcamp recommends for fans of a given album
recs = BandCamp.get_recommendations("https://artist.bandcamp.com/album/title")
# Returns list of BandcampAlbum (title, artist, url, image — no full scrape)

# Unique artists extracted from those recommendations
artists = BandCamp.get_related_artists("https://artist.bandcamp.com/album/title")
# Returns list of BandcampArtist (name, url — no full scrape)
```

These are also available as properties on `BandcampAlbum`:

```python
album = BandcampAlbum.from_url("https://artist.bandcamp.com/album/title")
album.recommendations   # list[BandcampAlbum]
album.related_artists   # list[BandcampArtist]
```

Bandcamp populates the "If you like…" section with ~6–8 albums from fans who also
own the current album. Availability depends on the album having enough purchase/fan data.

### Lyrics

```python
lyrics = BandCamp.get_track_lyrics("https://artist.bandcamp.com/track/song")
# Returns the lyrics text, or "lyrics unavailable" if not present.
```

---

## BandcampTrack

```python
from py_bandcamp import BandcampTrack

# Load from URL (fetches and parses the track page)
track = BandcampTrack.from_url("https://artist.bandcamp.com/track/song")

# Construct without fetching (e.g. from search results)
track = BandcampTrack({"url": "...", "title": "..."}, parse=False)

# Fetch page data later
track.parse_page()
```

| Property | Type | Description |
|---|---|---|
| `url` | `str` | Canonical Bandcamp URL |
| `title` | `str` | Track title |
| `image` | `str\|None` | Album art URL |
| `stream` | `str\|None` | Direct MP3-128 CDN URL |
| `duration` | `int` | Duration in seconds (0 if unavailable) |
| `track_num` | `int\|None` | Track number in album |
| `data` | `dict` | All parsed metadata |
| `album` | `BandcampAlbum\|None` | Album this track belongs to (fetches page) |
| `artist` | `BandcampArtist\|None` | Artist (fetches page) |

`stream` and `duration` are populated after `parse_page()` or `from_url()`.
Search results have `parse=False` by default — call `track.parse_page()` to load them.

---

## BandcampAlbum

```python
from py_bandcamp import BandcampAlbum

album = BandcampAlbum.from_url("https://artist.bandcamp.com/album/lp")

# Construct without scraping
album = BandcampAlbum({"url": "...", "title": "..."}, scrap=False)
```

| Property | Type | Description |
|---|---|---|
| `url` | `str` | Canonical Bandcamp URL |
| `title` | `str` | Album title |
| `image` | `str\|None` | Album art URL |
| `keywords` | `list[str]` | Genre/tag keywords |
| `tracks` | `list[BandcampTrack]` | Track listing (with `track_num` and `duration_iso`) |
| `featured_track` | `BandcampTrack\|None` | Featured track |
| `artist` | `BandcampArtist\|None` | Artist (fetches page) |
| `releases` | `list[dict]` | Release formats (`format`, `title`, `url`, `image`) |
| `comments` | `list[dict]` | Comments (`author`, `text`, `image`) |

Tracks in `album.tracks` have `duration` populated from the ISO 8601 duration
on the album page. They do **not** have stream URLs — call `track.parse_page()`
on individual tracks to load those.

---

## BandcampArtist

```python
from py_bandcamp import BandcampArtist

artist = BandcampArtist.from_url("https://artist.bandcamp.com")
```

| Property | Type | Description |
|---|---|---|
| `url` | `str` | Bandcamp artist URL |
| `name` | `str` | Artist name |
| `genre` | `str\|None` | Genre string |
| `location` | `str\|None` | Location string |
| `tags` | `list[str]` | Tag strings |
| `image` | `str\|None` | Artist image URL |
| `albums` | `list[BandcampAlbum]` | Albums (scrapes artist page) |
| `featured_album` | `BandcampAlbum` | First album from `/releases` |
| `featured_track` | `BandcampTrack\|None` | Featured track of the featured album |

---

## BandcampLabel

```python
from py_bandcamp import BandcampLabel

label = BandcampLabel.from_url("https://label.bandcamp.com")
```

| Property | Type | Description |
|---|---|---|
| `url` | `str` | Bandcamp label URL |
| `name` | `str` | Label name |
| `location` | `str\|None` | Location string |
| `tags` | `list[str]` | Tag strings |
| `image` | `str\|None` | Label image URL |

---

## Session / Custom HTTP client

By default a plain `requests.Session` is used. You can replace it with any
session-like object (e.g. one with custom headers, a retry adapter, or a mock):

```python
import requests
from py_bandcamp import set_session

# Custom session with a User-Agent header
s = requests.Session()
s.headers.update({"User-Agent": "my-app/1.0"})
set_session(s)

# Or inject a mock in tests
from unittest.mock import MagicMock
set_session(MagicMock())
```

The session object must implement `.get(url, **kwargs)` returning a response
with `.text`, `.content`, `.ok`, and `.status_code`.
