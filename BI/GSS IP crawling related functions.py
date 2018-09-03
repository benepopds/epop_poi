#filtering by category
def filter0(df):
    df_rt = pd.DataFrame(columns=["Source", "URL", "Rank"])
    for index, row in df.iterrows():
        i = row.URL
        r = urlopen("http://" + i)
        soup = BeautifulSoup(r, 'html.parser')
        try:
            div_cate = soup.find("div", {"id":"breadcrumb"})
            div_cate1 = div_cate.find_all("span", {"class":"item"})
            if ('냉장고' in  div_cate1[2].find('a',{'class':'hoverline'}).text) | ('청소기' in  div_cate1[2].find('a',{'class':'hoverline'}).text):
                print(div_cate1[2].find('a',{'class':'hoverline'}).text)
                df_rt.loc[index] = [row.Source, i, row.Rank]
            elif ('냉장고' in  div_cate1[3].find('a',{'class':'hoverline'}).text) | ('청소기' in  div_cate1[3].find('a',{'class':'hoverline'}).text):
                print(div_cate1[3].find('a',{'class':'hoverline'}).text)
                df_rt.loc[index] = [row.Source, i, row.Rank]
            elif ('냉장고' in  div_cate1[4].find('a',{'class':'hoverline'}).text) | ('청소기' in  div_cate1[4].find('a',{'class':'hoverline'}).text):
                print(div_cate1[3].find('a',{'class':'hoverline'}).text)
                df_rt.loc[index] = [row.Source, i, row.Rank]
            else:
                print(i, "WRONG")
        except:
            print("ERROR: ", i, div_cate1[2].find('a',{'class':'hoverline'}).text)
        df_rt.reset_index(drop=True)
    return df_rt

df_ref = filter0(pd.concat([ref1, ref2, ref]).drop_duplicates("URL").reset_index(drop=True))
df_vac = filter0(pd.concat([vac1, vac2, vac]).drop_duplicates("URL").reset_index(drop=True))


#extract model name 
def MN_extractor(url):
    html = urlopen("http://" + url)
    soup =  BeautifulSoup(html, "html.parser")
    #이름/모델명 가져오기
    name = soup.findAll("div", {"class": "normalN_table_wrap"})[0].tbody.td.get_text()
    temp = name.split(" ")[-1]
                   
    #괄호 안에 것만
    if "(" in temp:
        temp = temp[temp.index("(") + 1:temp.rindex(")")]
                   
    #한글이 있으면 통째로 반환
    if bool(re.match('[a-zA-Z0-9]', temp)):
        #print(i, "\t", temp)
        return temp
    else:
        #print(i, "\t", name)
        return name
rel_ref = pd.DataFrame(columns=["Source", "URL", "Rank"])
for item_url in df_ref[df_ref.Source!='전체-인기순'].URL.values:
    #모델명 가져오기: parse는 한글처리
    MN = parse.quote(MN_extractor(item_url))
    url = 'http://www.gsshop.com/shop/search/main.gs?tq=%s&rq=&cls='%MN
    html = urlopen(url)
    soup =  BeautifulSoup(html, "html.parser")
    
    #검색해서 URL 가져오기
    for o, i in enumerate([i for i in soup.select('a[href^="/prd/prd"]')]):
        #print([ ('TV_'+item_url[32:40]), ('www.gsshop.com' + i.get('href').split("&")[0]), o])
        rel_ref = rel_ref.append({'Source':('TV_'+item_url[32:40]), 'URL':('www.gsshop.com' + i.get('href').split("&")[0]), 'Rank':o}, ignore_index=True)

rel_vac = pd.DataFrame(columns=["Source", "URL", "Rank"])
for item_url in df_vac[df_vac.Source!='전체-인기순'].URL.values:
    #모델명 가져오기: parse는 한글처리
    MN = parse.quote(MN_extractor(item_url))
    url = 'http://www.gsshop.com/shop/search/main.gs?tq=%s&rq=&cls='%MN
    html = urlopen(url)
    soup =  BeautifulSoup(html, "html.parser")
    
    #검색해서 URL 가져오기
    for o, i in enumerate([i for i in soup.select('a[href^="/prd/prd"]')]):
        #print([ ('TV_'+item_url[32:40]), ('www.gsshop.com' + i.get('href').split("&")[0]), o])
        rel_vac = rel_vac.append({'Source':('TV_'+item_url[32:40]), 'URL':('www.gsshop.com' + i.get('href').split("&")[0]), 'Rank':o}, ignore_index=True)
df_ref = pd.concat([df_ref[df_ref.Source!='전체-인기순'], rel_ref, df_ref[df_ref.Source=='전체-인기순']])
df_vac = pd.concat([df_vac[df_vac.Source!='전체-인기순'], rel_vac, df_vac[df_vac.Source=='전체-인기순']])


# filter by URL(The URLs exist in MWS_COLT_ITEM)
engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.50:3306/wspider_gfk2?charset=utf8mb4", encoding = 'utf8', pool_size=20,pool_recycle=3600,connect_args={'connect_timeout':1000000} )
df_ref = df_ref.assign(ITEM_NUM = df_ref.URL.str[32:40])
df_vac = df_vac.assign(ITEM_NUM = df_vac.URL.str[32:40])
ITEM_QUE1 = []
ITEM_QUE2 = []

query = """
select *
from MWS_COLT_ITEM
where ITEM_NUM = '%s'
"""

count = 0
for i in df_ref.ITEM_NUM.values:
    if len(pd.read_sql_query(query%i,engine)) != 0: 
        ITEM_QUE1.append(i)
for i in df_vac.ITEM_NUM.values:
    if len(pd.read_sql_query(query%i,engine)) != 0: 
        ITEM_QUE2.append(i)