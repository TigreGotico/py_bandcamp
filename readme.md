# py_bandcamp

Python scraper for Bandcamp — search, metadata, and stream URL extraction.

## Install

```bash
pip install py_bandcamp
```

## Quick start

```python
from py_bandcamp import BandCamp, BandcampTrack, BandcampAlbum

# Get a streamable MP3 URL
url = BandCamp.get_stream_url("https://deadunicorn.bandcamp.com/track/astronaut-problems")
print(url)  # https://t4.bcbits.com/stream/...

# Search
for track in BandCamp.search_tracks("astronaut problems"):
    print(track, track.url)

for album in BandCamp.search_albums("black metal"):
    print(album.title, album.data.get("artist"))

# Load a track directly
track = BandcampTrack.from_url("https://deadunicorn.bandcamp.com/track/astronaut-problems")
print(track.title, track.stream, track.image)

# Load an album
album = BandcampAlbum.from_url("https://naxatras.bandcamp.com/album/iii")
for t in album.tracks:
    print(t.track_num, t.title)
```

## API

See [docs/bandcamp_api.md](docs/bandcamp_api.md) for the full reference.

## Examples

| Script | What it shows |
|---|---|
| `examples/track_stream.py` | Fetch track metadata and stream URL |
| `examples/album_browse.py` | Browse an album: tracks, releases, artist |
| `examples/search.py` | Search for tracks, albums, artists, labels |

## Notes

- Stream URLs come from the `data-tralbum` attribute on Bandcamp pages (not the ld+json blob).
  They are time-limited tokens — cache them for short periods only.
- HTTP responses are cached in memory for 5 minutes via `requests-cache`.
- Bandcamp does not provide a public API; this library scrapes HTML and may break if Bandcamp changes its markup.
