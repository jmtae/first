##https://iskaz.tistory.com/21#--%--%EC%--%--%EC%A-%--%EB%--%-C%--%EB%-D%B-%EC%-D%B-%ED%--%B-%--%EC%--%--%EC%--%--%--%EC%A-%--%EC%-E%A-%ED%--%--%EA%B-%B-

# import requests
# from bs4 import BeautifulSoup

# URL = "https://www.ajou.ac.kr"
# res = requests.get(URL)
# html = res.text
# soup = BeautifulSoup(html, 'lxml')

# result = []
# for e in soup.select("a"):
#     text = e.text.strip() 
#     if text != '':
#         result.append(text)

# result = [e.text.strip() for e in soup.select("a") if e.text.strip() != '']
# print(result)

#[1. 라이브러리 모듈 불러오기]
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import datetime
from time import sleep
import math
import requests
import pandas as pd
# 경고 표시 무시하기.
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# [2. 정책 검색하기]
# 정책 중 키워드를 골라서 검색하기
print('='* 100)
Search_text = input('안녕하세요 한국 정책 브리핑중  어떤 관련 정책이 궁금하시나요?: ')

# [3. 셀리니움 불러오기] 
options = webdriver.ChromeOptions()
options.add_argument('start-maximized')


# Selenium 스크립트가 종료된 후에도 브라우저가 자동으로 닫히지 않도록 설정
chrome_options = Options()
chrome_options.add_experimental_option("detach",True)

# 크롬드라이버 설정
driver = webdriver.Chrome(options=chrome_options)

#대기 시간으로 WebDriver가 요소를 찾을 때까지 대기
driver.implicitly_wait(5)
# 타겟 url은 한국 정책 브리핑 사이트.
TARGET_URL = 'https://www.korea.kr/news/pressReleaseList.do'

# 드라이버로 url열기
driver.get(TARGET_URL)

# 키워드 열고 검색창 클릭
driver.find_element(By.ID, 'srchKeyword').click()
driver.find_element(By.ID, 'srchKeyword').send_keys(Search_text + Keys.ENTER)
sleep(0.5)

# 검색 날 지정하기. 1달이나 1년은 너무 많으니 최근 이슈로 지정 <2번째> 셀렉터가 안 찾아와져 XPATH로 가지고 오기.
driver.find_element(By.XPATH, '//*[@id="period"]/option[2]').click()        
sleep(1)
driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div/div[2]/div[1]/button/span').click() 

# 파싱하기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 검색 결과 총 수 가져오기.
Total_Article_n = int(soup.select_one('div.result > strong').text)	
print("브리핑 총 검색 결과 수는", Total_Article_n,"개 입니다.")
# 브리핑 페이지수가 20개 단위로 늘어나기에 20개를 나누어서 총 넘겨야 할 페이지 지정.
Pages_Article = math.ceil(int(Total_Article_n) / 20)	
Pagenum = 1

print('=' * 100)
    
print('<3초 크롤링 시작>')
sleep(3)


# [4. 크롤링 저장 변수 지정]
total_list = [ ]      # 전체 정책들 저장 변수
title1 = [ ]    #기사제목 저장
organiz1 = [ ]      #부속 기관들 (부처)) 저장
no = 1 # 정책들 넘기기

req = requests.get(TARGET_URL)
html_3 = req.text

# 크롤링 시작
for x in range(1, Pages_Article + 1) : # 총 페이지 
    
    i=1
    for i in range(1,21):
        if no > Total_Article_n: # 정책 수가 통합 수보다 크면 빠져나오기.
            break
        
        html_3 = driver.page_source 
        soup_3 = BeautifulSoup(html_3, 'lxml')    
        
        # 정책 제목 타이틀 가져오기
        content_3 = soup_3.select(f'div.list_type > ul > li:nth-child({i}) > a > span > strong')
        
        print("\n")
        print(f"--{no}번--")
        for title in content_3:
            print("기사 제목: ", title.get_text(strip = True))
            title1.append(title.get_text(strip=True))
        
        # 부처 가져오기
        
        content_4 = soup_3.select(f'div.list_type > ul > li:nth-child({i}) > a > span > span.source > span:nth-child(2)')
        for department in content_4:
            print("부처:", department.get_text(strip = True))
            organiz1.append(department.get_text(strip=True))
            
        for title, department in zip(content_3, content_4):
            total_list.append({
                "Title": title.get_text(strip=True),
                "Organization": department.get_text(strip=True)
            })
    
            
        no += 1
            
    if no > Total_Article_n:
        break
    
    x += 1 
    y = str(x)
    
    # 페이지 바꿈 함수
    driver.find_element(By.LINK_TEXT ,'%s' %y).click()
    print(f'1초 후에 {y}페이지 크롤링 시작합니다.')
    driver.implicitly_wait(5)
    sleep(1)

#[5. 크롤링 데이터 저장]
# 크롤링한 데이터를 데이터프레임으로 저장(제이슨으로 저장할거지만 프레임으로도 보기위하여)
df = pd.DataFrame({
    '기사제목': title1,
    '부처': organiz1,
})

#[6. json으로 저장]
with open("korea_briefing.jsonl", "w", encoding="UTF-8") as output_file:
    for article in total_list:
        print(json.dumps(article, ensure_ascii=False), file=output_file)

#######################################################


# # JSONL 파일로 저장
# with open("한국정책브리핑.jsonl", "w", encoding="UTF-8") as output_file:
#     for article in total:
#         json_line = json.dumps(article, ensure_ascii=False)
#         output_file.write(json_line + "\n")
