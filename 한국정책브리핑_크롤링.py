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

#Part 1. 모듈 가져오기
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import math
from time import sleep
import warnings
import requests
# 데이터 저장을 위한 json parsing
import json
warnings.simplefilter(action='ignore', category=FutureWarning)


#Part 2. 키워드 수집 설정
Keyword = input('1. 수집 검색어는 무엇입니까?: ')
ft_name = "articles"
# fx_name = input('3. 결과를 저장할 xlsx형식의 파일명을 쓰세요(예: 파일명.xlsx): ')       
# [c:\\py_temp\\파일명.xlsx] 절대경로 지정방법


#Part 3. 셀레니움 & BS4 크롬 제어
options = webdriver.ChromeOptions()
options.add_argument('start-maximized')
##driver = webdriver.Chrome('/Users/kaz/Desktop/Project/chromedriver', options=options)

# 브라우저 자동 꺼짐 방지 옵션
chrome_options = Options()
chrome_options.add_experimental_option("detach",True)
# 크롬드라이버 생성
driver = webdriver.Chrome(options=chrome_options)
# 페이지 로딩이 완료될 때까지 기다리는 코드
driver.implicitly_wait(5)
TARGET_URL = 'https://www.korea.kr/news/pressReleaseList.do'
driver.get(TARGET_URL)

driver.find_element(By.ID, 'srchKeyword').click()
driver.find_element(By.ID, 'srchKeyword').send_keys(Keyword + Keys.ENTER)
sleep(1)

driver.find_element(By.XPATH, '//*[@id="period"]/option[2]').click()        #최근 1주 검색 <2번쨰.>
sleep(1)
driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div/div[2]/div[1]/button/span').click() 

# driver.find_element(By.XPATH, '//*[@id="container"]/div/article/div[1]/div[2]/div[1]/button/span').click() 원래 있던 코드


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

Result_Articles = int(soup.select_one('div.result > strong').text)	#검색 결과 총 000건 
print("총 검색 결과 수는", Result_Articles)
ArticlePages = math.ceil(int(Result_Articles) / 20)	# 브리핑룸은 20개 단위로 늘어남 그래서 20개를 나누어서 페이지를 넘기는 거임.
PageNum = 1

print('=' *80)
    
print('3초 후에 시작합니다.')
sleep(3)

'''
#Part 4. 각 항목별 데이터를 수집하여 리스트에 저장
sn2 = [ ]       #연번 저장
date2 = [ ]     #날짜 저장
'''
total = [ ]      #링크 저장
title1 = [ ]    #기사제목 저장
ogz1 = [ ]      #부처 저장
no = 1

req = requests.get(TARGET_URL)
html_3 = req.text


for a in range(1, ArticlePages + 1) :
    
    i=1
    for i in range(1,21):
        if no > Result_Articles:
            break
        
        html_3 = driver.page_source 
        soup_3 = BeautifulSoup(html_3, 'lxml')    
        
        # 정책 제목 타이틀 가져오기
        content_3 = soup_3.select(f'div.list_type > ul > li:nth-child({i}) > a > span > strong')
        # #container > div > div > div > div.list_type > ul > li:nth-child(1) > a > span > strong
        print("\n")
        print(f"--{no}번--")
        for title in content_3:
            print("기사 제목: ", title.get_text(strip = True))
            title1.append(title.get_text(strip=True))
        
        # 부처 가져오기
        # 셀럭터 container > div > div > div > div.list_type > ul > li:nth-child(1) > a > span > span.source > span:nth-child(2)
        content_4 = soup_3.select(f'div.list_type > ul > li:nth-child({i}) > a > span > span.source > span:nth-child(2)')
        for department in content_4:
            print("부처:", department.get_text(strip = True))
            ogz1.append(department.get_text(strip=True))
            
        no += 1
        
        for titles, ogzs in zip(title,department):
            total.append({
                "Title": titles,
                "Organization":ogzs
            })
            
            
                
    if no > Result_Articles:
        break
    a += 1 
    b = str(a)
    
    # 페이지 바꿈 함수
    driver.find_element(By.LINK_TEXT ,'%s' %b).click()
    print(f'1초 후에 {b}페이지 크롤링 시작합니다.')
    driver.implicitly_wait(5)
    sleep(1)

# 크롤링한 데이터를 데이터프레임으로 저장
df = pd.DataFrame({
    '기사제목': title1,
    '부처': ogz1,
})

with open("한국정책브리핑.jsonl", "w", encoding="UTF-8") as output_file:
    for articles in total:
        print(json.dumps(articles, ensure_ascii=False), file=output_file)

#######################################################


