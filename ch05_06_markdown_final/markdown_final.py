# -*- coding: utf-8 -*-

import time
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import platform
from tqdm import tqdm
import pyperclip
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import requests
import json
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import subprocess
import markdown
import random
import re
from pprint import pprint as pp
from pathlib import Path
from json_flatten import flatten
import pandas as pd
from tabulate import tabulate
import os
from googlesearch import search
from urllib import parse
import xml.etree.ElementTree as ET
from xml_to_dict import XMLtoDict
import google.generativeai as genai

osName = platform.system()  # window 인지 mac 인지 알아내기 위한

C_END = "\033[0m"
C_BOLD = "\033[1m"
C_INVERSE = "\033[7m"
C_BLACK = "\033[30m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BGBLACK = "\033[40m"
C_BGRED = "\033[41m"
C_BGGREEN = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN = "\033[46m"
C_BGWHITE = "\033[47m"

# ------------------------------------------------------------------------------------------------ START #
# 개인 입력 / 수정이 필요한 부분
# ------------------------------------------------------------------------------------------------ START #

# 업로드 대상이 되는 티스토리 블로그 주소(본인들의 주소를 적어주시면 됩니다. 마지막 '/'는 붙여주지 마세요)
# tistory_blog_name = "https://itmap.tistory.com"
tistory_blog_name = "https://pemtinfo1.tistory.com"

# 업로드 대상이 되는 티스토리의 카테고리 이름을 적어주세요
tistory_category_name = "분양정보"

# bard AI를 이용하려면 (1) 을 입력 gemini AI를 이용하려면 (2) 그리고 이용하지 않으려면 (0)을 입력해 주세요 (default: gemini ai)
selected_AI_model = 2

# gemini 토큰 정보 입력
GOOGLE_GEMINI_API_KEY = ""

# 각 소제목별 정보의 수량(max = 3)
ITEMS_PER_SUBJECT = 1

# time 정보
PAUSE_TIME = 0.5  # 셀레니움 수행도중 중간중간 wait time
LOADING_WAIT_TIME = 2  # 웹 페이지의 로딩 시간
LOGIN_WAIT_TIME = 180  # 로그인 대기시간
CONTANTS_GENERATE_TIME = 20  # chatGPT 글 생성시간(초단위) - 의미없음!!! 잠깐동안 입력을 안받는 용도!!!
BARD_REQUEST_WAIT_TIME = 300

# 이미 검색된 키워드의 중복성 제거를위해 엑셀에 그 데이터들을 저장 후 리스트 비교를 함
# keyword_list_csv_path = '/Users/xxx/Desktop/crawling/playlist/keyword_lists.csv'  # for mac
keyword_list_csv_path = 'keyword_lists.csv'

# post md 파일이 저장될 위치
# post_md_location = r"O:\workspace\ree31206.github.io\_posts"
# post_md_location = r"/Users/xxx/Desktop/crawling/playlist"  # for mac
# post_md_location = r"O:\workspace\post_baskup"
post_md_location = r"O:\workspace"

# ------------------------------------------------------------------------------------------------ END #

# ======================================================================================================== START
# [시스템 공통 입력 정보]
# ======================================================================================================== START

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
random_user_agent = random.choice(user_agents)
fixed_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Whale/3.19.166.16 Safari/537.36'


# [시스템 공통 입력 정보]
# ======================================================================================================== END


# TODO: keyword list를 관리할 수 있게 만들기
# TODO: keyword list 중복과 보드 발행 제목 등을 비교하여 기발행된 포스팅에 대해서는 발행하지 않게 하기
# TODO: 제목 url 인코딩
# TODO: 검색결과가 없을때나 다른 response 에 대한 예외처리
# TODO: album 및 track 에 대한 결과가 역순으로 나오는데 이것을 ascending=False 으로 역순처리하였는데 추후 다른 알고리즘 처리

def init_driver():
    if osName not in "Windows":
        try:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223 --user-data-dir="~/Desktop/crawling/chromeTemp23"'],
                shell=True, stdout=subprocess.PIPE)  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9223 --user-data-dir="~/Desktop/crawling/chromeTemp23"'],
                shell=True, stdout=subprocess.PIPE)
    else:
        try:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9223 '
                             r'--user-data-dir="C:\chrometemp23"')  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen(
                r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9223 '
                r'--user-data-dir="C:\chrometemp23"')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    # service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\120.0.6099.71\\chromedriver.exe')
    # service = ChromeService(
    #     '/Users/xxx/.wdm/drivers/chromedriver/mac64/120.0.6099.71/chromedriver-mac-x64/chromedriver')  # for MAC
    _driver = webdriver.Chrome(service=service, options=options)
    _driver.implicitly_wait(LOADING_WAIT_TIME)
    return _driver


def get_cookies_session(driver, url):
    driver.get(url)
    sleep(LOADING_WAIT_TIME)

    _cookies = driver.get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
        print(f"{cookie['name']} = {cookie['value']}")

    _session = requests.Session()
    headers = {
        'User-Agent': random_user_agent,
    }

    _session.headers.update(headers)  # User-Agent 변경

    _session.cookies.update(cookie_dict)  # 응답받은 cookies로  변경

    # _cookies = driver.get_cookies()
    # for cookie in _cookies:
    #     cookie_dict[cookie['name']] = cookie['value']
    #     print(f"{cookie['name']} = {cookie['value']}")

    return _session


def tistory_login(driver):
    try:
        driver.get('https://www.tistory.com/auth/login#')
        sleep(LOADING_WAIT_TIME)
        driver.find_element(By.CLASS_NAME, 'link_profile')
        print(f'\n이미 로그인 되어 다음 과정으로 넘어가겠습니다.')
    except:
        driver.get('https://www.tistory.com/auth/login#')
        sleep(LOADING_WAIT_TIME)

        # 로그인 과정을 기다려주는 부분
        print(f'\n{C_BOLD}{C_RED}{C_BGBLACK}주의: 3분안에 로그인을 완료해주세요!!!(tistory main ID 로 로그인해야함){C_END}')
        pbar = tqdm(total=LOGIN_WAIT_TIME)
        for x in range(LOGIN_WAIT_TIME):
            sleep(1)
            try:
                driver.find_element(By.CLASS_NAME, 'link_profile')  # 해당 element 가 존재하는지 확인
                break
            except:
                pass
            pbar.update(1)
        pbar.close()


def tistory_write_and_make_md_file(_driver, keyword, AI_description_result, youtube_mv_info_df, google_search_info_df,
                                   vibe_album_df, vibe_track_df):

    # print(vibe_album_df)
    # print(vibe_track_df)

    # -------------------------------------------------------------
    # Markdown content 생성
    # -------------------------------------------------------------

    post_title = f"[{keyword.replace('+', ' - ')}] 가사 듣기 뮤비 정보"

    post_head = f"""---
title: "{post_title}"
author: Moon
categories: shopping
tags: [Top10, shopping]
pin: true
---

해당 게시물은 N사 [**VIBE**](https://vibe.naver.com/) 플랫폼을 통해 얻은 정보와 G사 [**검색엔진**](https://www.google.com), 유튜브(youtube) 검색결과를 통해 얻어진 결과를 통해 음악 정보(가수정보, 가사, 앨범, 트랙 등)를 제공하고 있습니다. 또한 AI 툴인 G사 [**bard**](https://bard.google.com/) 또는 G사 [**gemini**](https://blog.google/technology/ai/google-gemini-ai/)들을 이용하여 나온 결과물을 첨부하고 있으니 참고하시기 바랍니다.



"""

    ai_body = '## AI 검색결과'
    album_body = '## 곡 정보'
    track_body = '## 가사'
    preview_body = '## 1분 미리듣기'
    youtube_body = '## 유튜브(youtube) 검색 결과'
    google_search_body = '## 구글 검색 결과'

    ai_body = ai_body + f"""
    {AI_description_result}

---
"""

    vibe_album_reverse_df = vibe_album_df.iloc[::-1].reset_index(drop=True)  # dataframe 역순만들기
    for item_index in range(len(vibe_album_reverse_df[:ITEMS_PER_SUBJECT])):
        album_body = album_body + f"""
Album Title : {vibe_album_reverse_df['albumTitle'][item_index]}
Agency Name : {vibe_album_reverse_df['agencyName'][item_index]}
Production Name : {vibe_album_reverse_df['productionName'][item_index]}
ReleaseDate : {vibe_album_reverse_df['releaseDate'][item_index]}
Artist Name : {vibe_album_reverse_df['artistName'][item_index]}
Artist ImageUrl : 
![가수 이미지]({vibe_album_reverse_df['artist imageUrl'][item_index]})
Album ImageUrl : 
![앨범 이미지]({vibe_album_reverse_df['album imageUrl'][item_index]})
Size and Duration : {vibe_album_reverse_df['sizeAndDuration'][item_index]}
Artist Total Count : {vibe_album_reverse_df['artistTotalCount'][item_index]}
Description : {vibe_album_reverse_df['description'][item_index]}
Album Genres : {vibe_album_reverse_df['albumGenres'][item_index]}
Share Url : {vibe_album_reverse_df['shareUrl'][item_index]}

---
"""

    vibe_track_reverse_df = vibe_track_df.iloc[::-1].reset_index(drop=True)
    for item_index in range(len(vibe_track_reverse_df[:ITEMS_PER_SUBJECT])):
        track_body = track_body + f"""
{vibe_track_reverse_df['lyrics'][item_index]}

---
"""

    vibe_album_reverse_df = vibe_album_df.iloc[::-1].reset_index(drop=True)
    for item_index in range(len(vibe_album_reverse_df[:ITEMS_PER_SUBJECT])):
        preview_body = preview_body + f"""
<iframe src="https://vibe.naver.com/embed/album/{vibe_album_reverse_df['albumId'][item_index]}?width=600&amp;height=450&amp;isPC=true&amp;autoPlay=false" id="__vibe_embed" width="600" height="450" frameborder="no" scrolling="no" allowfullscreen=""></iframe>

---
"""

    for item_index in range(len(youtube_mv_info_df[:ITEMS_PER_SUBJECT])):
        youtube_body = youtube_body + f"""
제목 : {youtube_mv_info_df['title'][item_index]}
설명 : {youtube_mv_info_df['label'][item_index]}
<iframe width="560" height="315" src="https://www.youtube.com/embed/{youtube_mv_info_df['videoId'][item_index]}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

---
"""

    for item_index in range(len(google_search_info_df[:ITEMS_PER_SUBJECT])):
        google_search_body = google_search_body + f"""
제목 : {google_search_info_df['title'][item_index]}
설명 : {google_search_info_df['description'][item_index]}
링크 : {google_search_info_df['url'][item_index]}

---
"""

    post_content = post_head + ai_body + album_body + track_body + preview_body + youtube_body + google_search_body
    # post_content = markdown.markdown(post_content)   # markdown > html 로 변환

    # -------------------------------------------------------------
    # Markdown content 로 md 파일 생성 (for github page)
    # -------------------------------------------------------------

    # 현재 날짜를 이용해 파일명 생성
    yesterday = datetime.now() - timedelta(days=1)
    timestring = yesterday.strftime('%Y-%m-%d')

    # 파일명 생성
    filename = f"{timestring}-{keyword.replace('+', '_')}.md"

    # 파일 경로 설정
    filepath = os.path.join(post_md_location, filename)

    # 파일에 블로그 내용 작성 + 성공 실패에 따른
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(post_content)
            f.close()
        print(f"\nMD 파일 생성 성공!!!")
        # if keyword_idx is not None:
        #     df["posted"].values[keyword_idx] = 'O'
        #     df.to_csv(csv_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
    except:
        print(f"MD 파일 생성 실패!!!")
        # if keyword_idx is not None:
        #     df["posted"].values[keyword_idx] = 'X'
        #     df.to_csv(csv_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)

    # -------------------------------------------------------------
    # 티스토리예 셀레니움(selenium)을 사용하여 포스팅
    # -------------------------------------------------------------
    _driver.get(f'{tistory_blog_name}/manage/post')
    sleep(LOADING_WAIT_TIME)
    # _driver.maximize_window()  # 창 최대화

    # 이전에 쓰고 있는 글이 있어도 새로운 글을 작성하도록 alert popup 처리
    try:
        obj = _driver.switch_to.alert
        # msg = obj.text
        # print("Alert shows following message: " + msg)
        print(f'\nalert dismiss')
        # obj.accept()
        obj.dismiss()
        sleep(PAUSE_TIME)
    except:
        pass
        # print('no alert')

    # HTML 모드로 변환
    _driver.find_element(By.ID, 'editor-mode-layer-btn-open').click()
    sleep(PAUSE_TIME)
    # _driver.find_element(By.ID, 'editor-mode-html').click()  # html로 작성할 시
    _driver.find_element(By.ID, 'editor-mode-markdown').click()  # markdown 언어로 작성 시
    sleep(PAUSE_TIME)
    _driver.switch_to.alert.accept()  # html 모드 변환시 alert 처리
    sleep(PAUSE_TIME)

    # 카테고리 선택
    _driver.find_element(By.ID, 'category-btn').click()
    sleep(PAUSE_TIME)
    _driver.find_element(By.XPATH, f"//span[normalize-space()='{tistory_category_name}']").click()
    sleep(PAUSE_TIME)

    # 제목 입력
    _driver.find_element(By.ID, 'post-title-inp').click()
    sleep(PAUSE_TIME)
    pyperclip.copy(post_title)
    ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()  # for window
    # ActionChains(_driver).key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()  # for mac
    sleep(PAUSE_TIME)

    # 글쓰기
    _driver.find_element(By.CLASS_NAME, 'CodeMirror-line').click()
    sleep(PAUSE_TIME)
    pyperclip.copy(post_content)
    ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()  # for window
    # ActionChains(_driver).key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()  # for mac
    sleep(PAUSE_TIME)

    # 임시저장 버튼
    _driver.find_element(By.CLASS_NAME, 'btn-draft').click()
    print(f'\n티스토리 글이 임시저장 되었습니다. 최종 발행은 따로 진행 부탁드립니다.')
    sleep(PAUSE_TIME)

    # # 완료 버튼 누르기
    # _driver.find_element(By.ID, 'publish-layer-btn').click()
    # sleep(PAUSE_TIME)
    #
    # # 예약 버튼 누르기
    # ele = _driver.find_elements(By.CLASS_NAME, "btn_date")
    # _driver.execute_script("arguments[0].click();", ele[1])


def make_google_bard_data(driver, keyword):
    print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[쿠키값 저장 및 세션 리턴 시작]', C_END)
    session = get_cookies_session(driver, 'https://bard.google.com/')
    sleep(PAUSE_TIME)
    print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[쿠키값 저장 및 세션 리턴 완료]', C_END)

    from bardapi import Bard, SESSION_HEADERS

    my_headers = {'User-Agent': random_user_agent}
    session.headers.update(my_headers)

    print('')
    for key, value in session.cookies.get_dict().items():
        if key == '__Secure-1PSID':
            print(f'{key} : {value}')
            psid_token = value
        elif key == '__Secure-1PSIDCC':
            print(f'{key} : {value}')
        elif key == '__Secure-1PSIDTS':
            print(f'{key} : {value}')
        else:
            pass

    print(f'\nbard 질문 키워드는 ({keyword}) 입니다.')
    bard = Bard(token=psid_token, session=session, timeout=30)
    answer = bard.get_answer(f"'{keyword}' 라는 가수 및 노래에 대해 자세히 설명해줘")

    print(answer)
    try:
        # result = markdown.markdown(answer['choices'][0]['content'][0])  # HTML 로 포스팅 할때
        result = answer['choices'][0]['content'][0]  # markdown 으로 포스팅 할때
        print(f'bard result = {result}')
        return result
    except:
        print(f"너무 많은 바드 요청이 있었습니다. ({BARD_REQUEST_WAIT_TIME})초간 대기 후 다시금 시도하겠습니다.")
        sleep(BARD_REQUEST_WAIT_TIME)
        make_google_bard_data(driver, keyword)


def make_google_gemini_data(keyword):
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    print(f'\ngemini 질문 키워드는 ({keyword}) 입니다.')
    answer = model.generate_content(f"'{keyword}' 라는 가수 및 노래에 대해 자세히 설명해줘")

    try:
        # result = markdown.markdown(answer.text)  # HTML 로 포스팅 할때
        result = answer.text  # markdown 으로 포스팅 할때
        print(result)
        return result
    except Exception as e:
        print('\n' + C_BOLD + C_RED + C_BGBLACK + '[정보를 가져오는데 실패하였습니다. ERROR를 확인해 주세요!!!]', C_END)
        print(f'{type(e).__name__}: {e}')
        return ''


def get_youtube_info(keyword):
    # TODO: 현재로는 검색어에 MV 라는것을 붙여서 관련 MV를 좀더 잘 찾을 수 있도록 되어있지만 개인적으로 변경이 가능
    # url = f'https://www.youtube.com/results?search_query=김범수+꿈일까+MV'
    url = f'https://www.youtube.com/results?search_query={keyword}+MV'
    headers = {
        'User-Agent': random_user_agent,
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    # print(soup)

    # 참조 - https://www.javatpoint.com/how-to-extract-youtube-data-in-python
    data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
    data_json = json.loads(data)  # 딕셔너리로 변환
    # pp(data_json)

    # ----------------------------------------------------------------
    # 너무 복잡한 json 파일 분석 tip 1 (flatten 함수를 활용하자!!)
    # ----------------------------------------------------------------
    flat_json = flatten(data_json)  # json 데이터를 flat하게 보여줘 확인하기 쉽게 만들어 줌
    # print(flat_json)

    # ----------------------------------------------------------------
    # 너무 복잡한 json 파일 분석 tip 2 (json_normalize 함수를 활용하자!!)
    # ----------------------------------------------------------------
    df = pd.json_normalize(data_json)
    # df = pd.json_normalize(data_json, record_path='contents.twoColumnSearchResultsRenderer.primaryContents.sectionListRenderer.contents')
    # print(tabulate(df, headers='keys', tablefmt='grid'))
    csv_path = f'youtube_normalize_info.csv'
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
    else:
        df.to_csv(csv_path, mode='a', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False, header=False)

    # ----------------------------------------------------------------
    # 너무 복잡한 json 파일 분석 tip 3 (json 파일을 저장해서 전반적인 구조를 살펴라!!)
    # ----------------------------------------------------------------
    youtube_info_path = "youtube_info.json"
    Path(youtube_info_path).touch(exist_ok=True)
    with open(youtube_info_path, 'w', encoding="UTF-8") as output_file:
        json.dump(data_json, output_file, ensure_ascii=False, indent=4, separators=(',', ': '))
        # print(f'\n유튜브 json path가 너무 커서 이를 저장을 위해 python 객체(dict)를 json.dump를 사용하여 json 파일로 저장\n')

    # ----------------------------------------------------------------
    # 너무 복잡한 json 파일 분석 tip 4 (postman 과 같은 프로그램을 활용해라!!)
    # ----------------------------------------------------------------

    # print(list(data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0].keys())[0])
    # print(data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][
    #           0]['itemSectionRenderer']['contents'][0]['videoRenderer']['videoId'])
    # print(data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][
    #           0]['itemSectionRenderer']['contents'][1]['videoRenderer']['videoId'])

    youtube_mv_info_lists = []
    for i in range(3):
        temp_dic = {}
        if list(data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][i].keys())[0] == 'videoRenderer':
            temp_dic['videoId'] = \
                data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                    'contents'][
                    0]['itemSectionRenderer']['contents'][i]['videoRenderer']['videoId']  # videoId
            temp_dic['thumbnail'] = \
                data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                    'contents'][
                    0]['itemSectionRenderer']['contents'][i]['videoRenderer']['thumbnail']['thumbnails'][1][
                    'url']  # 썸네일 url
            temp_dic['title'] = \
                data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                    'contents'][
                    0]['itemSectionRenderer']['contents'][i]['videoRenderer']['title']['runs'][0]['text']  # 제목
            temp_dic['label'] = \
                data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                    'contents'][
                    0]['itemSectionRenderer']['contents'][i]['videoRenderer']['title']['accessibility'][
                    'accessibilityData']['label']  # 설명
            youtube_mv_info_lists.append(temp_dic)

    df = pd.DataFrame(youtube_mv_info_lists)
    # print(tabulate(df, headers='keys', tablefmt='grid'))

    print('')
    for idx in df.index:
        print(
            f"{idx + 1}. {df.loc[idx, 'videoId']} | {df.loc[idx, 'thumbnail']} | {df.loc[idx, 'title']} | {df.loc[idx, 'label']}")

    # video_id = data_json['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['videoRenderer']['videoId']
    # youtube_mv_link = f'https://www.youtube.com/embed/{video_id}'

    # TODO: frame 형태로 티스토리에 넣어주기
    # <p><iframe src="https://www.youtube.com/embed/6P8y1sImLWM" width="860" height="484" frameborder="0" allowfullscreen="true"></iframe></p>

    return df


def get_google_search_info(keyword):
    result_lists = search(f"{keyword}+MV", num_results=10, advanced=True)  # 3개의 결과값만 가져오도록 함

    # print(type(result_lists))  # generator type

    google_search_info_lists = []
    # print('')
    for result in result_lists:
        temp_dic = {'title': result.title, 'description': result.description, 'url': result.url}
        # print(f"{result.title} | {result.description} | {result.url}")
        google_search_info_lists.append(temp_dic)

    df = pd.DataFrame(google_search_info_lists)
    df.drop_duplicates(subset=['title', 'description', 'url'],
                       keep="first")  # 중복제거를할때 남길 행입니다. first면 위에서부터 첫값을 남기고 last면 행의 마지막 값을 남깁
    df = df[:3]  # 위 search 함수에서 generator 를 통해 10개의 데이터를 뽑았지만 우리가 필요한건 3개의 데이터

    print('')
    for idx in df.index:
        print(f"{idx + 1}. {df.loc[idx, 'title']} | {df.loc[idx, 'description']} | {df.loc[idx, 'url']}")

    # print(tabulate(df, headers='keys', tablefmt='grid'))
    # TODO: frame 형태로 티스토리에 넣어주기
    # <p><iframe src="https://music.bugs.co.kr/track/33037375?wl_ref=list_tr_08_chart" width="860" height="484" frameborder="0" allowfullscreen="true"></iframe></p>

    return df


def get_vibe_info(keyword):
    # "https://vibe.naver.com/search?query=김범수+꿈일까+MV" 로 검색해서 개발자도구를 보면 아래와 같은 get 을 살펴볼수 있음
    # url = f'https://apis.naver.com/vibeWeb/musicapiweb/v4/searchall?query={parse.quote(keyword, encoding="utf-8")}'
    url = f'https://apis.naver.com/vibeWeb/musicapiweb/v4/searchall?query={keyword}'
    headers = {
        'User-Agent': random_user_agent,
    }

    response = requests.get(url, headers=headers)
    # pp(response.text)

    # ----------------------------------------------------------------
    # ElementTree 객체생성을 사용한 방법
    # ----------------------------------------------------------------
    # root = ET.fromstring(response.text)
    # for child in root.iter('*'):
    #     print(child.tag, child.attrib)

    # ----------------------------------------------------------------
    # xml_to_dict 패키지를 이용하여 활용하는 방법
    # ----------------------------------------------------------------
    xd = XMLtoDict()

    # 앨범에 대한 정보
    album_info_lists = []
    searchall_info_response = response.content
    print('')
    albumTotalCount = int(xd.parse(searchall_info_response)['response']['result']['albumResult']['albumTotalCount'])
    print('albumTotalCount ==>', albumTotalCount)
    for i in range(albumTotalCount):
        if i == albumTotalCount - 1:
            break
        temp_dic = {}
        if albumTotalCount == 1:
            album_id = xd.parse(searchall_info_response)['response']['result']['albumResult']['albums']['album'][
                'albumId']
        else:
            album_id = xd.parse(searchall_info_response)['response']['result']['albumResult']['albums']['album'][i][
                'albumId']
        url = f'https://apis.naver.com/vibeWeb/musicapiweb/album/{album_id}?includeDesc=true&includeIntro=true'
        print(
            '# ---------------------------------------------------------------------------------------------------------------------')
        print(f"album list ({i + 1}): ", url)
        headers = {
            'User-Agent': random_user_agent,
        }
        response = requests.get(url, headers=headers)
        try:
            albumTitle = xd.parse(parse.unquote(response.content))['response']['result']['album']['albumTitle']  # 꿈일까
        except:
            albumTitle = ''
        try:
            agencyName = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'agencyName']  # 영엔터테인먼트
        except:
            agencyName = ''
        try:
            productionName = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'productionName']  # (주)지니뮤직_Stone Music Entertainment
        except:
            productionName = ''
        try:
            releaseDate = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'releaseDate']  # 2023.12.4
        except:
            releaseDate = ''
        try:
            artistName = xd.parse(parse.unquote(response.content))['response']['result']['album']['artists']['artists'][
                'artistName']  # 김범수
        except:
            artistName = ''
        try:
            artist_imageUrl = \
            xd.parse(parse.unquote(response.content))['response']['result']['album']['artists']['artists'][
                'imageUrl']  # https://musicmeta-phinf.pstatic.net/artist/000/002/2016.jpg?type=r300&v=20231201180029
        except:
            artist_imageUrl = ''
        try:
            album_imageUrl = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'imageUrl']  # https://musicmeta-phinf.pstatic.net/album/030/419/30419062.jpg?type=r480Fll&v=20231201182447
        except:
            album_imageUrl = ''
        try:
            sizeAndDuration = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'sizeAndDuration']  # 2곡, 8분 22초
        except:
            sizeAndDuration = ''
        try:
            artistTotalCount = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'artistTotalCount']  # 1
        except:
            artistTotalCount = ''
        try:
            description = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'description']  # 우린 가끔 잊을 수 없는 꿈을 꾸곤 한다. \n꿈속에서 만난 연인을 생생하게 기억하고 현실과 꿈이 뒤엉켜버려 그 연인과의 운명적
        except:
            description = ''
        try:
            albumGenres = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'albumGenres']  # 발라드, 알앤비/어반
        except:
            albumGenres = ''
        try:
            shareUrl = xd.parse(parse.unquote(response.content))['response']['result']['album'][
                'shareUrl']  # https://vibe.naver.com/album/30419062
        except:
            shareUrl = ''

        temp_dic['albumId'] = album_id
        temp_dic['albumTitle'] = albumTitle
        temp_dic['agencyName'] = agencyName
        temp_dic['productionName'] = productionName
        temp_dic['releaseDate'] = releaseDate
        temp_dic['artistName'] = artistName
        temp_dic['artist imageUrl'] = artist_imageUrl
        temp_dic['album imageUrl'] = album_imageUrl
        temp_dic['sizeAndDuration'] = sizeAndDuration
        temp_dic['artistTotalCount'] = artistTotalCount
        temp_dic['description'] = description
        temp_dic['albumGenres'] = albumGenres
        temp_dic['shareUrl'] = shareUrl
        print(
            f"{i + 1}. {album_id} | {albumTitle} | {agencyName} | {productionName} | {releaseDate} | {artistName} | {artist_imageUrl} | {album_imageUrl} | {sizeAndDuration} | {artistTotalCount} | {description} | {albumGenres} | {shareUrl}")
        album_info_lists.append(temp_dic)

    # track 에 대한 정보
    track_info_lists = []
    print('')
    trackTotalCount = int(xd.parse(searchall_info_response)['response']['result']['trackResult']['trackTotalCount'])
    for i in range(trackTotalCount):  # 0, 1
        if i == trackTotalCount - 1:
            break
        temp_dic = {}
        if trackTotalCount == 1:
            track_id = xd.parse(searchall_info_response)['response']['result']['trackResult']['tracks']['track'][
                'trackId']
        else:
            track_id = xd.parse(searchall_info_response)['response']['result']['trackResult']['tracks']['track'][i][
                'trackId']
        url = f'https://apis.naver.com/vibeWeb/musicapiweb/vibe/v4/lyric/{track_id}'
        print(
            '# ---------------------------------------------------------------------------------------------------------------------')
        print(f"track list ({i + 1}): ", url)
        headers = {
            'User-Agent': random_user_agent,
        }
        response = requests.get(url, headers=headers)
        try:
            lyrics = xd.parse(parse.unquote(response.content))['response']['result']['lyric']['normalLyric']['text']
        except:
            lyrics = ''
        # try:
        #     lyrics_list = xd.parse(parse.unquote(response.content))['response']['result']['lyric']['syncLyric']['contents']['contents']['text']['text']
        # except:
        #     lyrics_list = ''
        temp_dic['lyrics'] = lyrics
        # temp_dic['lyrics list'] = lyrics_list
        # print(f"{i + 1}. {lyrics} | {lyrics_list}")
        print(f"{i + 1}. {lyrics}")
        track_info_lists.append(temp_dic)

    # album_df = pd.DataFrame(album_info_lists).sort_index(ascending=False) # 역순으로해야 실제 검색결과랑 동일하나 추후 확인해 봐야 함
    # track_df = pd.DataFrame(track_info_lists).sort_index(ascending=False)

    album_df = pd.DataFrame(album_info_lists)
    track_df = pd.DataFrame(track_info_lists)

    # print(tabulate(album_df, headers='keys', tablefmt='grid'))
    # print(tabulate(track_df, headers='keys', tablefmt='grid'))
    return album_df, track_df


# main start
def main():
    try:
        print("\nSTART...")
        start_time = time.time()
        now = datetime.now()
        print("START TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))

        print('\n키워드 작성 예시: "김범수 꿈일까"와 같이 가수명과 노래제목을 검색어로 지정하면 됩니다.')
        keyword = input('검색(발행) 키워드를 입력하세요 : ')
        keyword = keyword.replace(' ', '+')

        # keyword = '김범수+꿈일까'
        # keyword = '자이언티+모르는사람'
        # keyword = '비오+미처버리겠다'

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 시작]', C_END)
        driver = init_driver()
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[티스토리 로그인 수동 과정 시작(주의 : 3분 이내에 로그인 과정을 끝내야 합니다...)]', C_END)
        tistory_login(driver)
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[로그인 수동 과정 완료]', C_END)

        if selected_AI_model == 1:
            print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[google bard를 이용하여 키워드에 따른 컨텐츠를 생산하기 시작]{C_END}')
            AI_description_result = make_google_bard_data(driver, keyword)
            sleep(PAUSE_TIME)
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[google bard를 이용하여 키워드에 따른 컨텐츠를 생산하기 완료]', C_END)
        elif selected_AI_model == 2:
            print(f'\n{C_BOLD}{C_YELLOW}{C_BGBLACK}[google gemini를 이용하여 키워드에 따른 컨텐츠를 생산하기 시작]{C_END}')
            AI_description_result = make_google_gemini_data(keyword)
            sleep(PAUSE_TIME)
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[google gemini를 이용하여 키워드에 따른 컨텐츠를 생산하기 완료]', C_END)
        else:
            AI_description_result = ''

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[유튜브에서 검색하여 정보 가져오기]', C_END)
        # 참고. https://www.youtube.com/watch?v=6P8y1sImLWM 최종적으로 video id(6P8y1sImLWM)를 얻기 위함
        youtube_mv_info_df = get_youtube_info(keyword)
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[유튜브에서 검색하여 정보 가져오기 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[구글 검색하여 정보 가져오기]', C_END)
        google_search_info_df = get_google_search_info(keyword)
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[구글 검색하여 정보 가져오기 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버 VIBE에서 정보(가수, 앨범, 트랙, 가사 등) 가져오기]', C_END)
        vibe_album_df, vibe_track_df = get_vibe_info(keyword)
        # 참고 - 일상님 포멧으로 구성 - https://odaily.tistory.com/entry/%EB%AF%B8%EB%85%B8%EC%9D%B4-MEENOI-Ticket-%EC%8B%A0%EA%B3%A1-%EB%93%A3%EA%B8%B0-%EA%B0%80%EC%82%AC-%EB%AE%A4%EB%B9%84-MV-Lyrics-%ED%8B%B0%EC%BC%93-AOMG
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[네이버 VIBE에서 정보(가수, 앨범, 트랙, 가사 등) 가져오기 완료]', C_END)

        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[티스토리에 markdown 으로 포스팅 시작]', C_END)
        tistory_write_and_make_md_file(driver, keyword, AI_description_result, youtube_mv_info_df,
                                       google_search_info_df, vibe_album_df, vibe_track_df)
        sleep(PAUSE_TIME)
        print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[티스토리에 markdown 으로 포스팅 완료]', C_END)

    finally:
        # if (driver):
        #     driver.close()
        #     driver.quit()
        end_time = time.time()
        ctime = end_time - start_time
        time_list = str(timedelta(seconds=ctime)).split(".")
        print("\n실행시간 (시:분:초)", time_list)
        print("END...")
# main end

if __name__ == '__main__':
    main()


