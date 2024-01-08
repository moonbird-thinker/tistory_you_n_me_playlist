# -*- coding: utf-8 -*-

import time
from datetime import timedelta
from datetime import datetime
import requests
from pprint import pprint as pp
from xml_to_dict import XMLtoDict
from json_flatten import flatten  # 유튜브 검색 결과보기 JSON
from urllib import parse
import pandas as pd
import random

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

def get_vibe_info(keyword):
    
    url = f'https://apis.naver.com/vibeWeb/musicapiweb/v4/searchall?query={keyword}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'referer': 'https://vibe.naver.com/search?query=%EA%B9%80%EB%B2%94%EC%88%98%20%EA%BF%88%EC%9D%BC%EA%B9%8C'
    }
    
    response = requests.get(url, headers=headers)
    # pp(response.text)
    
    # ------------------------------------------------
    # xml 파싱
    # 1. ElementTree 객체생성 후 사용 X
    # 2. xml_to_dict 패키지를 이용한 방법 O >> XML을 dictionary 형태로 변환
    # ...
    # ------------------------------------------------
    
    xd = XMLtoDict()
    
    # 앨범에 대한 정보
    album_info_lists = []
    searchall_info_response = response.content
    print('')
    albumTotalCount = int(xd.parse(searchall_info_response)['response']['result']['albumResult']['albumTotalCount'])
    for i in range(albumTotalCount):
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
    for i in range(trackTotalCount):
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
        
        vibe_album_df, vibe_track_df = get_vibe_info(keyword)


    finally:
        end_time = time.time()
        ctime = end_time - start_time
        time_list = str(timedelta(seconds=ctime)).split(".")
        print("\n실행시간 (시:분:초)", time_list)
        print("END...")
# main end

if __name__ == '__main__':
    main()
