from pykospacing import spacing
from bs4 import BeautifulSoup
import pandas as pd
import requests
from sqlalchemy import create_engine
import datetime as dt
import re
from Parsing import *
from conduct_address import ConductADDR

p = re.compile("\(.*?\)")
x = re.compile('%')
w = re.compile('''[-=.'"#/:$\\\]''')
CA = ConductADDR()


def get_add_columns(record):  # 사업장명_R, 소재지전체주소_R, 주소1, 주소2, 주소3 column 추가
    co_name = record[1]
    co_addr = record[2]
    co_road_addr = record[3]

    co_name_r = re.sub(x, '%%', co_name)
    co_name_r = re.sub(w, '', co_name_r)
    name_list = co_name_r.split()

    for j in range(len(name_list)):
        rt = re.sub(p, " ", name_list[j])
        name_list[j] = rt

    co_name_r = ' '.join(name_list).strip()

    addr1 = ''
    addr2 = ''
    addr3 = ''

    if co_addr == '':
        co_addr = CA.get_old_addr(co_road_addr)
        record[2] = co_addr

    split_addr = co_addr.split()

    if len(split_addr) >= 3:
        addr3 = split_addr[2]

    if len(split_addr) >= 2:
        addr2 = split_addr[1]

    if len(split_addr) >= 1:
        addr1 = split_addr[0]

    co_addr_r = co_addr
    if '  ' in co_addr:
        co_addr_r = spacing(co_addr)

    if len(co_addr_r.split()) > 1:
        try:
            co_addr_r = AddrNormalization(co_addr_r.split())
        except:
            pass

    return [co_name_r, co_addr_r, addr1, addr2, addr3]


def update_open_data():
    engine = create_engine("mysql+pymysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4",
                           encoding='utf8', pool_size=20, pool_recycle=3600, connect_args={'connect_timeout': 1000000})

    # API key 들의 목록을 넣어둔 csv file 로드
    API_list = pd.read_csv('API_list.csv', sep='@')

    # 검색 기간 설정
    end_date = dt.datetime.now()
    bgn_date = end_date-dt.timedelta(days=14)

    next_index_query = '''
    select max(번호) IT
    from REF_OPEN_DATA
    '''
    index_df = pd.read_sql_query(next_index_query, engine)
    next_iterator = int(index_df[index_df.index == 0].IT)+1  # 현재 DB 최대 index 부터 다음 번호로 index 를 매기기 위한 변수

    for cate_num, api in API_list.iterrows():
        # cate_num : 카테고리 넘버
        # api : 각 카테고리의 api 정보
        # url : bgn_date 에서 end_date 사이의 변동사항이 생긴 상점들의 페이지를 사이즈 4000개로 보여준다.

        if cate_num < 37: continue
        if cate_num in (93, 241): continue        # 확인 결과 사업장명 없는 경우가 많은 카테고리로 생략이 필요
        url = api['URL']+'&pageSize=4000&bgnYmd={}&endYmd={}'.format(bgn_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

        code = chr(cate_num // 26 + ord('A')) + chr(cate_num % 26 + ord('A'))   # 카테고리 기호화 (ex : 01 -> AB)

        columns = []  # 카테고리마다 테이블의 column 의 종류가 다르기 때문에 매번 새로 가져온다.
        check = False
        for page in range(1, 11111111):
            update_record_list = []     # 기간 내의 변동이 생긴 레코드들의 리스트

            for _ in range(10):     # 종종 발생하는 internal sever error 로 인한 중지를 방지하기 위해 반복 실행

                # 지자체 웹 사이트에서 테이블 크롤링
                try:
                    res = requests.get(url+'&pageIndex={}'.format(page))

                    html = res.text
                    soup = BeautifulSoup(html, 'xml')
                    columns = []
                    check = False

                    for ele in soup.find('columns'):
                        try:
                            columns.append(ele.text)
                            if columns[-1] == '인허가번호':
                                check = True

                        except AttributeError:
                            continue

                except:
                    continue

                break

            columns.append('카테고리')      # 카테고리 column 추가

            if not check:
                columns.append('인허가번호')     # 인허가번호가 없는 테이블의 경우 추가

            columns += ['사업장명_R', '소재지전체주소_R', '주소1', '주소2', '주소3']

            rows = soup.find('rows').find_all('row')
            if len(rows) == 0:      # 더 이상 데이터가 없는 경우 row 가 0개이므로 반복 정지
                break

            for row in rows:

                # xml 파일을 레코드로 변환하는 과정
                record = []
                for ele in row:
                    try:
                        record.append(ele.text.strip())

                    except AttributeError:
                        continue

                record.append(code)

                if not check:
                    record.append('')

                record += get_add_columns(record)

                if len(columns) != len(record): continue    # 비정상 데이터 (거의 나타나지 않는다.)

                update_record_list.append(record)

            # 공통 column 만 선별
            update_table = pd.DataFrame.from_records(update_record_list, columns=columns)[['번호', '사업장명', '사업장명_R',
                                                                                           '소재지전체주소', '주소1', '주소2', '주소3',
                                                                                           '소재지전체주소_R', '도로명전체주소',
                                                                                           '인허가일자', '영업상태명', '폐업일자',
                                                                                           '휴업시작일자', '휴업종료일자',
                                                                                           '재개업일자', '소재지우편번호', '전화번호',
                                                                                           '위치정보(X)', '위치정보(Y)', '인허가번호',
                                                                                           '상세영업상태명', '카테고리']]

            for index, record in update_table.iterrows():
                try:
                    query = 'select 번호 from REF_OPEN_DATA where 인허가번호 = "{}" and 사업장명 = "{}" and 소재지전체주소 = "{}" and 카테고리 = "{}"'\
                        .format(record.인허가번호, record.사업장명, record.소재지전체주소, code)  # 유니크한 레코드를 가져오는 쿼리

                    id_list = pd.read_sql_query(query, engine)
                except: continue

                if len(id_list) > 1:  # 데이터 중복 의심
                    print(2, record)

                elif len(id_list) == 0:   # 신규 데이터 추가
                    record['번호'] = next_iterator
                    new_record = pd.DataFrame([record]).set_index('번호')

                    new_record.to_sql('REF_OPEN_DATA', con=engine, if_exists='append')
                    next_iterator += 1
                    print('append record no %d...' % next_iterator)

                elif len(id_list) == 1:   # 기존 데이터 업데이트
                    record_id = int(id_list[id_list.index == 0].번호)
                    update_query = 'update REF_OPEN_DATA set 영업상태명 = "{}", 폐업일자 = "{}", 휴업시작일자 = "{}", 휴업종료일자 = "{}", ' \
                                   '재개업일자 = "{}", 인허가번호 = "{}", 상세영업상태명 = "{}" where 번호 = {}'\
                        .format(record.영업상태명, record.폐업일자, record.휴업시작일자, record.휴업종료일자, record.재개업일자,
                                record.인허가번호, record.상세영업상태명, record_id)

                    with engine.begin() as conn:
                        conn.execute(update_query)

                    print('update record no %d...' % record_id)

            print('category {} page{} clear...'.format(cate_num, page))

        print('category %d done...' % cate_num)


if __name__ == '__main__':
    update_open_data()
