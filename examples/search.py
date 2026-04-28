"""Search Bandcamp for tracks, albums, artists, and labels."""
from py_bandcamp import BandCamp

print("=== Track search: 'astronaut problems' ===")
for i, track in enumerate(BandCamp.search_tracks("astronaut problems")):
    print(f"  [{i+1}] {track!r}  url={track.url}")
    if i >= 2:
        break

print("\n=== Album search: 'iii' ===")
for i, album in enumerate(BandCamp.search_albums("iii")):
    print(f"  [{i+1}] {album!r}  artist={album.data.get('artist')}  url={album.url}")
    if i >= 2:
        break

print("\n=== Artist search: 'Perturbator' ===")
for i, artist in enumerate(BandCamp.search_artists("Perturbator")):
    print(f"  [{i+1}] {artist!r}  genre={artist.genre}  url={artist.url}")
    if i >= 2:
        break

print("\n=== Label search: 'season of mist' ===")
for i, label in enumerate(BandCamp.search_labels("season of mist")):
    print(f"  [{i+1}] {label!r}  location={label.location}  url={label.url}")
    if i >= 2:
        break

print("\nDone.")
