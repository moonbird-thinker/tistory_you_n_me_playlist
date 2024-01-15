# -*- coding: utf-8 -*-

import time
from datetime import timedelta
from datetime import datetime
import requests
from pprint import pprint as pp
from xml_to_dict import XMLtoDict
from json_flatten import flatten
from urllib import parse
import pandas as pd
import random
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
import os
from googlesearch import search

keyword = '김범수+꿈일까'

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

def get_youtube_info():
    url = f'https://www.youtube.com/results?search_query={keyword}+MV'
    headers = {
        'User-Agent' : random_user_agent,
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    # print(soup)
    
    data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
    data_json = json.loads(data)
    # pp(data_json)
    
    # ----------------------------------------------------------
    # 너무 복잡한 json 파일 분석법 tip 1 (flatten 함수를 이용하자)
    # ----------------------------------------------------------
    
    flat_json = flatten(data_json)
    # print(flat_json)
    
    # ----------------------------------------------------------
    # 너무 복잡한 json 파일 분석법 tip 2 (json 파일로 저장하는 방법)
    # ----------------------------------------------------------
    youtube_info_path = 'youtube_info.json'
    Path(youtube_info_path).touch(exist_ok=True)
    with open(youtube_info_path, 'w', encoding="UTF-8") as output_file:
        json.dump(data_json, output_file, ensure_ascii=False, indent=4, separators=(',', ': '))
    
    # ----------------------------------------------------------
    # 너무 복잡한 json 파일 분석법 tip 3 (json_normalize)
    # ----------------------------------------------------------
    df = pd.json_normalize(data_json)  # pandas dataframe
    csv_path = f'youtube_normalize_info.csv'
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, mode='w', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False)
    else:
        df.to_csv(csv_path, mode='a', sep=',', na_rep='NaN', encoding='utf-8-sig', index=False, header=False)


    youtube_mv_info_lists = []
    for i in range(3):
        temp_dic = {}
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


def get_google_search_info():
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
    


# main start
def main():
    try:
        print("\nSTART...")
        start_time = time.time()
        now = datetime.now()
        print("START TIME : ", now.strftime('%Y-%m-%d %H:%M:%S'))
        
        youtube_my_info_df = get_youtube_info()
        
        get_google_search_info()
        

    finally:
        end_time = time.time()
        ctime = end_time - start_time
        time_list = str(timedelta(seconds=ctime)).split(".")
        print("\n실행시간 (시:분:초)", time_list)
        print("END...")
# main end

if __name__ == '__main__':
    main()
