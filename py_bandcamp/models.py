from bs4 import BeautifulSoup
from py_bandcamp.session import SESSION as requests
from py_bandcamp.utils import extract_ldjson_blob, get_props, _extract_tralbum, _parse_iso_duration


class BandcampTrack:
    def __init__(self, data, parse=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if parse:
            self.parse_page()
        if not self.url:
            raise ValueError("bandcamp url is not set")

    def parse_page(self):
        self._page_data = self.get_track_data(self.url)
        return self._page_data

    @staticmethod
    def from_url(url):
        return BandcampTrack({"url": url})

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def album(self):
        return self.get_album(self.url)

    @property
    def artist(self):
        return self.get_artist(self.url)

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @property
    def title(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def image(self):
        return self.data.get("image")

    @property
    def track_num(self):
        return self.data.get("tracknum")

    @property
    def duration(self):
        secs = self.data.get("duration_secs")
        if secs:
            return secs
        iso = self.data.get("duration_iso") or ""
        return _parse_iso_duration(iso)

    @property
    def stream(self):
        return self.data.get("file_mp3-128")

    @staticmethod
    def get_album(url):
        data = extract_ldjson_blob(url, clean=True)
        if data.get('inAlbum'):
            return BandcampAlbum({
                "title": data['inAlbum'].get('name'),
                "url": data['inAlbum'].get('id', url).split("#")[0],
                'type': data['inAlbum'].get("type"),
            })

    @staticmethod
    def get_artist(url):
        data = extract_ldjson_blob(url, clean=True)
        d = data.get("byArtist")
        if d:
            return BandcampArtist({
                "title": d.get('name'),
                "url": d.get('id', url).split("#")[0],
                'genre': d.get('genre'),
                "artist_type": d.get('type')
            }, scrap=False)
        return None

    @staticmethod
    def get_track_data(url):
        import json

        resp = requests.get(url)
        if not resp.ok:
            raise ValueError(f"HTTP {resp.status_code} fetching {url}")
        text = resp.text

        if '<script type="application/ld+json">' not in text:
            raise ValueError(f"No ld+json found at {url} — may be a 404 or non-track page")

        ld_blob = text.split('<script type="application/ld+json">')[-1].split("</script>")[0]

        def _clean(d):
            if isinstance(d, dict):
                return {k.replace("@", ""): _clean(v) for k, v in d.items()}
            if isinstance(d, list):
                return [_clean(i) for i in d]
            return d

        try:
            data = _clean(json.loads(ld_blob))
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse ld+json from {url}: {e}") from e
        tralbum = _extract_tralbum(text)

        kwords = data.get('keywords', "")
        if isinstance(kwords, str):
            kwords = kwords.split(", ") if kwords else []
        track = {
            'dateModified': data.get('dateModified'),
            'datePublished': data.get('datePublished'),
            "url": data.get('id') or url,
            "title": data.get("name"),
            "type": data.get("type"),
            'image': data.get('image'),
            'keywords': kwords
        }
        for k, v in get_props(data).items():
            track[k] = v

        # Pull stream URL and duration from data-tralbum if not already present
        trackinfo = (tralbum.get("trackinfo") or [{}])[0]
        if not track.get("file_mp3-128"):
            mp3 = trackinfo.get("file", {}).get("mp3-128")
            if mp3:
                track["file_mp3-128"] = mp3
        if not track.get("duration_secs"):
            dur = trackinfo.get("duration")
            if dur:
                track["duration_secs"] = int(dur)

        return track

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.title

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.url)


class BandcampAlbum:
    def __init__(self, data, scrap=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if scrap:
            self.scrap()
        if not self.url:
            raise ValueError("bandcamp url is not set")

    def scrap(self):
        self._page_data = self.get_album_data(self.url)
        return self._page_data

    @staticmethod
    def from_url(url):
        return BandcampAlbum({"url": url})

    @property
    def image(self):
        return self.data.get("image")

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def title(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def releases(self):
        return self.get_releases(self.url)

    @property
    def artist(self):
        return self.get_artist(self.url)

    @property
    def keywords(self):
        return self.data.get("keywords") or []

    @property
    def tracks(self):
        return self.get_tracks(self.url)

    @property
    def featured_track(self):
        if not len(self.tracks):
            return None
        num = self.data.get('featured_track_num', 1) or 1
        return self.tracks[int(num) - 1]

    @property
    def recommendations(self):
        return self.get_recommendations(self.url)

    @property
    def related_artists(self):
        seen = set()
        artists = []
        for album in self.get_recommendations(self.url):
            artist_name = album.data.get("artist", "")
            if artist_name and artist_name not in seen:
                seen.add(artist_name)
                artists.append(BandcampArtist({"name": artist_name, "url": album.url.split("/album/")[0]}, scrap=False))
        return artists

    @property
    def comments(self):
        return self.get_comments(self.url)

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @staticmethod
    def get_releases(url):
        data = extract_ldjson_blob(url, clean=True)
        releases = []
        for d in data.get("albumRelease", []):
            release = {
                "description": d.get("description"),
                'image': d.get('image'),
                "title": d.get('name'),
                "url": d.get('id', url).split("#")[0],
                'format': d.get('musicReleaseFormat'),
            }
            releases.append(release)
        return releases

    @staticmethod
    def get_artist(url):
        data = extract_ldjson_blob(url, clean=True)
        d = data.get("byArtist")
        if d:
            return BandcampArtist({
                "description": d.get("description"),
                'image': d.get('image'),
                "title": d.get('name'),
                "url": d.get('id', url).split("#")[0],
                'genre': d.get('genre'),
                "artist_type": d.get('type')
            }, scrap=False)
        return None

    @staticmethod
    def get_tracks(url):
        data = extract_ldjson_blob(url, clean=True)
        if not data.get("track"):
            return []

        data = data['track']

        tracks = []

        for entry in data.get('itemListElement', []):
            d = entry.get('item', {})
            track = {
                "title": d.get('name'),
                "url": d.get('id') or url,
                'type': d.get('type'),
                "tracknum": entry.get('position'),
                "duration_iso": d.get('duration'),
            }
            for k, v in get_props(d).items():
                track[k] = v
            tracks.append(BandcampTrack(track, parse=False))
        return tracks

    @staticmethod
    def get_recommendations(url):
        """Albums recommended by Bandcamp for fans of this album ('If you like…')."""
        resp = requests.get(url)
        if not resp.ok:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        container = soup.find(id="recommendations_container")
        if not container:
            return []
        albums = []
        for li in container.find_all("li", class_="recommended-album"):
            album_url_tag = li.find("a", class_="album-link")
            if not album_url_tag:
                continue
            href = album_url_tag.get("href", "").split("?")[0]
            title_span = album_url_tag.find(class_="release-title")
            artist_span = album_url_tag.find(class_="by-artist")
            raw_artist = artist_span.text.strip() if artist_span else li.get("data-artist", "")
            artist = raw_artist.removeprefix("by ") if raw_artist else li.get("data-artist")
            albums.append(BandcampAlbum({
                "title": title_span.text.strip() if title_span else li.get("data-albumtitle"),
                "artist": artist,
                "url": href,
                "image": (li.find("img") or {}).get("src"),
            }, scrap=False))
        return albums

    @staticmethod
    def get_comments(url):
        data = extract_ldjson_blob(url, clean=True)
        comments = []
        for d in data.get("comment", []):
            text = d.get("text", "")
            if isinstance(text, list):
                text = " ".join(text)
            comment = {
                "text": text,
                'image': d["author"].get("image"),
                "author": d["author"]["name"]
            }
            comments.append(comment)
        return comments

    @staticmethod
    def get_album_data(url):
        data = extract_ldjson_blob(url, clean=True)
        props = get_props(data)
        kwords = data.get('keywords', "")
        if isinstance(kwords, str):
            kwords = kwords.split(", ")
        return {
            'dateModified': data.get('dateModified'),
            'datePublished': data.get('datePublished'),
            'description': data.get('description'),
            "url": data.get('id') or url,
            "title": data.get("name"),
            "type": data.get("type"),
            "n_tracks": data.get('numTracks'),
            'image': data.get('image'),
            'featured_track_num': props.get('featured_track_num'),
            'keywords': kwords
        }

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.title

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.url)


class BandcampLabel:
    def __init__(self, data, scrap=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if scrap:
            self.scrap()
        if not self.url:
            raise ValueError("bandcamp url is not set")

    def scrap(self):
        self._page_data = {}  # TODO
        return self._page_data

    @staticmethod
    def from_url(url):
        return BandcampLabel({"url": url}, scrap=False)

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @property
    def name(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def location(self):
        return self.data.get("location")

    @property
    def tags(self):
        return self.data.get("tags") or []

    @property
    def image(self):
        return self.data.get("image")

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.name

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.url)


class BandcampArtist:
    def __init__(self, data, scrap=True):
        self._url = data.get("url")
        self._data = data or {}
        self._page_data = {}
        if scrap:
            self.scrap()

    def scrap(self):
        if not self._url:
            return {}
        try:
            resp = requests.get(self._url)
            if not resp.ok:
                return {}
            soup = BeautifulSoup(resp.text, "html.parser")
            loc_tag = soup.find(id="band-name-location")
            name, location = None, None
            if loc_tag:
                name_span = loc_tag.find(class_="title")
                loc_span = loc_tag.find(class_="location")
                name = name_span.text.strip() if name_span else None
                location = loc_span.text.strip() if loc_span else None
            genre_tag = soup.find("dd", class_="genre") or soup.find("span", class_="genre")
            genre = genre_tag.text.strip() if genre_tag else None
            img_tag = soup.find("div", id="bio-container")
            image = None
            if img_tag:
                img = img_tag.find("img")
                image = img["src"] if img else None
            self._page_data = {k: v for k, v in {
                "name": name, "location": location,
                "genre": genre, "image": image,
            }.items() if v is not None}
        except Exception:
            self._page_data = {}
        return self._page_data

    @property
    def featured_album(self):
        return BandcampAlbum.from_url(self.url + "/releases")

    @property
    def featured_track(self):
        if not self.featured_album:
            return None
        return self.featured_album.featured_track

    @staticmethod
    def get_albums(url):
        albums = []
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        for album in soup.find_all("a"):
            title_tag = album.find("p", {"class": "title"})
            if not title_tag:
                continue
            title = title_tag.text.strip()
            art_div = album.find("div", {"class": "art"})
            art_img = art_div.find("img") if art_div else None
            art = art_img["src"] if art_img else None
            href = album.get("href", "")
            album_url = url + href
            albums.append(BandcampAlbum({"album_name": title,
                                         "image": art,
                                         "url": album_url}))
        return albums

    @property
    def albums(self):
        return self.get_albums(self.url)

    @staticmethod
    def from_url(url):
        return BandcampArtist({"url": url})

    @property
    def url(self):
        return self._url or self.data.get("url")

    @property
    def data(self):
        for k, v in self._page_data.items():
            self._data[k] = v
        return self._data

    @property
    def name(self):
        return self.data.get("title") or self.data.get("name") or \
               self.url.split("/")[-1]

    @property
    def location(self):
        return self.data.get("location")

    @property
    def genre(self):
        return self.data.get("genre")

    @property
    def tags(self):
        return self.data.get("tags") or []

    @property
    def image(self):
        return self.data.get("image")

    def __repr__(self):
        return self.__class__.__name__ + ":" + self.name

    def __str__(self):
        return self.url

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.url)
