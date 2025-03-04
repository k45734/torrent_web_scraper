import argparse
import json
import logging
import re
import bs4
import scraperHelpers
import setting
from urllib import parse

class BoardItemInfo:
    def __init__(self, title: str, url: str, ID: int, number: int) -> None:
        self.title = title
        self.url = url
        self.id = ID
        self.number = number

class BoardScraper():
    def getScrapUrl(self, url: str, page: int)->str:
        if page > 1:
            if not "?" in url:
                url += "?"
            return url + "&page="+str(page)
        else:
            return url

    def getBoardItemInfos(self, urlOrFilePath: str, page: int, titleTag: str, titleClass: str, titleSelector: str)->list:
        """
        게시판에서 제목리스트 얻기
        """
        logging.debug(f'게시판에서 제목리스트를 추출합니다. {urlOrFilePath}, tag: {titleTag}, class: {titleClass}, selecotr: {titleSelector}')
        if urlOrFilePath.startswith("http"):
            urlOrFilePath = self.getScrapUrl(urlOrFilePath, page)
            soup = scraperHelpers.getSoup(urlOrFilePath)
        else:
            soup = scraperHelpers.getSoupFromFile(urlOrFilePath)
        if soup is None:
            return [];
        if titleSelector == None or titleSelector == "":
            titles = soup.find_all(titleTag, class_=titleClass)
        else:
            titles = soup.select(titleSelector)
        if titles is None or not any(titles):
            return [];
        results = []
        for title in titles:
            aTag = title.a
            if aTag == None:
                continue;
            # category link
            if len(aTag.text.strip()) < 8:
                aTag = title.a.next_sibling
            if aTag == None:
                continue;
            if len(aTag.text.strip()) == 0 or aTag.get('href') == "#":
                continue;
        
            parentContents = list(filter(lambda a: a != '\n', title.parent.contents))
            numberString = parentContents[0].text.replace('\n', '')
            if numberString == None:
                parentContents = list(filter(lambda a: a != '\n', title.parent.parent.contents))
                numberString = parentContents[0].text.replace('\n', '')
            if numberString == None:
                parentContents = list(filter(lambda a: a != '\n', title.parent.parent.parent.contents))
                numberString = parentContents[0].text.replace('\n', '')
            if numberString != None:
                numberString = numberString.strip()
                if numberString == "AD" or numberString == "광고" or numberString == "공지":
                    continue;
                elif numberString.lower() == "new":
                    logging.debug("게시물 번호가 NEW입니다.")
                    boardNumber = 0
                else:
                    boardNumber = self.intTryParse(numberString)
                    if boardNumber == None:
                        parentContents = list(filter(lambda a: a != '\n', title.parent.parent.contents))
                        numberString = parentContents[0].text.replace('\n', '')
                        if numberString != None:
                            numberString = numberString.strip()
                            boardNumber = self.intTryParse(numberString)
                        if boardNumber == None:
                            logging.debug("게시물 번호를 찾을 수 없어요.2")
                            boardNumber = 0
            else:
                logging.debug("게시물 번호를 찾을 수 없어요.")
                boardNumber = 0
            boardItemInfo = self.GetBoardItemInfo(aTag, int(boardNumber))
            if boardItemInfo.id > 10:
                results.append(boardItemInfo)
            elif boardItemInfo.id == -1:
                logging.info(f"게시물 아이디를 확인할 수 없습니다. title: {boardItemInfo.title}")

        return results
 
    def intTryParse(self, value):
        try:
            return int(value)
        except ValueError:
            return ;

    def getID(self, url: str)->int:
        """게시판 아이디 파싱, url을 기반으로 wr_id text를 뒤의 id parsing"""
        match = re.search(r"wr_id=[^&?\n]+", url)
        if match:
            return int(match.group().replace("wr_id=", ""))

        match = re.search(r"[&?](id)=[0-9]+", url)
        if match:
            return int(match.group().replace("&", "").replace("?","").replace("id=", ""))

        match = re.search(r"[/][0-9]{6,}", url)
        if match:
            return int(match.group().replace("/",""))

        match = re.search(r"([0-9]){6,}", url)
        if match:
            return int(match.group())
        #print("게시물 아이디 얻기에 실패하였습니다. "+url)
        return -1

    def GetBoardItemInfo(self, aTag: bs4.element.Tag, boardNumber: int) -> BoardItemInfo:
        url = aTag.get('href')
        id = self.getID(url)
        if id == -1:
            id = boardNumber
        boardItemInfo = BoardItemInfo(aTag.text.replace('\n', ''), url, id, boardNumber)
        return boardItemInfo

    def getMagnet(self, url: str)->str:
        logging.debug(f'magnet을 검색합니다. url: {url}')
        html = scraperHelpers.getHtml(url)

        if html is None:
            logging.error(f'url로부터 html을 얻지 못했어요. url: {url}')
            return ""
        
        match = re.search(r"[ :]([A-Za-z0-9]){40}[^\w.]", html)
        if match:
            logging.debug(f'magnet을 찾았어. {match.group()[1:-1]}')
            return "magnet:?xt=urn:btih:"+ match.group()[1:-1]
        f = open("/tmp/magnet_fail.html", 'w')
        f.write(html)
        f.close()
        logging.error(f'html에서 magnet을 찾지 못했어요. url: {url}')
        return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("urlOrFilePath", help="스크랩할 url이나 html파일경로")
    parser.add_argument("--titleTag", help="제목 태그")
    parser.add_argument("--titleClass", help="제목 클래스")
    parser.add_argument("--titleSelector", help="제목 selector")
    args = parser.parse_args()
    # 로그파일 초기화용
    mySetting = setting.Setting()
    myBoardScraper = BoardScraper()
    # 매그넷 구하기
    if args.titleTag is not None or args.titleSelector is not None:
        logging.info(f'스크랩 테스트를 시작합니다. [{args.urlOrFilePath}], selector: [{args.titleSelector}], tag: [{args.titleTag}], class: [{args.titleClass}]')
        boardItems = myBoardScraper.getBoardItemInfos(args.urlOrFilePath, 1, args.titleTag, args.titleClass, args.titleSelector)
        if not boardItems:
            logging.error(f"게시판에서 제목리스트 얻기에 실패하였습니다.")
        print(json.dumps(boardItems, default=lambda x: x.__dict__))
        logging.info("스크랩 테스트를 마쳤습니다.")
    else:
        url = parse.unquote(args.urlOrFilePath)
        print(myBoardScraper.getMagnet(url))