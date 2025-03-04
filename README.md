**실행 환경**  
테스트 OS : 리눅스(우분투, 데비안, 라즈베리파이OS), 윈도우10, 윈도우11  
실행 언어 : Python3.6이상  
토렌트 클라이언트: [Transmission](https://transmissionbt.com)

# 1. 소개
등록된 키워드로 게시판을 검색하여 토렌트(마그넷)를 자동 추가 해주는 웹스크랩퍼(웹크롤러)입니다.

# 1.1 설치
## 1.1.1 transmission 설치
[https://transmissionbt.com](https://transmissionbt.com)에서 운영체제에 맞는 프로그램을 다운받아 설치합니다. 윈도우의 경우 transmission-daemon이 설치되도록 설치옵션을 변경해야 합니다.

## 1.1.2 설치
소스를 다운로드 받은 후에 다음 스크립트를 실행합니다.

    $ ./install.sh

# 1.2 설정
설치가 완료되면 config디렉토리의 setting.json 파일을 자신의 환경에 맞게 수정해주어야 합니다.

## 1.2.1 transmission 접속정보 설정
transmission과 통신할 호스트(아이피), 포트, 아이디와 패스워드를 지정합니다. 웹브라우저에서 http://[transmission이 실행중인 아이피]:9091로 접속을 확인해 보는 것이 좋습니다. 우분투, 데비안의 경우 트랜스미션 데몬의 기본값을 변경하지 않은 경우에는 아래 설정을 변경하지 않아도 됩니다. 비밀번호는 설정파일에 저장하지 않고 실행할 때 파라미터로 전달할 수 있습니다.

    "transmission": {
        "host": "127.0.0.1",
        "port": 9091,
        "id": "transmission",
        "pw": "transmission"
    }

## 1.2.2 토렌트 사이트 설정 
도메인에 숫자가 변경되는 경우가 있을 때에는 수정합니다. 

    "mainUrl": "https://domainXXX.com/",

# 1.3 키워드 추가
TVShow.json 파일에 제목과 해상도 등을 옵션으로 추가로 지정할 수 있습니다. (옵션은 생략가능) 

    ,{"name": "제목", "option": "720", "option2":"Next"}

Movie.txt 파일에 추가할 수 있습니다. 코덱과 해상도는 config/setting.json에서 movie에서 변경할 수 있습니다.

    제목 2009

# 1.4 실행
실행시키면 게시판을 읽어와서 TVShow.json와 Movie.txt에 등록한 키워드를 검색하여 transmission에 추가됩니다. 웹사이트에서 데이터를 가지고 오는 것은 많은 시간이 걸릴 수 있습니다. 

    torrent_web_scraper$ python3 .

비밀번호를 지정할 수 있습니다. 

    torrent_web_scraper$ python3 . --transPass 비밀번호

# 1.5 스케줄러 등록
주기적으로 실행하게 설정해두면, 토렌트 사이트를 방문하여 새로 등록된 마그넷 파일이 있는지 확인하고, 자동으로 추가해줍니다. 
  
**주의** 

토렌트 사이트를 웹 스크래핑하는 것은 불법이 아닙니다. 하지만, 토렌트를 사용하여 영화, TV 프로그램등의 동영상을 배포 등은 저작권을 침해하는 불법입니다. 이점을 이해하고 실행 여부를 결정하세요.


# 변경이력
## 2.1.09
* 매그넷 다운받기 버그 수정
## 2.1.08
* uid, gid지원 (폴더권한)
## 2.1.07
* 폴더를 설정하지 않은 경우 다운로드가 완료되지 않았던 버그 수정
* transmission 로그인 설정이 되지 않은 경우 버그 수정
## 2.1.06
* 사이트 주소 갱신 개선
## 2.1.05
* magnet검색 버그 수정
## 2.1.04
* 스크랩 페이지 수 게시판별로 설정
* 지원 사이트 추가
* 사이트 접속시에 예외처리 추가
* selector 지원
## 2.1.03
* 실행방식 변경(비밀번호 파라미터 추가)
* 다운로드 폴더 권한 변경 개선
## 2.1.02
* 간헐적으로 사이트 주소가 바로 적용되지 않았던 버그 수정
## 2.1.01
* 간헐적으로 사이트 주소 갱신이 되지 않는 버그 수정
## 2.1.00 
* 사이트 주소 자동갱신
## 2.0.00
* 로그 개선
* 스크랩 사이트 추가 지원
## 2.0.00-beta2.11
* 디버그용 로그 개선
## 2.0.00-beta2.1
* 폴더 권한의 간헐적인 버그 수정
## 2.0.00-beta2
* 폴더 권한 관련 개선
## 2.0.00-beta1
* Movie.txt 에서 간헐적으로 삭제되지 않았던 버그 수정
* transmission 보안연결 지원
* 스크랩 페이지 2에서 3페이지 늘림(config/setting.json: scrapPage)
## 2.0.00-alpha3
* 폴더 권한 처리
## 2.0.00-alpha2
* 로그 추가
  * 설정파일 "logging" 추가
## 2.0.00-alpha1
* 설정파일 변경
  * "movie"에서 
    * "resolution": "1080"를 "resolution": 1080 숫자로 변경.
    * "video_codec"을 "videoCodec"으로 변경.
  * "sites"에서 
    * "board"제거(사용안함)
    * "category"를 "categories"로 변경.및 "title" 추가. 
  * "page_scrap_max"를 "scrapPage"로 변경.
  * torrentHistory, torrentFail 추가
