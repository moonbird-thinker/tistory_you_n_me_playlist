# -*- coding: utf-8 -*-

import time
from datetime import timedelta
from datetime import datetime
import requests
import random
from time import sleep
import google.generativeai as genai
import platform
import subprocess
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import markdown

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

# ------------------------------------------------------------------------------------------------ START #
# 개인 입력 / 수정이 필요한 부분
# ------------------------------------------------------------------------------------------------ START #

# time 정보
PAUSE_TIME = 0.5  # 셀레니움 수행도중 중간중간 wait time
LOADING_WAIT_TIME = 3  # 웹 페이지의 로딩 시간
BARD_REQUEST_DELAY_TIME = 300
GEMINI_REQUEST_DELAY_TIME = 300

# bard AI를 이용하려면 (1) 을 입력 gemini AI를 이용하려면 (2) 그리고 이용하지 않으려면 (0)을 입력해 주세요 (default: gemini ai)
selected_AI_model = 2

# gemini 토큰 정보 입력
GOOGLE_GEMINI_API_KEY = "" # 여러분들의 토큰 정보를 넣어주세요!!!

keyword = '김범수+꿈일까'

# ------------------------------------------------------------------------------------------------ END #


def init_driver():
    if osName not in "Windows":
        try:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9231 --user-data-dir="~/Desktop/crawling/chromeTemp31"'],
                shell=True, stdout=subprocess.PIPE)  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9231 --user-data-dir="~/Desktop/crawling/chromeTemp31"'],
                shell=True, stdout=subprocess.PIPE)
    else:
        try:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9231 '
                             r'--user-data-dir="C:\chromeTemp31"')  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen(
                r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9231 '
                r'--user-data-dir="C:\chromeTemp31"')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9231")

    service = ChromeService(executable_path=ChromeDriverManager().install())
    # service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\120.0.6099.71\\chromedriver.exe')
    # service = ChromeService(
    #     '/Users/XXX/.wdm/drivers/chromedriver/mac64/120.0.6099.71/chromedriver-mac-x64/chromedriver')  # for MAC
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

    # print(answer)
    try:
        # result = markdown.markdown(answer['choices'][0]['content'][0])  # HTML 로 포스팅 할때
        # result = answer['choices'][0]['content'][0]  # markdown 형식으로 포스팅 할때
        result = markdown.markdown(answer['choices'][0]['content'][0])  # html 형식으로 포스팅 할때
        print(f'bard result = {result}')
        return result
    except Exception as e:
        print(f'{type(e).__name__}: {e}')
        print(f"너무 많은 바드 요청이 있거나 키워드에 이슈가 있습니다. ({BARD_REQUEST_DELAY_TIME})초간 대기 후 다른 키워드를 실행하겠습니다.")
        print(f"({keyword}) 키워드로 요청된 바드 결과는 빈 공란으로 넘겨주겠습니다.")
        sleep(BARD_REQUEST_DELAY_TIME)
        return ''
        # make_google_bard_data(driver, keyword)
        # print(f"너무 많은 바드 요청이 있거나 키워드에 이슈가 있습니다. ({BARD_REQUEST_DELAY_TIME})초간 대기 후 다시금 시도하겠습니다.")


def make_google_gemini_data(keyword):
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    print(f'\ngemini 질문 키워드는 ({keyword}) 입니다.')
    answer = model.generate_content(f"'{keyword}' 라는 가수 및 노래에 대해 자세히 설명해줘")

    try:
        # result = markdown.markdown(answer.text)  # HTML 로 포스팅 할때
        # result = answer.text  # markdown 형태로 포스팅 할때
        result = markdown.markdown(answer.text)  # html 형태로 포스팅 할때 
        print(result)
        return result
    except Exception as e:
        print('\n' + C_BOLD + C_RED + C_BGBLACK + '[정보를 가져오는데 실패하였습니다. ERROR를 확인해 주세요!!!]', C_END)
        # print('answer.prompt_feedback : ', answer.prompt_feedback)
        # print(f'{type(e).__name__}: {e}')
        if e is not None:
            return ''
        else:
            print(f"request에 문제가 있어 ({GEMINI_REQUEST_DELAY_TIME})초간 대기 후 다시금 시도하겠습니다.")
            sleep(GEMINI_REQUEST_DELAY_TIME)
            make_google_gemini_data(keyword)



# main start
def main():
    try:
        print("\nSTART...")
        start_time = time.time()
        now = datetime.now()
        print("START TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))
        
        if selected_AI_model == 1:
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 시작]', C_END)
            driver = init_driver()
            sleep(PAUSE_TIME)
            print('\n' + C_BOLD + C_YELLOW + C_BGBLACK + '[크롬 드라이버 초기화 완료]', C_END)
        
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


    finally:
        end_time = time.time()
        ctime = end_time - start_time
        time_list = str(timedelta(seconds=ctime)).split(".")
        print("\n실행시간 (시:분:초)", time_list)
        print("END...")
# main end

if __name__ == '__main__':
    main()
