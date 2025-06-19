# Jellybox - Jellyfin client for XBMC4Xbox / XBMC4Gamers
![Movies](screenshots/movies.jpg)
Movies
![2](screenshots/tv.jpg)
TV (Episodes View)
![3](screenshots/nowplaying.jpg)
Now Playing

## How to Use:
- Make sure you have Jellyfin installed and set up with your ideal transcoding settings on your host PC!
- Copy the "Jellybox" folder into to Q:/plugins/video
- In XBMC, select "Video Add-ons", then open up the context menu on "Jellybox", select "Plug-in settings" and enter your Jellyfin IP address, username and password. (this may work for external instances, but that's untested!)
- Run Jellybox, select the category you'd like to view content in, and enjoy!

## TODO:
- Clean up UI a bit (maybe add "Play in Order" context option?)

## FAQ:
- Will this support "XYZ" codec?
- If your machine running Jellyfin can transcode it, yes. Otherwise, no, as Jellybox will always attempt direct play first, then transcoded video if the video's not supported.
