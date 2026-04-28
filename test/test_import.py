def test_import():
    from py_bandcamp import BandCamp, BandcampTrack, BandcampAlbum, BandcampArtist, BandcampLabel


def test_version():
    from py_bandcamp.version import __version__
    assert __version__
