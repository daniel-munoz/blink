#!/usr/bin/python3
import dateutil.parser
import os
import pytz
import requests


class Network(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Network id=%s name=%s>' % (self.id, repr(self.name))


class Event(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Event id=%s camera=%s at=%s>' % (self.id,
                                                  repr(self.camera_name),
                                                  repr(self.created_at))


class SyncModule(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<SyncModule %s>' % repr(self.__dict__)


class Camera(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Camera id=%s name=%s>' % (self.id, repr(self.name))


class Blink(object):
    def __init__(self, email, password, server='prod.immedia-semi.com'):
        self._authtoken = None
        self._email = email
        self._password = password
        self._server = server
        if not self._email:
            raise Exception('Please specify an email address.')
        if not self._password:
            raise Exception('Please specify a password.')

    def _connect_if_needed(self):
        if not self._authtoken:
            self.connect()
        if not self.connected:
            raise Exception('Unable to connect.')

    @property
    def connected(self):
        return self._authtoken is not None

    @property
    def _auth_headers(self):
        return {'TOKEN_AUTH': self._authtoken['authtoken']}

    def _path(self, path):
        return 'https://%s/%s' % (self._server, path.lstrip('/'))

    def connect(self):
        headers = {
            'Content-Type': 'application/json',
            'Host': self._server,
        }
        data = {
            'email': self._email,
            'password': self._password,
            'client_specifier': 'Blink Home Security Camera Python API @ https://github.com/keredson/blink',
        }
        resp = requests.post(self._path('login'), json=data, headers=headers)
        if resp.status_code != 200:
            raise Exception(resp.json()['message'])
        raw = resp.json()
        self._networks_by_id = raw['networks']
        self.networks = []
        for network_id, network in self._networks_by_id.items():
            network = dict(network)
            network['id'] = network_id
            network = Network(**network)
            self.networks.append(network)
        self._region = raw['region']
        self._authtoken = raw['authtoken']
        self._server = 'rest-{}.immedia-semi.com'.format(list(self._region.keys())[0])

    def homescreen(self):
        '''
        Return information displayed on the home screen of the mobile client
        '''
        self._connect_if_needed()
        resp = requests.get(self._path('homescreen'), headers=self._auth_headers)
        return resp.json()

    def events(self, network, type='motion'):
        self._connect_if_needed()
        resp = requests.get(self._path('events/network/%s' % network.id), headers=self._auth_headers)
        events = resp.json()['event']
        if type:
            events = [e for e in events if e['type'] == 'motion']
        events = [Event(**event) for event in events]
        return events

    def cameras(self, network, type='motion'):
        self._connect_if_needed()
        resp = requests.get(self._path('network/%s/cameras' % network.id), headers=self._auth_headers)
        cameras = resp.json()['devicestatus']
        cameras = [Camera(**camera) for camera in cameras]
        return cameras

    def download_video_by_address(self, address):
        '''
            returns the mp4 data as a file-like object
        '''
        self._connect_if_needed()
        resp = requests.get(self._path(address), headers=self._auth_headers)
        return resp.content

    def download_video(self, event):
        '''
            returns the mp4 data as a file-like object
        '''
        return self.download_video_by_address(event.video_url)

    def download_thumbnail(self, event):
        '''
            returns the jpg data as a file-like object
            doesn't work - server returns 404
        '''
        self._connect_if_needed()
        thumbnail_url = self._path(event.video_url[:-4] + '.jpg')
        resp = requests.get(thumbnail_url, headers=self._auth_headers)
        return resp.content

    def sync_modules(self, network):
        '''
            Response: JSON response containing information about the known state of the Sync module,
            most notably if it is online
            Notes: Probably not strictly needed but checking result can verify that the sync module
            is online and will respond to requests to arm/disarm, etc.
        '''
        self._connect_if_needed()
        resp = requests.get(self._path('network/%s/syncmodules' % network.id), headers=self._auth_headers)
        return [SyncModule(**resp.json()['syncmodule'])]

    def arm(self, network):
        '''
            Arm the given network (start recording/reporting motion events)
            Response: JSON response containing information about the disarm command request,
            including the command/request ID
            Notes: When this call returns, it does not mean the disarm request is complete, the
            client must gather the request ID from the response and poll for the status of the command.
        '''
        self._connect_if_needed()
        resp = requests.post(self._path('network/%s/arm' % network.id), headers=self._auth_headers)
        return resp.json()

    def disarm(self, network):
        '''
            Disarm the given network (stop recording/reporting motion events)
            Response: JSON response containing information about the disarm command request,
            including the command/request ID
            Notes: When this call returns, it does not mean the disarm request is complete,
            the client must gather the request ID from the response and poll for the status of the command.
        '''
        self._connect_if_needed()
        resp = requests.post(self._path('network/%s/disarm' % network.id), headers=self._auth_headers)
        return resp.json()

    def command_status(self, network, command_id):
        '''
            Get status info on the given command
            Response: JSON response containing state information of the given command, most notably whether
            it has completed and was successful.
            Notes: After an arm/disarm command, the client appears to poll this URL every second or so until
            the response indicates the command is complete.
            Known Commands: lv_relay, arm, disarm, thumbnail, clip
        '''
        self._connect_if_needed()
        resp = requests.get(self._path('network/%s/command/%s' % (network.id, command_id)), headers=self._auth_headers)
        return resp.json()

    def clients(self):
        '''
            Request Gets information about devices that have connected to the blink service
            Response JSON response containing client information, including: type, name, connection time, user ID
        '''
        self._connect_if_needed()
        resp = requests.get(self._path('account/clients'), headers=self._auth_headers)
        return resp.json()

    def regions(self):
        '''
            Gets information about supported regions
        '''
        self._connect_if_needed()
        resp = requests.get(self._path('regions'), headers=self._auth_headers)
        return resp.json()

    def health(self):
        '''
            Gets information about system health
        '''
        self._connect_if_needed()
        resp = requests.get(self._path('health'), headers=self._auth_headers)
        return resp.json()

    def videos(self):
        '''
            Gets a list of all the available videos
        '''
        self._connect_if_needed()
        videos = []
        resp = requests.get(self._path('api/v2/videos/count'), headers=self._auth_headers)
        total = resp.json()['count']
        page = 0
        while len(videos) < total:
                resp = requests.get(self._path('api/v2/videos/page/{}'.format(page)), headers=self._auth_headers)
                if not resp.json():
                        break
                for video in resp.json():
                        videos.append(video)
                page += 1
        return videos

    # UTIL FUNCTIONS
    def archive(self, path):
        self._connect_if_needed()
        for network in self.networks:
            network_dir = os.path.join(path, network.name)
            if not os.path.isdir(network_dir):
                os.mkdir(network_dir)

            already_downloaded = set()
            for (dirname, subdirs, files) in os.walk(network_dir):
                for fn in files:
                        if not fn.endswith('.mp4'):
                            continue
                        already_downloaded.add(fn)

            videos = self.videos()
            for video in videos:
                address = video['address']
                when = dateutil.parser.parse(video['created_at'])
                utcmoment = when.replace(tzinfo=pytz.utc)
                when = utcmoment.astimezone(pytz.timezone(video['time_zone']))
                video_name = '{}-{}.mp4'.format(
                    video['camera_name'].replace(' ', '_'),
                    when.strftime('%Y-%m-%d_%H:%M:%S_%Z'))

                if video_name in already_downloaded:
                    print(f'Skipping {video_name}')
                    continue
                date_dir = os.path.join(network_dir, when.strftime('%Y-%m-%d'))
                if not os.path.isdir(date_dir):
                    os.mkdir(date_dir)
                video_fn = os.path.join(date_dir, video_name)
                print('Saving:', video_fn)
                mp4 = self.download_video_by_address(address)
                with open(video_fn, 'wb') as f:
                    f.write(mp4)
