import pandas as pd
from sqlalchemy import create_engine
from jaroWinkler import get_jaro_distance

engine = create_engine("mysql+pymysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4",
                       encoding='utf8', pool_size=20, pool_recycle=3600, connect_args={'connect_timeout': 1000000})

query = '''
select *
from TEMP0001
where RAND()<0.0001
limit 300'''

df = pd.read_sql_query(query, engine)
df.to_pickle('rand300.df')
df = pd.read_pickle('rand300.df')
for index, record in df.iterrows():
    chk = False
    co_addr = record.ADDR
    co_name = record.CO_NAME_R
    split_addr = co_addr.split()

    if len(split_addr) < 4: continue    # 비정상 주소인 경우 건너뛴다.

    addr1 = split_addr[0]
    addr2 = split_addr[1]
    addr3 = split_addr[2]
    remain_addr = ' '.join(split_addr[3:])  # 동 이하의 상세주소

    query2 = '''
    select *
    from REF_OPEN_DATA
    where 주소3 = "{}" and 주소2 = "{}" and 주소1 = "{}"'''.format(addr3, addr2, addr1)   # 같은 시, 구, 동을 가진 지자체 데이터들을 가져온다.

    print(co_name, co_addr, record.REP_PHONE_NUM)   # 현재 매치 시도 자주와 레코드
    df2 = pd.read_sql_query(query2, engine)
    if len(df2) == 0: continue

    max_rate = 0    # 비교하면서 max rate를 update하는 구조
    max_record = pd.DataFrame()
    cnt = 0
    chk = False
    for idx, comp in df2.iterrows():
        if comp.사업장명_R == '' or len(comp.소재지전체주소_R.split()) < 4: continue   # 사업장 명이 비어있거나 자주와 데이터처럼 비정상 주소인 경우 건너뛴다.
        name_rate = get_jaro_distance(co_name, comp.사업장명_R)     # 사업장명, 주소 유사도를 구한 뒤 그 둘을 곱한다.
        remain_addr_comp = ' '.join(comp.소재지전체주소_R.split()[3:])     # 주소 유사도의 경우 시, 구, 동을 제외한 나머지 주소로만 비교를 한다.
        addr_rate = get_jaro_distance(remain_addr, remain_addr_comp)

        # 최대 매칭 레코드 업데이트
        if max_rate < name_rate * addr_rate:
            max_rate = name_rate * addr_rate
            max_record = comp

    if max_rate < 0.7:  # 매치율이 0.7 이하인 경우 매치실패
        print('매치 실패...')

    else:
        print(max_record.사업장명_R, max_record.소재지전체주소_R, max_record.전화번호, str(max_rate) + "\n")

    print()