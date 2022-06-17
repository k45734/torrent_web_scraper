#!/usr/bin/env python3

import os
import sys
import scraperHelpers
import re
import json
import configHelper 

def setSeasonTorrentFile(setting, torrentTitle, season):

    sessionId = scraperHelpers.getSessionIdTorrentRpc(setting)
    print("info, setSeasonTorrentFile session_id = "+sessionId)

    torrentId = scraperHelpers.getIdTransmissionRemote(setting, sessionId, torrentTitle)
    print("info, setSeasonTorrentFile id = "+torrentId)

    torrents = scraperHelpers.getFilesTorrentRemote(setting, sessionId, torrentId)
    print("info setSeasonTorrentFile torrents = "+torrents)

    for torrent in torrents:
        if "mp4" in torrent['name']:
            print("info setSeasonTorrentFile mp4_file "+torrent['name'])
            #dir = os.path.dirname(torrent['name'])
            fileName = os.path.basename(torrent['name'])
            replaceString = 's'+season+'\g<epi>'
            #re.sub('패턴', '바꿀문자열', '문자열', 바꿀횟수)
            newFileName = re.sub('(?P<epi>E\d+.)', replaceString, fileName)
            print("info setSeasonTorrentFile newFileName = "+newFileName)

            scraperHelpers.renameFileTorrentRpc(setting, torrentId, sessionId, torrent['name'], newFileName)
    return

if __name__ == '__main__':

    setting = configHelper.Setting()
    setting.loadJson()

    torrentTitle = sys.argv[1]
    print("info, main torrent_title = "+torrentTitle)

    # 시즌이 설정된 토렌트인가
    with open(setting.CONFIG_PATH + setting.json["tvshow"]["list"]) as TVShow:
      
        tvshowJson = json.load(TVShow)
      
        for tvshowTitle in tvshowJson['title_list']:

            tvshowTitleName = tvshowTitle['name']

            if tvshowTitleName in torrentTitle and len(tvshowTitle) >= 4:

              print("info, main program name = "+torrentTitle+", season = "+tvshowTitle['season'])
              setSeasonTorrentFile(setting.json, torrentTitle, tvshowTitle['season'])
            #else:
            #  print("not equal")
    sys.exit()

