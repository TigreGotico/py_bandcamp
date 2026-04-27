import json

from py_bandcamp.session import SESSION as requests


def extract_blob(url, params=None):
    blob = requests.get(url, params=params).text
    for b in blob.split("data-blob='")[1:]:
        json_blob = b.split("'")[0]
        return json.loads(json_blob)
    for b in blob.split("data-blob=\"")[1:]:
        json_blob = b.split("\"")[0].replace("&quot;", '"')
        return json.loads(json_blob)


def _extract_tralbum(text):
    """Parse the data-tralbum HTML attribute and return the decoded dict."""
    if 'data-tralbum' not in text:
        return {}
    try:
        raw = text.split('data-tralbum="')[1].split('"')[0]
        raw = raw.replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&")
        return json.loads(raw)
    except Exception:
        return {}


def extract_ldjson_blob(url, clean=False):
    txt_string = requests.get(url).text

    json_blob = txt_string. \
        split('<script type="application/ld+json">')[-1]. \
        split("</script>")[0]

    data = json.loads(json_blob)

    def _clean_list(l):
        for idx, v in enumerate(l):
            if isinstance(v, dict):
                l[idx] = _clean_dict(v)
            if isinstance(v, list):
                l[idx] = _clean_list(v)
        return l

    def _clean_dict(d):
        clean = {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = _clean_dict(v)
            if isinstance(v, list):
                v = _clean_list(v)
            k = k.replace("@", "")
            clean[k] = v
        return clean

    if clean:
        return _clean_dict(data)
    return data


def get_props(d, props=None):
    props = props or []
    data = {}
    for p in d.get('additionalProperty') or []:
        if p['name'] in props or not props:
            data[p['name']] = p['value']
    return data


def get_stream_data(url):
    resp = requests.get(url)
    text = resp.text

    # ld+json gives metadata; data-tralbum gives the actual streaming URLs
    ld_blob = text.split('<script type="application/ld+json">')[-1].split("</script>")[0]
    data = json.loads(ld_blob)

    tralbum = _extract_tralbum(text)

    artist_data = data.get('byArtist') or {}
    album_data = data.get('inAlbum') or {}
    kws = data.get("keywords", "")
    if isinstance(kws, str):
        kws = kws.split(", ") if kws else []

    result = {
        "categories": data.get("@type"),
        'album_name': album_data.get('name'),
        'artist': artist_data.get('name'),
        'image': data.get('image'),
        "title": data.get('name'),
        "url": url,
        "tags": kws + data.get("tags", [])
    }

    # Try ld+json additionalProperty first (some tracks expose it there)
    for p in data.get('additionalProperty') or []:
        if p['name'] == 'file_mp3-128':
            result["stream"] = p["value"]

    # Fall back to data-tralbum trackinfo (more reliable)
    if "stream" not in result:
        trackinfo = tralbum.get("trackinfo") or []
        if trackinfo:
            mp3 = trackinfo[0].get("file", {}).get("mp3-128")
            if mp3:
                result["stream"] = mp3

    return result
