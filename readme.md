# py_bandcamp

Python scraper for Bandcamp — search, metadata, stream URL extraction, and discovery.

## Install

```bash
pip install py_bandcamp
```

## Quick start

```python
from py_bandcamp import BandCamp, BandcampTrack, BandcampAlbum, BandcampArtist

# Get a streamable MP3 URL
url = BandCamp.get_stream_url("https://deadunicorn.bandcamp.com/track/astronaut-problems")
print(url)  # https://t4.bcbits.com/stream/...

# Search
for track in BandCamp.search_tracks("astronaut problems"):
    print(track, track.url)

for album in BandCamp.search_albums("black metal"):
    print(album.title, album.data.get("artist"))

for artist in BandCamp.search_artists("Perturbator"):
    print(artist.name, artist.genre, artist.location)

# Browse by genre tag
for result in BandCamp.search_tag("doom-metal", albums=True, tracks=False, max_pages=2):
    print(result.title, result.url)

# Load a track directly
track = BandcampTrack.from_url("https://deadunicorn.bandcamp.com/track/astronaut-problems")
print(track.title, track.stream, track.duration)

# Load an album
album = BandcampAlbum.from_url("https://naxatras.bandcamp.com/album/iii")
for t in album.tracks:
    print(t.track_num, t.title, t.duration)

# Discover related albums and artists from a seed
recs = BandCamp.get_recommendations("https://naxatras.bandcamp.com/album/iii")
for r in recs:
    print(r.title, r.data.get("artist"), r.url)

related = BandCamp.get_related_artists("https://naxatras.bandcamp.com/album/iii")
for a in related:
    print(a.name, a.url)

# Load an artist
artist = BandcampArtist.from_url("https://dopethrone.bandcamp.com")
print(artist.name, artist.location)
for album in artist.albums[:3]:
    print(album.title, album.url)
```

## Session injection

By default py_bandcamp uses a plain `requests.Session`. You can replace it with any
session-compatible object (e.g. one with custom headers, retries, or a cache):

```python
import requests
from py_bandcamp import set_session

session = requests.Session()
session.headers["User-Agent"] = "my-app/1.0"
set_session(session)
```

## API

See [docs/bandcamp_api.md](docs/bandcamp_api.md) for the full reference.

## Examples

| Script | What it shows |
|---|---|
| `examples/track_stream.py` | Fetch track metadata, stream URL, lyrics |
| `examples/album_browse.py` | Browse an album: tracks (with duration), releases, comments, artist |
| `examples/artist_browse.py` | Browse an artist: albums, featured album and track |
| `examples/search.py` | Search for tracks, albums, artists, labels, tags |
| `examples/recommendations.py` | Related albums and artists from a seed; genre browsing |

## Notes

- Stream URLs come from the `data-tralbum` attribute on Bandcamp pages (not the ld+json blob).
  They are time-limited tokens — do not cache them for long periods.
- Bandcamp does not provide a public API; this library scrapes HTML and may break if Bandcamp changes its markup.
