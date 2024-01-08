from time import sleep
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import platform
import subprocess
import pyperclip
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

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

osName = platform.system()  # window 인지 mac 인지 알아내기 위한

LOADING_WAIT_TIME = 5
PAUSE_TIME = 3

tistory_blog_name = 'https://pemtinfo1.tistory.com'

tistory_category_name = '분양정보'

def init_driver():
    if osName not in "Windows":
        try:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224 --user-data-dir="~/Desktop/crawling/chromeTemp24"'],
                shell=True, stdout=subprocess.PIPE)  # 디버거 모드(로그인 정보 기타 정보 저장)
        except FileNotFoundError:
            subprocess.Popen([
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9224 --user-data-dir="~/Desktop/crawling/chromeTemp24"'],
                shell=True, stdout=subprocess.PIPE)
    else:
        try:
            subprocess.Popen(r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9224 '
                             r'--user-data-dir="C:\chromeTemp24"')  # 디버거 크롬 구동
        except FileNotFoundError:
            subprocess.Popen(
                r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9224 '
                r'--user-data-dir="C:\chromeTemp24"')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9224")
    
    service = ChromeService('C:\\Users\\ree31\\.wdm\\drivers\\chromedriver\\win64\\120.0.6099.71\\chromedriver.exe')
    # service = ChromeService(executable_path=ChromeDriverManager().install())
    
    _driver = webdriver.Chrome(service=service, options=options)
    _driver.implicitly_wait(LOADING_WAIT_TIME)
    return _driver


def tistory_login(_driver):
    
    try:
        _driver.get('https://www.tistory.com/auth/login')
        _driver.implicitly_wait(LOADING_WAIT_TIME)
        _driver.find_element(By.CLASS_NAME, 'link_kakao_id').click()

        print(f'\n{C_BOLD}{C_RED}{C_BGBLACK}주의: 3분안에 로그인을 완료해주세요!!!(tistory main ID 로 로그인해야함){C_END}')
        WebDriverWait(_driver, 180).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'link_profile')
            )
        )
    except:
        print('이미 로그인 되어있습니다.')
    

def tistory_write(_driver, keyword):
    title = '임시로 정한 title 입니다. 나중에 변경해주세요!!'
    body_html = f'{keyword}'
    
    _driver.get(f'{tistory_blog_name}/manage/post')
    sleep(LOADING_WAIT_TIME)
    
    # 이미작성하고 있는 글이 있었을때 나오는 alert 팝업 처리
    try:
        obj = _driver.switch_to.alert
        msg = obj.text
        print(f'\nalert message = {msg}')
        print('alert dismiss')
        obj.dismiss()
        sleep(PAUSE_TIME)
    except:
        pass
        print('no alert')
        
    
    # html 모드로 변환
    _driver.find_element(By.ID, 'editor-mode-layer-btn-open').click()
    sleep(PAUSE_TIME)
    _driver.find_element(By.ID, 'editor-mode-html').click()
    sleep(PAUSE_TIME)
    _driver.switch_to.alert.accept()  # html 모드 변환시 alert 처리
    sleep(PAUSE_TIME)
    
    # 카테고리 선택
    _driver.find_element(By.ID, 'category-btn').click()
    sleep(PAUSE_TIME)
    # _driver.find_element(By.ID, 'category-item-1089536').click()
    _driver.find_element(By.XPATH, f"//span[normalize-space()='{tistory_category_name}']").click()
    sleep(PAUSE_TIME)
    
    # 제목 입력
    _driver.find_element(By.ID, 'post-title-inp').click()
    pyperclip.copy(title)
    ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    
    # 글쓰기
    _driver.find_element(By.CLASS_NAME, 'CodeMirror-lines').click()
    pyperclip.copy(body_html)
    ActionChains(_driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    
    # 임시저장버튼 누르기
    _driver.find_element(By.CLASS_NAME, 'btn-draft').click()
    print('\n티스토리 글이 임시 저장되었습니다. 최종 발행은 따로 진행 부탁드려요')
    sleep(PAUSE_TIME)
    

def main():
    try:
        print("\nSTART...")
        
        keyword = '김범수 꿈일까'
        
        # chrome driver init
        driver = init_driver()
        
        # tistory login
        tistory_login(driver)
        
        # tistory write
        tistory_write(driver, keyword)
        
        
    finally:
        print("\nEND!!!")


if __name__ == '__main__':
    main()