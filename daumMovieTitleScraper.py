import scraperHelpers
import setting

class SiteScraper:
    def __init__(self, mySetting: setting.Setting):

        #today = datetime.date.today()
        #first = today.replace(day=1)
        #lastMonth = first - datetime.timedelta(days=1)

        #webpage_addr[RANKING] += lastMonth.strftime("%Y%m")
        self.mySetting = mySetting

    def checkUrl(self)->bool:
        if scraperHelpers.getResponse(self.getScrapUrl()) is None:
            return False
        return True

    def getScrapUrl(self)->str:
        return (self.mySetting.json["movie"]["titleScrap"]["url"])

    # 리스트의 url링크 리스트
    def getParseData(self):
        bsObj = scraperHelpers.getSoup(self.getScrapUrl())
        nameList = bsObj.find_all('a', attrs={'class' : 'link_txt'})
        if len(nameList) == 0:
            print(__file__+" getParseData 제목 클래스가 없어요. a tag's class: link_txt")
        return nameList

