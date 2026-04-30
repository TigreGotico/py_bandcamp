"""Search Bandcamp for tracks, albums, artists, labels, and by tag."""
from py_bandcamp import BandCamp

print("=== search_tracks: 'astronaut problems' ===")
for i, t in enumerate(BandCamp.search_tracks("astronaut problems")):
    print(f"  [{i+1}] {t!r}  artist={t.data.get('artist')}  url={t.url}")
    if i >= 2: break

print("\n=== search_albums: 'iii' ===")
for i, a in enumerate(BandCamp.search_albums("iii")):
    print(f"  [{i+1}] {a!r}  artist={a.data.get('artist')}  url={a.url}")
    if i >= 2: break

print("\n=== search_artists: 'Perturbator' ===")
for i, ar in enumerate(BandCamp.search_artists("Perturbator")):
    print(f"  [{i+1}] {ar!r}  genre={ar.genre}  location={ar.location}  url={ar.url}")
    if i >= 2: break

print("\n=== search_labels: 'season of mist' ===")
for i, lb in enumerate(BandCamp.search_labels("season of mist")):
    print(f"  [{i+1}] {lb!r}  location={lb.location}  url={lb.url}")
    if i >= 2: break

print("\n=== search (mixed): 'electric wizard' ===")
for i, r in enumerate(BandCamp.search("electric wizard", albums=True, tracks=True,
                                       artists=True, labels=False)):
    print(f"  [{i+1}] {type(r).__name__}  {r!r}  url={r.url}")
    if i >= 4: break

print("\n=== search_tag: 'doom-metal' ===")
for i, r in enumerate(BandCamp.search_tag("doom-metal", albums=True, tracks=False,
                                           artists=False, max_pages=1)):
    print(f"  [{i+1}] {type(r).__name__}  {r!r}")
    if i >= 2: break

print("\n=== tags() ===")
tags = BandCamp.tags()
print(f"  {len(tags)} tags total. Sample: {tags[:6]}")
assert "black-metal" in tags, "expected black-metal in tag list"
assert "doom" in tags, "expected doom in tag list"
print("  OK")

print("\nDone.")
