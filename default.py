import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2
from jellyfin_api import JellyfinClient

# Plugin constants
ADDON_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def get_addon_setting(setting):
    return xbmcplugin.getSetting(setting)  # Removed ADDON_ID parameter

def log(msg):
    xbmc.log("[Jellyfin] " + str(msg), xbmc.LOGDEBUG)

def get_params():
    param_string = sys.argv[2][1:] if len(sys.argv) > 2 else ''
    param_pairs = param_string.split('&') if param_string else []
    return dict(pair.split('=') for pair in param_pairs if '=' in pair)

def add_directory_item(name, url, mode, icon='DefaultFolder.png', is_folder=True):
    u = BASE_URL + "?" + urllib.urlencode({'mode': mode, 'url': url})
    li = xbmcgui.ListItem(name, iconImage=icon)
    xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=li, isFolder=is_folder)

def main_menu():
    server_url = get_addon_setting('server_url')
    username = get_addon_setting('username')
    password = get_addon_setting('password')
    
    if not server_url or not username or not password:
        xbmcgui.Dialog().ok('Configuration Required', 'Please configure your Jellyfin server settings in the add-on settings.')
        return
    
    try:
        jellyfin = JellyfinClient(server_url, username, password)
        user_id = jellyfin.authenticate()
        
        if user_id:
            add_directory_item('Movies', user_id, 'movies')
            add_directory_item('TV Shows', user_id, 'tvshows')
            add_directory_item('Music', user_id, 'music')
        else:
            xbmcgui.Dialog().ok('Error', 'Failed to authenticate with Jellyfin server.')
    except Exception as e:
        log("Error in main_menu: " + str(e))
        xbmcgui.Dialog().ok('Error', str(e))
    
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_movies(user_id):
    try:
        server_url = get_addon_setting('server_url')
        username = get_addon_setting('username')
        password = get_addon_setting('password')
        
        jellyfin = JellyfinClient(server_url, username, password)
        jellyfin.authenticate()

        movies = jellyfin.get_movies(user_id)
        
        for movie in movies:
            url = BASE_URL + "?" + urllib.urlencode({'mode': 'play', 'url': movie['Id']})
            thumb = movie.get('PrimaryImageUrl')
            li = xbmcgui.ListItem(movie['Name'], iconImage='DefaultVideo.png')
            
            if thumb:
                li.setThumbnailImage(thumb)
            
            li.setInfo('video', {'title': movie['Name'], 'plot': movie.get('Overview', '')})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
        
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    except Exception as e:
        log("Error in list_movies: " + str(e))
        xbmcgui.Dialog().ok('Error', str(e))

def list_tv_shows(user_id):
    try:
        server_url = get_addon_setting('server_url')
        jellyfin = JellyfinClient(server_url, get_addon_setting('username'), get_addon_setting('password'))
        jellyfin.authenticate()

        tv_shows = jellyfin.get_tv_shows(user_id)

        for show in tv_shows:
            url = BASE_URL + "?" + urllib.urlencode({'mode': 'seasons', 'series_id': show['Id']})
            li = xbmcgui.ListItem(show['Name'], iconImage='DefaultVideo.png')

            thumb = show.get('PrimaryImageUrl')
            if thumb:
                li.setThumbnailImage(thumb)

            li.setInfo('video', {'title': show['Name'], 'plot': show.get('Overview', '')})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    except Exception as e:
        log("Error in list_tv_shows: " + str(e))
        xbmcgui.Dialog().ok('Error', str(e))

def list_seasons(series_id):
    try:
        server_url = get_addon_setting('server_url')
        username = get_addon_setting('username')
        password = get_addon_setting('password')
        jellyfin = JellyfinClient(server_url, username, password)
        user_id = jellyfin.authenticate()

        seasons = jellyfin.get_seasons(series_id, user_id)

        for season in seasons:
            url = BASE_URL + "?" + urllib.urlencode({'mode': 'episodes', 'series_id': series_id, 'season_id': season['Id']})
            li = xbmcgui.ListItem(season['Name'], iconImage='DefaultFolder.png')

            thumb = season.get('PrimaryImageUrl')
            if thumb:
                li.setThumbnailImage(thumb)

            li.setInfo('video', {'title': season['Name'], 'plot': season.get('Overview', '')})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    except Exception as e:
        log("Error in list_seasons: " + str(e))
        xbmcgui.Dialog().ok('Error', str(e))

def list_episodes(series_id, season_id):
    try:
        server_url = get_addon_setting('server_url')
        username = get_addon_setting('username')
        password = get_addon_setting('password')
        jellyfin = JellyfinClient(server_url, username, password)
        user_id = jellyfin.authenticate()

        episodes = jellyfin.get_episodes(series_id, season_id, user_id)

        for episode in episodes:
            url = BASE_URL + "?" + urllib.urlencode({'mode': 'play', 'url': episode['Id']})
            li = xbmcgui.ListItem(episode['Name'], iconImage='DefaultVideo.png')

            thumb = episode.get('PrimaryImageUrl')
            if thumb:
                li.setThumbnailImage(thumb)

            li.setInfo('video', {'title': episode['Name'], 'plot': episode.get('Overview', '')})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)

        xbmcplugin.endOfDirectory(ADDON_HANDLE)
    except Exception as e:
        log("Error in list_episodes: " + str(e))
        xbmcgui.Dialog().ok('Error', str(e))

def play_media(item_id):
    try:
        server_url = get_addon_setting('server_url')
        username = get_addon_setting('username')
        password = get_addon_setting('password')
        
        jellyfin = JellyfinClient(server_url, username, password)
        user_id = jellyfin.authenticate()
        
        # Try direct play first
        direct_url = jellyfin.get_direct_play_url(item_id)
        if direct_url:
            play_url = direct_url
        else:
            # Fall back to the original playback URL (transcoding)
            play_url = jellyfin.get_playback_url(item_id)

        if not play_url:
            xbmcgui.Dialog().ok('Error', 'Unable to retrieve playback URL.')
            return

        player = xbmc.Player()
        player.play(play_url)

    except Exception as e:
        log("Error in play_media: " + str(e))
        xbmcgui.Dialog().ok('Error', str(e))

params = get_params()
mode = params.get('mode', None)
url = params.get('url', None)

if mode is None:
    main_menu()
elif mode == 'movies':
    list_movies(url)
elif mode == 'tvshows':
    list_tv_shows(url)
elif mode == 'seasons':
    list_seasons(params.get('series_id'))
elif mode == 'episodes':
    list_episodes(params.get('series_id'), params.get('season_id'))
elif mode == 'play':
    play_media(url)
