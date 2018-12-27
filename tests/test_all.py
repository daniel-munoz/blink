import os
import pytest
import yaml
from blink.blink import Blink


@pytest.fixture(scope='class')
def credentials():
    config_fn = os.path.join(os.path.expanduser("~"), '.blinkconfig')
    if os.path.isfile(config_fn):
        with open(config_fn) as f:
            config = yaml.load(f.read())
            if isinstance(config, dict):
                if len(config) == 1:
                    _email, _password = list(config.items())[0]
                if len(config) > 1:
                    raise Exception('Multiple email/passwords found in .blinkconfig. Please specify which ones to use.')
            else:
                raise Exception('File .blinkconfig must be a YAML dictionary. Currently it is a %s.' % type(config))
        return dict(email=_email, password=_password)
    return {}


class TestBlink:
    def test_connect(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        assert b.connected is False
        b.connect()
        assert b.connected is True

    def test_homescreen(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        data = b.homescreen()
        assert data['account'] is not None

    def test_events(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        events = b.events(b.networks[0])
        assert type(events) == list

    def test_cameras(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        cameras = b.cameras(b.networks[0])
        assert type(cameras) == list

    def test_download_video(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        events = b.events(b.networks[0])
        if events:
                event = events[0]
                b.download_video(event)

    def test_videos_list(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        videos = b.videos()
        assert len(videos) > 0
        print(videos[:10])

    def test_download_by_address(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        videos = b.videos()
        b.download_video_by_address(videos[0]['address'])

    def _test_download_thumbnail(self, credentials):
        '''doesn't work'''
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        network_id = b.networks[0]['id']
        events = b.events(network_id)
        event = events[0]
        b.download_thumbnail(event)

    def test_sync_modules(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        sync_modules = b.sync_modules(b.networks[0])
        print(sync_modules)

    def _test_arm(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        b.connect()
        print(b.arm(b.networks[0]))

    def test_clients(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        print(b.clients())

    def test_regions(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        print(b.regions())

    def test_health(self, credentials):
        b = Blink(credentials['email'], credentials['password'])
        print(b.health())
