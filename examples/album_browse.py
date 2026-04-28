"""Browse an album: metadata, track list, featured track, artist info."""
from py_bandcamp import BandcampAlbum

ALBUM_URL = "https://naxatras.bandcamp.com/album/iii"

print(f"=== Album: {ALBUM_URL} ===")
album = BandcampAlbum.from_url(ALBUM_URL)
print(f"  title       : {album.title}")
print(f"  image       : {album.image}")
print(f"  keywords    : {album.keywords}")
print(f"  n_tracks    : {album.data.get('n_tracks')}")

print("\n=== Artist ===")
artist = album.artist
if artist:
    print(f"  name: {artist.name}  url: {artist.url}")

print("\n=== Tracks ===")
tracks = album.tracks
for t in tracks[:5]:
    print(f"  [{t.track_num}] {t.title}  {t.duration}s  stream={t.stream}")
if len(tracks) > 5:
    print(f"  ... and {len(tracks) - 5} more")

print("\n=== Featured track ===")
ft = album.featured_track
if ft:
    print(f"  {ft.title}  stream={ft.stream}")

print("\n=== Releases ===")
for r in album.releases:
    print(f"  {r.get('format')} — {r.get('title')}")

print("\nDone.")
