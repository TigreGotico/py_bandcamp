# py_bandcamp — Developer Reference

py_bandcamp scrapes Bandcamp pages to provide search, streaming, and metadata access without an official API.

---

## BandCamp (main interface)

```python
from py_bandcamp import BandCamp
```

### Search

```python
# Search across all types (returns generator)
for result in BandCamp.search("black metal", albums=True, tracks=True, artists=True, labels=False):
    print(type(result).__name__, result)

# Convenience wrappers
BandCamp.search_tracks("astronaut problems")
BandCamp.search_albums("iii")
BandCamp.search_artists("Perturbator")
BandCamp.search_labels("Nuclear Blast")
```

`search()` paginates automatically and yields `BandcampTrack`, `BandcampAlbum`, `BandcampArtist`, or `BandcampLabel` instances.

### Tags

```python
tags = BandCamp.tags()          # list of all genre/subgenre tag names
tags = BandCamp.tags(tag_list=False)  # dict with "genres" and "subgenres" keys

for result in BandCamp.search_tag("black-metal"):
    print(result)
```

### Streaming

```python
stream_url = BandCamp.get_stream_url("https://artist.bandcamp.com/track/song")
# Returns the direct MP3 URL, or the input URL if unavailable

urls = BandCamp.get_streams(["https://a.bandcamp.com/track/x",
                             "https://b.bandcamp.com/track/y"])
```

### Lyrics

```python
lyrics = BandCamp.get_track_lyrics("https://artist.bandcamp.com/track/song")
```

---

## BandcampTrack

```python
from py_bandcamp import BandcampTrack

track = BandcampTrack.from_url("https://artist.bandcamp.com/track/song")
```

| Property | Description |
|---|---|
| `url` | Canonical Bandcamp URL |
| `title` | Track title |
| `image` | Album art URL |
| `stream` | Direct MP3-128 URL (or `None`) |
| `duration` | Duration in seconds |
| `track_num` | Track number in album |
| `data` | Raw dict of all metadata |
| `album` | `BandcampAlbum` (fetches page) |
| `artist` | `BandcampArtist` (fetches page) |

---

## BandcampAlbum

```python
from py_bandcamp import BandcampAlbum

album = BandcampAlbum.from_url("https://artist.bandcamp.com/album/lp")
```

| Property | Description |
|---|---|
| `url` | Canonical Bandcamp URL |
| `title` | Album title |
| `image` | Album art URL |
| `keywords` | List of keyword strings |
| `tracks` | List of `BandcampTrack` |
| `featured_track` | `BandcampTrack` marked as featured |
| `artist` | `BandcampArtist` |
| `releases` | List of release format dicts |
| `comments` | List of comment dicts |

---

## BandcampArtist

```python
from py_bandcamp import BandcampArtist

artist = BandcampArtist.from_url("https://artist.bandcamp.com")
```

| Property | Description |
|---|---|
| `url` | Bandcamp artist URL |
| `name` | Artist name |
| `genre` | Genre string |
| `location` | Location string |
| `tags` | List of tag strings |
| `image` | Artist image URL |
| `albums` | List of `BandcampAlbum` (scrapes artist page) |
| `featured_album` | First `BandcampAlbum` from `/releases` |
| `featured_track` | Featured track of the featured album |

---

## BandcampLabel

```python
from py_bandcamp import BandcampLabel

label = BandcampLabel.from_url("https://label.bandcamp.com")
```

| Property | Description |
|---|---|
| `url` | Bandcamp label URL |
| `name` | Label name |
| `location` | Location string |
| `tags` | List of tag strings |
| `image` | Label image URL |

---

## Session / Caching

HTTP responses are cached in memory for 5 minutes via `requests_cache`. This prevents hammering Bandcamp during repeated lookups in the same process.

```python
from py_bandcamp.session import SESSION
SESSION.expire_after = 60  # change cache TTL to 60 seconds
```
