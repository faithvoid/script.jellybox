import urllib
import urllib2
import json
import base64

class JellyfinClient:
    def __init__(self, server_url, username, password):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.access_token = None
        self.user_id = None
    
    def authenticate(self):
        auth_url = self.server_url + "/Users/AuthenticateByName"
        auth_data = {
            "Username": self.username,
            "Pw": self.password
        }
        
        headers = {
            "X-Emby-Authorization": "MediaBrowser Client=\"Jellyfin4Xbox\", Device=\"XBMC4Xbox\", DeviceId=\"jellyfin4xbox\", Version=\"1.0.0\"",
            "Content-Type": "application/json"
        }
        
        req = urllib2.Request(auth_url, json.dumps(auth_data), headers)
        response = urllib2.urlopen(req)
        data = json.load(response)
        
        self.access_token = data['AccessToken']
        self.user_id = data['User']['Id']
        return self.user_id
    
    def get_movies(self, user_id):
        url = self.server_url + "/Users/" + user_id + "/Items?Recursive=true&IncludeItemTypes=Movie&Fields=PrimaryImageAspectRatio,Overview"
        headers = {
            "X-Emby-Token": self.access_token,
            "Accept": "application/json"
        }
        
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        data = json.load(response)
        
        movies = []
        for item in data.get('Items', []):
            movie = {
                'Id': item.get('Id'),
                'Name': item.get('Name'),
                'Overview': item.get('Overview'),
                'PrimaryImageUrl': self._get_image_url(item.get('Id'), item.get('ImageTags', {}).get('Primary')),
                'PlaybackInfoUrl': "/Items/" + item.get('Id')
            }
            movies.append(movie)
        
        return movies
    
    def get_tv_shows(self, user_id):
        url = self.server_url + "/Users/" + user_id + "/Items?Recursive=true&IncludeItemTypes=Series&Fields=PrimaryImageAspectRatio,Overview"
        headers = {
            "X-Emby-Token": self.access_token,
            "Accept": "application/json"
        }
        
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        data = json.load(response)
        
        tv_shows = []
        for item in data.get('Items', []):
            tv_show = {
                'Id': item.get('Id'),
                'Name': item.get('Name'),
                'Overview': item.get('Overview'),
                'PrimaryImageUrl': self._get_image_url(item.get('Id'), item.get('ImageTags', {}).get('Primary')),
                'PlaybackInfoUrl': "/Shows/" + item.get('Id') + "/Seasons"
            }
            tv_shows.append(tv_show)
        
        return tv_shows
    
    def get_seasons(self, series_id, user_id):
        url = self.server_url + "/Shows/" + series_id + "/Seasons?UserId=" + user_id + "&Fields=PrimaryImageAspectRatio,Overview"
        headers = {
            "X-Emby-Token": self.access_token,
            "Accept": "application/json"
        }
        
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        data = json.load(response)
        
        seasons = []
        for item in data.get('Items', []):
            season = {
                'Id': item.get('Id'),
                'Name': item.get('Name'),
                'Overview': item.get('Overview'),
                'PrimaryImageUrl': self._get_image_url(item.get('Id'), item.get('ImageTags', {}).get('Primary')),
                'SeasonNumber': item.get('IndexNumber'),
                'PlaybackInfoUrl': "/Shows/" + series_id + "/Episodes?SeasonId=" + item.get('Id')
            }
            seasons.append(season)
        
        return seasons
    
    def get_episodes(self, series_id, season_id, user_id):
        url = self.server_url + "/Shows/" + series_id + "/Episodes?SeasonId=" + season_id + "&UserId=" + user_id + "&Fields=PrimaryImageAspectRatio,Overview"
        headers = {
            "X-Emby-Token": self.access_token,
            "Accept": "application/json"
        }
        
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        data = json.load(response)
        
        episodes = []
        for item in data.get('Items', []):
            episode = {
                'Id': item.get('Id'),
                'Name': item.get('Name'),
                'Overview': item.get('Overview'),
                'PrimaryImageUrl': self._get_image_url(item.get('Id'), item.get('ImageTags', {}).get('Primary')),
                'EpisodeNumber': item.get('IndexNumber'),
                'PlaybackInfoUrl': "/Items/" + item.get('Id')
            }
            episodes.append(episode)
        
        return episodes
    
    def _get_image_url(self, item_id, image_tag=None, image_type="Primary"):
        if not image_tag:
            return None
        return self.server_url + "/Items/" + item_id + "/Images/" + image_type + "?tag=" + image_tag
    
    def get_playback_url(self, item_id):
        url = self.server_url + "/Items/" + item_id + "/PlaybackInfo"
        headers = {
            "X-Emby-Token": self.access_token,
            "Accept": "application/json"
        }
    
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        data = json.load(response)
    
        if data.get('MediaSources'):
            media_source = data['MediaSources'][0]
            # The 'Path' might be a local file path on server, not URL.
            # Instead, use Jellyfin's streaming endpoint:
            play_url = self.server_url + "/Videos/" + item_id + "/stream" + "?api_key=" + self.access_token
            return play_url
        return None


    def get_direct_play_url(self, item_id, media_source_id=None):
        url = self.server_url + "/Items/" + item_id + "/PlaybackInfo?UserId=" + self.user_id

        request_data = {
            "MediaSourceId": media_source_id or item_id,
            "UserId": self.user_id,
            "DeviceProfile": {
                "MaxStreamingBitrate": 140000000,
                "DirectPlayProfiles": [
                    {"Container": "mp4", "Type": "Video"},
                    {"Container": "mkv", "Type": "Video"},
                    {"Container": "webm", "Type": "Video"}
                ],
                "TranscodingProfiles": [],
                "CodecProfiles": [],
                "SubtitleProfiles": [],
                "ResponseProfiles": []
            }
        }

        headers = {
            "X-Emby-Token": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        req = urllib2.Request(url, json.dumps(request_data), headers)
        response = urllib2.urlopen(req)
        data = json.load(response)

        reasons = data.get("TranscodingReasons", [])
        if not reasons:
            # Direct Play is possible
            return self.server_url + "/Videos/" + item_id + "/stream?Static=true&api_key=" + self.access_token
        else:
            # Transcoding is required
            print("Transcoding required. Reasons:", reasons)
            return None
