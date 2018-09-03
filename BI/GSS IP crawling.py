#gsshop 냉장고/청소기 관련 IP 크롤 코드

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import time
import re
from urllib import parse
from sqlalchemy import create_engine
import datetime
import math
import numpy as np
import telepot


#전체-인기순
html = urlopen('http://www.gsshop.com/shop/sect/sectM.gs?sectid=1379153&lsectid=1378798&msectid=1379153&lseq=358308&gsid=SECT-1378798-0-1')
soup =  BeautifulSoup(html, "html.parser")
ref = pd.DataFrame(columns=["Source", "URL", "Rank"])
for o, i in enumerate([i for i in soup.select('a[href^="/prd/prd"]')]):
    ref.loc[o] = ["전체-인기순", ('www.gsshop.com' + i.get('href').split("§")[0]), o]
html = urlopen('http://www.gsshop.com/shop/sect/sectM.gs?sectid=1378984&lsectid=1378796&msectid=1378984&lseq=358308&gsid=SECT-1378796-0-1')
soup =  BeautifulSoup(html, "html.parser")
vac = pd.DataFrame(columns=["Source", "URL", "Rank"])
for o, i in enumerate([i for i in soup.select('a[href^="/prd/prd"]')]):
    vac.loc[o] = ["전체-인기순", ('www.gsshop.com' + i.get('href').split("§")[0]), o]

#TV편성표
html = urlopen('http://www.gsshop.com/shop/tv/tvScheduleSearch.gs?lseq=410634&scheduleTq=%EB%83%89%EC%9E%A5%EA%B3%A0')
soup =  BeautifulSoup(html, "html.parser")
ref1 = pd.DataFrame(columns=["Source", "URL", "Rank"])
for o, i in enumerate ([i for i in soup.select('a[href^="/prd/prd"]') if not i.get('class')]):
    ref1.loc[o] = ["TV편성표", ('www.gsshop.com' + i.get('href').split("&")[0]), o]
html = urlopen('http://www.gsshop.com/shop/tv/tvScheduleSearch.gs?lseq=410634&scheduleTq=%EC%B2%AD%EC%86%8C%EA%B8%B0')
soup =  BeautifulSoup(html, "html.parser")
vac1 = pd.DataFrame(columns=["Source", "URL", "Rank"])
for o, i in enumerate ([i for i in soup.select('a[href^="/prd/prd"]') if not i.get('class')]):
    vac1.loc[o] = ["TV편성표", ('www.gsshop.com' + i.get('href').split("&")[0]), o]

#TV쇼핑
html = urlopen('http://www.gsshop.com/shop/sect/sectS.gs?sectid=1087134&eh=eyJjYXRlZ29yeSI6IjQyMTIyMF8xMDg3MDUzXzE0MzI4OTMiLCJzb3J0VHlwZSI6IkRFRkFVTFQifQ%3D%3D')
soup =  BeautifulSoup(html, "html.parser")
ref2 = pd.DataFrame(columns=["Source", "URL", "Rank"])
o = 0
for i in [i for i in soup.select('a[href^="/prd/prd"]') if not i.get('prd-item')]:
    if "냉장고" in i.get_text(): 
        o += 1
        ref2.loc[o] = ["TV쇼핑", ('www.gsshop.com' + i.get('href').split("§")[0]), o]
html = urlopen('http://www.gsshop.com/shop/sect/sectS.gs?sectid=1087134&eh=eyJjYXRlZ29yeSI6IjQyMTIyMF8xMDg3MDUzXzEwODcxMzQiLCJzb3J0VHlwZSI6IkRFRkFVTFQifQ%3D%3D')
soup =  BeautifulSoup(html, "html.parser")
vac2 = pd.DataFrame(columns=["Source", "URL", "Rank"])
o = 0
for i in [i for i in soup.select('a[href^="/prd/prd"]') if not i.get('prd-item')]:
    if "청소기" in i.get_text():
        o += 1
        vac2.loc[o] = ["TV쇼핑", ('www.gsshop.com' + i.get('href').split("§")[0]), o]

#오늘추천
html = urlopen('http://www.gsshop.com/flexShop.gs?sectid=743&lseq=409881-1&gsid=gnb-AU409881-AU409881-1')
soup =  BeautifulSoup(html, "html.parser")
vac_TR=[]
ref_TR=[]
for i in [i for i in soup.select('a[href^="/deal/deal"]')]:
    if "냉장고" in i.get_text(): ref_TR.append('www.gsshop.com' + i.get('href').split("§")[0])
    if "청소기" in i.get_text(): vac_TR.append('www.gsshop.com' + i.get('href').split("§")[0])    

driver = webdriver.Chrome('/home/aron/epop_poi/ForCrawling/chromedriver')
driver.implicitly_wait(3)
driver.get('http://www.gsshop.com/flexShop.gs?sectid=743&lseq=409881-1&gsid=gnb-AU409881-AU409881-1')
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.close()
mybuttons = soup.findAll('dt')
tar = ['product-title', 'base-line']
TD_text = []
for but in mybuttons:
    if len(but.attrs)==0 : continue
    if but['class'] == ['product-title', 'base-line']: 
        TD_text.append(but.get_text())
mybuttons = soup.findAll('button')
TD_link = []
for but in mybuttons:
    if but['class'][0] == 'user-comment': TD_link.append(but.get('onclick').split("'")[1])
for i in range(40):
    if '냉장고' in TD_link[i]: ref_TR.append(TD_link[i])
    if '청소기' in TD_link[i]: vac_TR.append(TD_link[i])

## 오늘추천-배너
html = urlopen('http://www.gsshop.com/planPrd/planPrd.jsp?planseq=140537&svcid=gc&lseq=391142-2&dseq=37307578&gsid=gnb-AU391142-AU391142-2')
soup =  BeautifulSoup(html, "html.parser")
vac_BN=[]
ref_BN=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]')]:
    if "청소기" in i.get_text(): vac_BN.append('www.gsshop.com' + i.get('href').split("&")[0])
    if ("냉장고" in i.get_text())|("냉동고" in i.get_text()): ref_BN.append('www.gsshop.com' + i.get('href').split("&")[0])  

## X브랜드

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000041&tq=1156%2C1169%2C8224%2C58939%2C58941%2C118252&suppCode=1028495&eh=eyJjYXRlZ29yeSI6IjEzNzg3OThfMTM3OTE1MyJ9')
soup =  BeautifulSoup(html, "html.parser")
ref_LG=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    ref_LG.append('www.gsshop.com' + i.get('href').split("§")[0])
html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000041&tq=1156%2C1169%2C8224%2C58939%2C58941%2C118252&suppCode=1028495&eh=eyJjYXRlZ29yeSI6IjEzNzg3OThfMTM3OTE1MyJ9')
soup =  BeautifulSoup(html, "html.parser")
ref_LG=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    ref_LG.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000041&tq=1156%2C1169%2C8224%2C58939%2C58941%2C118252&suppCode=1028495&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_LG=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_LG.append('www.gsshop.com' + i.get('href').split("§")[0])
​
html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000041&tq=1156%2C1169%2C8224%2C58939%2C58941%2C118252&suppCode=1028495&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_LG=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_LG.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000747&tq=19005&suppCode=709860&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTgifQ%3D%3D')
soup =  BeautifulSoup(html, "html.parser")
ref_SK=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    if "세탁기" in i.get_text(): ref_SK.append('www.gsshop.com' + i.get('href').split("§")[0])
html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000747&tq=19005&suppCode=709860&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTgifQ%3D%3D')
soup =  BeautifulSoup(html, "html.parser")
ref_SK=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    if "세탁기" in i.get_text(): ref_SK.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000747&tq=19005&suppCode=709860&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_SK=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_SK.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000546&tq=19027&suppCode=123473&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_DS=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_DS.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000767&tq=1054&suppCode=1002935&eh=eyJjYXRlZ29yeSI6IjEzNzg3OThfMTM3OTE1MyJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_SS=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_SS.append('www.gsshop.com' + i.get('href').split("§")[0])
html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000767&tq=1054&suppCode=1002935&eh=eyJjYXRlZ29yeSI6IjEzNzg3OThfMTM3OTE1MyJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_SS=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_SS.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000767&tq=1054&suppCode=1002935&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
ref_SS=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    ref_SS.append('www.gsshop.com' + i.get('href').split("§")[0])

html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000040&tq=24243&suppCode=1015563,1021979&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_TF=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_TF.append('www.gsshop.com' + i.get('href').split("§")[0])
html = urlopen('http://www.gsshop.com/shop/jbp/main.gs?jbpBrandCd=1000000040&tq=24243&suppCode=1015563,1021979&eh=eyJjYXRlZ29yeSI6IjEzNzg3OTZfMTM3ODk4NCJ9')
soup =  BeautifulSoup(html, "html.parser")
vac_TF=[]
for i in [i for i in soup.select('a[href^="/prd/prd"]') if i.get("onclick")]:
    vac_TF.append('www.gsshop.com' + i.get('href').split("§")[0])


## 오늘오픈
driver = webdriver.Chrome('/home/aron/epop_poi/ForCrawling/chromedriver')
driver.implicitly_wait(3)
driver.get('http://www.gsshop.com/shop/deal/newArrival.gs?lseq=408940-1&gsid=gnb-AU408940-AU408940-1#group_109_P_1')
soup = BeautifulSoup(driver.page_source, 'html.parser')

vac_TD=[]
ref_TD=[]
for i in [i for i in soup.select('a[href^="/deal/deal"]') ]:
    if "냉장고" in i.get_text(): ref_TD.append('www.gsshop.com' + i.get('href'))
    if "세탁기" in i.get_text(): vac_TD.append('www.gsshop.com' + i.get('href'))
driver.close()

## 지금BEST
vac_TD=[]
ref_TD=[]

driver = webdriver.Chrome('/home/aron/epop_poi/ForCrawling/chromedriver')
driver.implicitly_wait(3)
driver.get('http://www.gsshop.com/shop/spa/nowBest.gs?lseq=415303-1&gsid=gnb-AU415303-AU415303-1')

ref_NB = []
vac_NB = []

#냉장고
driver.execute_script("setRcmdAreaView('main-r30', '1378798', 60)") #냉장고, etc
time.sleep(2)
soup = BeautifulSoup(driver.page_source, 'html.parser')
time.sleep(2)
for i in [i for i in soup.select('a[href^="/prd/prd"]') ]:
    if "냉장고" in i.get_text(): ref_NB.append('www.gsshop.com' + i.get('href').split("&")[0])
        
#청소기
driver.execute_script("setRcmdAreaView('main-r30', '1378796', 60)") #청소기, etc
time.sleep(2)
soup = BeautifulSoup(driver.page_source, 'html.parser')
time.sleep(2)
for i in [i for i in soup.select('a[href^="/prd/prd"]') ]:
    if "청소기" in i.get_text(): vac_NB.append('www.gsshop.com' + i.get('href').split("&")[0])

driver.close()