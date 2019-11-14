#!/usr/bin/env python3
from datetime import datetime as dtime
import os
import sys
import web_scraper_tofiles
import web_scraper_lib

__version__ = 'v1.00'

if __name__ == '__main__':

    SETTING_PATH = os.path.realpath(os.path.dirname(__file__))+"/"
    SETTING_FILE = SETTING_PATH+"web_scraper_settings.json"
    HISTORY_FILE = SETTING_PATH+"web_scraper_history.csv"
    runTime = dtime.now().strftime("%Y-%m-%d %H:%M:%S")
    #print("%s %s is going to work at %s. %s" % (os.path.basename(__file__),
    #    __version__, runTime,sys.getdefaultencoding()) )

    JD = web_scraper_lib.JsonParser(SETTING_FILE)
    MOVIE_LIST_FILE = SETTING_PATH+JD.get("movie").get("list")
    webpage_max = JD.get('page_scrwap_max')

    # This list is to scrap websites.
    siteList = []

    if  JD.get('tofiles').get("enable") == "True":
        siteList.append(web_scraper_tofiles)

    if len(siteList) == 0:
        print("Wrong, we should choice at least one analyzer.")
        sys.exit()

    for site in siteList:
        scraper = site.site_scraper(JD)

        #Step 1. test for access with main url
        #print("====================================\n=> Try to access site : ", scraper.getMainUrl())
        if not scraper.checkMainUrl():
            continue

        #Step 2. Iterate category for this site
        for index, category in enumerate(JD.get("tofiles").get("category")):
            cateIdx = category.get("idx")
            #Step 3. setup Latest Id for this site/this category
            needNewLatestId = True
            #print("scraping [%s][%s]" % (scraper.sitename, cateIdx))

            #Step 4. iterate page (up to 10) for this site/this category
            for count in range(1, webpage_max+1):
                needKeepgoing = True
                #cateIdxNo = web_scraper_lib.getCateIdxFromStr(cateIdx)
                #scraper.getScrapUrl(cateIdxNo, count)
                url = category.get("url") + "&page="+str(count)
                boardList = scraper.getParseData(url)

                #print("info: url=%s" % url)

                #for board in boardList:
                for num, board in enumerate(boardList, start=1):
                    #print("info: board=%s" % board)
                    #게시판 제목
                    title = board.get_text().replace('\t', '').replace('\n', '')
                    href = board.get('href').replace('..', scraper.mainUrl)
                    #print("info: href=\t%s" % href)
                    boardIdNum = scraper.get_wr_id(href)
                    #print("[%d][%d] - %s" % (num, boardIdNum, title))

                    if needNewLatestId:
                        newLatestId = scraper.get_wr_id(href)
                        if newLatestId > 0:
                            #웹페이지상의 게시판번호와 실제 게시물번호는 다를 수 있음
                            #print("We set up for new latest ID %d." % newLatestId)
                            needNewLatestId = False
                        else:
                            print("Something wrong, cannot get new latest ID - %d." % newLatestId)

                    #boardList의 첫 게시물의 id를 확인
                    if num == 1:
                        if (category['history']> boardIdNum):
                            needKeepgoing = False
                            #print("needKeepgoing is false --> break \tcateIdx=%s,boardIdNum=%s" % (cateIdx,boardIdNum))
                            break
                    if cateIdx.find("movie")>-1:
                      matched_name = web_scraper_lib.checkTitleWithMovieList(title, MOVIE_LIST_FILE, \
                        JD.get("movie").get("video_codec"), JD.get("movie").get("resolution"), dtime.now().strftime("%Y") )
                    else:
                      matched_name=web_scraper_lib.checkTitleWithProgramList(title)

                    if not matched_name:
                        #print("info main matched_name ", title)
                        continue

                    if (category['history']> boardIdNum):
                        needKeepgoing = False
                        #print("needKeepgoing2 --> break")
                        break

                    #print("info: parse info=\t[%s][%s][%d][p. %d] - %s" % \
                    #        (scraper.sitename, cateIdx, boardIdNum, count, title))

                    magnet = scraper.getmagnetDataFromPageUrl(href)
                    #print("\t%s" % magnet)

                    #magnet was already downloaded.
                    if web_scraper_lib.check_magnet_history(HISTORY_FILE, magnet):
                        continue

                    if cateIdx.find("movie")>-1:
                      download_dir=JD.get("movie").get("download")
                    else:
                      download_dir=JD.get("download-base")+"/"+matched_name
                    #print(download_dir)
                    if not os.path.exists(download_dir):
                      os.makedirs(download_dir)

                    session_id = web_scraper_lib.get_session_id_torrent_rpc(JD)
                    web_scraper_lib.add_magnet_transmission_remote(magnet, JD, download_dir, session_id)

                    if cateIdx.find("movie")>-1:
                      #movie_list에서 삭제하기
                      f = open(MOVIE_LIST_FILE, "r", encoding="utf-8")
                      lines = f.readlines()
                      buffer = ""
                      for line in lines:
                        #print("info, main matched_name = %s, line = %s" % (matched_name, line))
                        if not matched_name in line:
                          #print("info, not contain: main matched_name = %s, line = %s" % (matched_name, line))
                          buffer += line
                        else:
                          # 영화리스트 파일에 매치되어 파일에 기록하지 않으니 다운받았다는 메시지다.
                          # 영화는 자주 다운로드 하지 않으니 일단 로그 놔두고, 메일 받는 것으로 하자.
                          print("info, remove in movie_list, matched_name = %s, line = %s" % (matched_name, line))
                      f.close()

                      f = open(MOVIE_LIST_FILE, "w", encoding="utf-8")
                      f.write(buffer)
                      f.close()
                    else:
                      web_scraper_lib.remove_transmission_remote(JD, session_id, matched_name)

                    web_scraper_lib.add_magnet_info_to_file(HISTORY_FILE,
                            runTime, scraper.sitename, title, magnet, matched_name)

                if not needKeepgoing:
                    break

            #Step 5. save scrap ID
            #scraper.saveNewLatestIDwithCate(cateIdx, newLatestId)
            JD.data["tofiles"]["category"][index]["history"]=newLatestId
            JD.write()
