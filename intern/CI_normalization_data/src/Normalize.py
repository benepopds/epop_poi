import pandas as pd
from addr_list import addr_list, sub_addr_list
from pykospacing import spacing
from selenium import webdriver
from sqlalchemy import create_engine
from selenium.webdriver.common.alert import Alert


def AddrNormalization(addr):
    chk = False
    if addr[0] == '대한민국':   #앞에 대한민국이 붙어있는 경우 지운다.
        addr = addr[1:]
        print(addr)

    for city in addr_list.keys():
        if addr[0] in addr_list[city]:  #주소 첫번째 단어가 정규화 주소 목록 안에 있는 경우 정규화를 시킨다.
            addr[0] = city
            chk = True
            break

    if chk is False:
        for city in sub_addr_list.keys():   #충청도, 경상도 등 남, 북으로 나뉘어있는 지역의 경우 파악을 한다.
            if addr[1] in addr_list[city]:
                addr[0] = city
                chk=True
                break

    if chk is False:    #변환을 하지 못했으면 주소에 오탈자를 의심한다.
        assert(0)

    return ' '.join(addr)


def PhoneNumNormalization(phone_num):
    return ''.join([s for s in phone_num.split() if s.isdigit()])


def CrawlingAddr(lat, lon):
    if lat <30 or lon <100:     #좌표의 유효성 체크
        assert(0)

    driver.find_element_by_name('query').send_keys('{} {}'.format(lat, lon))

    for i in range(5):  #웹 사이트에 좌표를 넣고 주소를 받아오는 과정
        try:
            driver.implicitly_wait(1)
            driver.find_element_by_id('submit').click()
        except:
            Alert(driver).accept()
            driver.find_element_by_name('query').clear()
            assert(0)

        cc = driver.find_elements_by_class_name('close')
        if len(cc) >= 2:
            break

    driver.find_element_by_name('query').clear()
    res = cc[1].text.split()[1:]

    res = ' '.join(res)
    print(res)
    return res

if __name__ == '__main__':
    engine = create_engine("mysql+pymysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' ,
                       pool_size=20,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    crawling_url = 'http://mygeoposition.com/'
    driver = webdriver.Chrome('C:\\Users\\1906182\\Downloads\\chromedriver')    #크롬 드라이버 설치 필요
    driver.get(crawling_url)
    driver.implicitly_wait(5)
    Alert(driver).accept()  #알람 수락

    for i in range(87):
        print(i)
        query = '''
        select a.ID, CO_NAME_R, ADDR, LATITUDE, LONGITUDE, REP_PHONE_NUM, MSISDN
        from MEUMS_COMPANY a left join MEUMS_COM_ADD_PHONE_NUM b on a.ID = b.CO_ID and a.REP_PHONE_NUM != b.MSISDN
        where a.ID > {} and a.ID <= {}'''.format(i*100000, (i+1)*100000)

        my_company_list=pd.read_sql_query(query, engine)

        columns = [str(my_company_list.columns)]
        result=[]
        print(len(my_company_list))
        if len(my_company_list)==0: continue

        for index, record in my_company_list.iterrows():

            try:
                record['REP_PHONE_NUM'] = PhoneNumNormalization(record['REP_PHONE_NUM'])    #공백이나 기타 불필요한 기호 제거
                if record['MSISDN'] is not None:
                    record['MSISDN'] = PhoneNumNormalization(record['MSISDN'])

                split_addr = record['ADDR'].split()
                if len(split_addr)<4:       #띄어쓰기 기준으로 split했을 때 4개보다 적게 분리되는 경우 정규화 전에 띄어쓰기를 시도한다.
                    split_addr = spacing(record['ADDR']).split()
                    if len(split_addr)<4:   #띄어쓰기를 시행한 뒤에서 4개보다 적게 분리되는 경우 크롤링을 해서 대체한다.
                        print(record['ADDR'])
                        split_addr = CrawlingAddr(record['LATITUDE'], record['LONGITUDE']).split()

                record['ADDR'] = AddrNormalization(split_addr)  #주소정규화
                record['STATE'] = 1
            except: #주소에 오탈자가 의심되는 경우
                print(record)
                record['STATE'] = 0

            result.append(record)

        df = pd.DataFrame.from_records(result).set_index('ID')
        # df.to_sql('TEMP0001', con=engine, if_exists='append')