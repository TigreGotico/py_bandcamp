"""Fetch track metadata and get a streamable MP3 URL."""
from py_bandcamp import BandCamp, BandcampTrack

TRACK_URL = "https://deadunicorn.bandcamp.com/track/astronaut-problems"

print(f"=== Track: {TRACK_URL} ===")
track = BandcampTrack.from_url(TRACK_URL)
print(f"  title    : {track.title}")
print(f"  duration : {track.duration}s")
print(f"  image    : {track.image}")
print(f"  stream   : {track.stream}")

print("\n=== get_stream_url (BandCamp helper) ===")
stream = BandCamp.get_stream_url(TRACK_URL)
print(f"  stream url: {stream}")
assert stream, "expected a non-empty stream URL"
print("  OK — got a stream URL")

print("\n=== Artist from track page ===")
artist = track.artist
if artist:
    print(f"  name: {artist.name}  url: {artist.url}")
else:
    print("  (no artist data on this page)")

print("\n=== Album from track page ===")
album = track.album
if album:
    print(f"  title: {album.title}  url: {album.url}")
else:
    print("  (no album data on this page)")
