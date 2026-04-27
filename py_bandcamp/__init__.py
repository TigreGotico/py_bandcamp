from bs4 import BeautifulSoup

from py_bandcamp.models import BandcampTrack, BandcampAlbum, BandcampArtist, BandcampLabel
from py_bandcamp.session import SESSION as requests, set_session
from py_bandcamp.utils import extract_ldjson_blob, get_props, extract_blob, \
    get_stream_data


class BandCamp:
    @staticmethod
    def tags(tag_list=True):
        data = extract_blob("https://bandcamp.com/tags")
        tags = {"genres": data["signup_params"]["genres"],
                "subgenres": data["signup_params"]["subgenres"]}
        if not tag_list:
            return tags
        tag_list = []
        for genre in tags["subgenres"]:
            tag_list.append(genre)
            tag_list += [sub["norm_name"] for sub in tags["subgenres"][genre]]
        return tag_list

    @classmethod
    def search_tag(cls, tag, page=1, pop_date=1):
        tag = tag.strip().replace(" ", "-").lower()
        if tag not in cls.tags():
            return []
        params = {"page": page, "sort_field": pop_date}
        url = 'http://bandcamp.com/tag/' + str(tag)
        data = extract_blob(url, params=params)

        related_tags = [{"name": t["norm_name"], "score": t["relation"]}
                        for t in data["hub"].pop("related_tags")]

        collections, dig_deeper = data["hub"].pop("tabs")
        dig_deeper = dig_deeper["dig_deeper"]["results"]
        collections = collections["collections"]

        _to_remove = ['custom_domain', 'custom_domain_verified', "item_type",
                      'packages', 'slug_text', 'subdomain', 'is_preorder',
                      'item_id', 'num_comments', 'tralbum_id', 'band_id',
                      'tralbum_type', 'tag_id', 'audio_track_id']

        for c in collections:
            if c["name"] == "bc_dailys":
                continue
            for result in c["items"]:
                result["image"] = "https://f4.bcbits.com/img/a{art_id}_1.jpg". \
                    format(art_id=result.pop("art_id"))
                for _ in _to_remove:
                    if _ in result:
                        result.pop(_)
                result["related_tags"] = related_tags
                result["collection"] = c["name"]
                if "tralbum_url" in result:
                    result["album_url"] = result.pop("tralbum_url")
                yield BandcampTrack(result, parse=False)

        for k in dig_deeper:
            for result in dig_deeper[k]["items"]:
                for _ in _to_remove:
                    if _ in result:
                        result.pop(_)
                result["related_tags"] = related_tags
                result["collection"] = "dig_deeper"
                if "tralbum_url" in result:
                    result["album_url"] = result.pop("tralbum_url")
                yield BandcampTrack(result, parse=False)

    @classmethod
    def search_albums(cls, album_name):
        for album in cls.search(album_name, albums=True, tracks=False,
                                artists=False, labels=False):
            yield album

    @classmethod
    def search_tracks(cls, track_name):
        for t in cls.search(track_name, albums=False, tracks=True,
                            artists=False, labels=False):
            yield t

    @classmethod
    def search_artists(cls, artist_name):
        for a in cls.search(artist_name, albums=False, tracks=False,
                            artists=True, labels=False):
            yield a

    @classmethod
    def search_labels(cls, label_name):
        for a in cls.search(label_name, albums=False, tracks=False,
                            artists=False, labels=True):
            yield a

    @classmethod
    def search(cls, name, page=1, albums=True, tracks=True, artists=True,
               labels=False):
        params = {"page": page, "q": name}
        response = requests.get('http://bandcamp.com/search', params=params)
        soup = BeautifulSoup(response.content, 'html.parser')

        seen = []
        for item in soup.find_all("li", class_="searchresult"):
            item_type = item.find('div', class_='itemtype').text.strip().lower()
            if item_type == "album" and albums:
                data = cls._parse_album(item)
            elif item_type == "track" and tracks:
                data = cls._parse_track(item)
            elif item_type == "artist" and artists:
                data = cls._parse_artist(item)
            elif item_type == "label" and labels:
                data = cls._parse_label(item)
            else:
                continue
            if data is None:
                continue
            yield data
            seen.append(data)
        if not seen:
            return  # no more pages
        for item in cls.search(name, page=page + 1, albums=albums,
                               tracks=tracks, artists=artists, labels=labels):
            if item in seen:
                return  # duplicate data, bail out of recursion
            yield item

    @staticmethod
    def get_track_lyrics(track_url):
        track_page = requests.get(track_url)
        track_soup = BeautifulSoup(track_page.text, 'html.parser')
        track_lyrics = track_soup.find("div", {"class": "lyricsText"})
        if track_lyrics:
            return track_lyrics.text
        return "lyrics unavailable"

    @classmethod
    def get_streams(cls, urls):
        if not isinstance(urls, list):
            urls = [urls]
        return [cls.get_stream_url(url) for url in urls]

    @classmethod
    def get_stream_url(cls, url):
        data = get_stream_data(url)
        return data.get("stream") or url

    @staticmethod
    def _parse_label(item):
        art_tag = item.find("div", {"class": "art"})
        art_img = art_tag.find("img") if art_tag else None
        art = art_img["src"] if art_img else None
        name = item.find('div', class_='heading').text.strip()
        url = item.find('div', class_='heading').find('a')['href'].split("?")[0]
        subhead = item.find('div', class_='subhead')
        location = subhead.text.strip() if subhead else ""
        try:
            tags = item.find('div', class_='tags').text.replace("tags:", "").split(",")
            tags = [t.strip().lower() for t in tags]
        except (AttributeError, KeyError):
            tags = []
        return BandcampLabel({"name": name, "location": location,
                              "tags": tags, "url": url, "image": art})

    @staticmethod
    def _parse_artist(item):
        name = item.find('div', class_='heading').text.strip()
        url = item.find('div', class_='heading').find('a')['href'].split("?")[0]
        genre_tag = item.find('div', class_='genre')
        genre = genre_tag.text.strip().replace("genre: ", "") if genre_tag else ""
        subhead = item.find('div', class_='subhead')
        location = subhead.text.strip() if subhead else ""
        try:
            tags = item.find('div', class_='tags').text.replace("tags:", "").split(",")
            tags = [t.strip().lower() for t in tags]
        except (AttributeError, KeyError):
            tags = []
        art_tag = item.find("div", {"class": "art"})
        art_img = art_tag.find("img") if art_tag else None
        art = art_img["src"] if art_img else None
        return BandcampArtist({"name": name, "genre": genre, "location": location,
                               "tags": tags, "url": url, "image": art, "albums": []},
                              scrap=False)

    @staticmethod
    def _parse_track(item):
        track_name = item.find('div', class_='heading').text.strip()
        url = item.find('div', class_='heading').find('a')['href'].split("?")[0]
        subhead = item.find('div', class_='subhead')
        subhead_text = subhead.text.strip() if subhead else ""
        if "by" in subhead_text:
            parts = subhead_text.split("by", 1)
            album_name = parts[0].strip().replace("from ", "")
            artist = parts[1].strip()
        else:
            album_name = subhead_text.replace("from ", "").strip()
            artist = ""
        released_tag = item.find('div', class_='released')
        released = released_tag.text.strip().replace("released ", "") if released_tag else ""
        try:
            tags = item.find('div', class_='tags').text.replace("tags:", "").split(",")
            tags = [t.strip().lower() for t in tags]
        except (AttributeError, KeyError):
            tags = []
        art_tag = item.find("div", {"class": "art"})
        art_img = art_tag.find("img") if art_tag else None
        art = art_img["src"] if art_img else None
        return BandcampTrack({"track_name": track_name, "released": released,
                              "url": url, "tags": tags, "album_name": album_name,
                              "artist": artist, "image": art}, parse=False)

    @staticmethod
    def _parse_album(item):
        art_tag = item.find("div", {"class": "art"})
        art_img = art_tag.find("img") if art_tag else None
        art = art_img["src"] if art_img else None
        album_name = item.find('div', class_='heading').text.strip()
        url = item.find('div', class_='heading').find('a')['href'].split("?")[0]
        length_tag = item.find('div', class_='length')
        tracks, minutes = "", ""
        if length_tag:
            length = length_tag.text.strip()
            parts = length.split(",")
            if len(parts) == 2:
                tracks = parts[0].replace(" tracks", "").replace(" track", "").strip()
                minutes = parts[1].replace(" minutes", "").strip()
        released_tag = item.find('div', class_='released')
        released = released_tag.text.strip().replace("released ", "") if released_tag else ""
        try:
            tags = item.find('div', class_='tags').text.replace("tags:", "").split(",")
            tags = [t.strip().lower() for t in tags]
        except (AttributeError, KeyError):
            tags = []
        artist = item.find("div", {"class": "subhead"}).text.strip()
        if artist.startswith("by "):
            artist = artist[3:]
        return BandcampAlbum({"album_name": album_name, "minutes": minutes,
                              "url": url, "image": art, "artist": artist,
                              "track_number": tracks, "released": released,
                              "tags": tags}, scrap=False)
