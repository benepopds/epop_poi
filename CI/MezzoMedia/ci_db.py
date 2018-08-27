import numpy as np
import pandas as pd
import pymysql
import webbrowser
import random
import pickle
import os
from matplotlib import font_manager, rc
import pylab as plot
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from pandas import ExcelWriter
import winsound
import math
import locale

# korean font for plot
font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
rc('font', family=font_name)
locale.setlocale(locale.LC_ALL, '')

def excelExport(df, file_name, tab_name):

    if not os.path.exists('./export/'):
        os.makedirs('./export/')

    writer = ExcelWriter('./export/'+ file_name + '_' + datetime.now().strftime('%Y-%m-%d(%H_%M_%S)')+'.xlsx')
    df.to_excel(writer, tab_name)
    writer.save()

def beep():
    dt=datetime.now()
    winsound.Beep(2500, 1000)
    return dt

def get_test() :
    conn = pymysql.connect(host='133.186.143.65', user='wspider', password='wspider00!q', db='wspider', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    queryString = "select * from MWS_COLT_ITEM where ITEM_NUM='26824625';"
    curs.execute(queryString)

    p = pd.DataFrame( curs.fetchall() )
    conn.close()

    return p

def get_ci_company(coname, guname):
    conn = pymysql.connect(host='133.186.143.151', port=13306, user='eums', password='eums00!q', db='eums-shared', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    queryString = "select * from MEUMS_COMPANY where CO_NAME_R regexp '"+coname+"' and ADDR regexp '"+guname+"';"
    curs.execute(queryString)

    p = pd.DataFrame( curs.fetchall() )
    conn.close()

    return p

def get_ci_company_by_coname(coname):
    conn = pymysql.connect(host='133.186.143.151', port=13306, user='eums', password='eums00!q', db='eums-shared', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    coname = coname.replace(' ', '')

    queryString = "select * from MEUMS_COMPANY where CO_NAME_R regexp '"+coname+"';"
    #print(queryString)
    curs.execute(queryString)

    p = pd.DataFrame( curs.fetchall() )
    conn.close()

    return p

def get_ci_revisit(company_id_list):
    # JAJUWA
    def get_ci_revisit_jjw(company_id_list):
        conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        company_id_list = [str(x) for x in company_id_list]
        company_id_list = pd.DataFrame(company_id_list)

        data = [tuple( x ) for x in company_id_list.values]

        curs.execute("CREATE temporary TABLE temp_tbl ( COMPANY_ID bigint );")
        sql = "INSERT INTO temp_tbl(COMPANY_ID) values (%s);"
        curs.executemany(sql, data)
        conn.commit()

        queryString = "select * from MEUMS_COMP_REVISIT_HIS A join temp_tbl B on A.COMPANY_ID=B.COMPANY_ID;"
        curs.execute(queryString)
        p = pd.DataFrame( curs.fetchall() )

        conn.close()
        return p

    # CJ
    def get_ci_revisit_cj(company_id_list):
        conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        company_id_list = [str(x) for x in company_id_list]
        company_id_list = pd.DataFrame(company_id_list)

        data = [tuple( x ) for x in company_id_list.values]

        curs.execute("CREATE temporary TABLE temp_tbl ( COMPANY_ID bigint );")
        sql = "INSERT INTO temp_tbl(COMPANY_ID) values (%s);"
        curs.executemany(sql, data)
        conn.commit()

        queryString = "select * from MEUMS_COMP_REVISIT_HIS A join temp_tbl B on A.COMPANY_ID=B.COMPANY_ID;"
        curs.execute(queryString)
        p = pd.DataFrame( curs.fetchall() )

        conn.close()

        return p

    p1 = get_ci_revisit_jjw(company_id_list)
    p2 = get_ci_revisit_cj(company_id_list)
    p = p1.append(p2)
    p.reset_index(drop=True, inplace=True)

    return p

def get_ci_revisit_usr(epopcon_id_list):
    # JAJUWA
    def get_ci_revisit_usr_jjw(epopcon_id_list):
        conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        epopcon_id_list = [ x for x in epopcon_id_list]
        epopcon_id_list = pd.DataFrame(epopcon_id_list)

        data = [tuple( x ) for x in epopcon_id_list.values]

        curs.execute("CREATE temporary TABLE temp_tbl ( EPOPCON_ID char(100), INDEX EPOPCON_ID_INDEX (EPOPCON_ID) );")
        sql = "INSERT INTO temp_tbl(EPOPCON_ID) values (%s);"
        curs.executemany(sql, data)
        conn.commit()

        queryString = "select * from MEUMS_COMP_REVISIT_HIS A join temp_tbl B on A.EPOPCON_ID=B.EPOPCON_ID;"
        curs.execute(queryString)

        try:
            p = pd.DataFrame( curs.fetchall() )
        except:
            p = pd.DataFrame([])

        conn.close()
        return p

    # CJ
    def get_ci_revisit_usr_cj(epopcon_id_list):
        conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        epopcon_id_list = [ x  for x in epopcon_id_list]
        epopcon_id_list = pd.DataFrame(epopcon_id_list)

        data = [tuple( x ) for x in epopcon_id_list.values]

        curs.execute("CREATE temporary TABLE temp_tbl ( EPOPCON_ID char(100), INDEX EPOPCON_ID_INDEX (EPOPCON_ID) );")
        sql = "INSERT INTO temp_tbl(EPOPCON_ID) values (%s);"
        curs.executemany(sql, data)
        conn.commit()

        queryString = "select * from MEUMS_COMP_REVISIT_HIS A join temp_tbl B on A.EPOPCON_ID=B.EPOPCON_ID;"
        curs.execute(queryString)

        try:
            p = pd.DataFrame( curs.fetchall() )
        except:
            p = pd.DataFrame([])

        conn.close()

        return p

    p1 = get_ci_revisit_usr_jjw(epopcon_id_list)
    p2 = get_ci_revisit_usr_cj(epopcon_id_list)

    p = pd.DataFrame([])
    p = p.append(p1)
    p = p.append(p2)

    p.reset_index(drop=True, inplace=True)

    return p



def get_ci_revisit_adjacent(epopcon_id, deal_dt, poi_name):
    adjacent_threshold_before = 3
    adjacent_threshold_after = 6

    if epopcon_id.startswith('ep'):
        conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
    else:
        conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')

    curs = conn.cursor(pymysql.cursors.DictCursor)

    day_before = deal_dt - timedelta(hours = adjacent_threshold_before)
    day_after = deal_dt + timedelta(hours = adjacent_threshold_after)

    stopCO_NAME = ['택시' ] + [poi_name]
    stopCATE1 = ['기차', '버스', '택시', '온라인쇼핑', '인터넷', '휴대폰', '간편결제', '결재', '기타', '공공요금', '관리비']

    try:
        queryString = "select * from MEUMS_COMP_REVISIT_HIS where EPOPCON_ID='"+epopcon_id+"' and DEAL_DT >= '"+str(day_before)+"' and DEAL_DT < '"+str(deal_dt)+"' ;"
        curs.execute(queryString)
        p1 = pd.DataFrame( curs.fetchall() )
        c1 = get_ci_company_by_id(p1['COMPANY_ID'].tolist())
        p1 = pd.merge(p1, c1, how='inner', left_on = 'COMPANY_ID', right_on = 'ID')
        [p1.drop( p1[p1.CO_NAME == coname].index, inplace=True ) for coname in stopCO_NAME]
        [p1.drop( p1[p1.CATE1 == cate1].index, inplace=True ) for cate1 in stopCATE1]
        pp = p1
        p1 = p1.loc[p1['DEAL_DT'].idxmax()].squeeze()

    except:
        p1 = None
        c1 = pd.DataFrame([])
        pp = pd.DataFrame([])

    try:
        queryString = "select * from MEUMS_COMP_REVISIT_HIS where EPOPCON_ID='"+epopcon_id+"' and DEAL_DT <= '"+str(day_after)+"' and DEAL_DT > '"+str(deal_dt)+"' ;"
        curs.execute(queryString)
        p2 = pd.DataFrame( curs.fetchall() )
        c2 = get_ci_company_by_id(p2['COMPANY_ID'].tolist())
        p2 = pd.merge(p2, c2, how='inner', left_on = 'COMPANY_ID', right_on = 'ID')
        [p2.drop( p2[p2.CO_NAME == coname].index, inplace=True ) for coname in stopCO_NAME]
        [p2.drop( p2[p2.CATE1 == cate1].index, inplace=True ) for cate1 in stopCATE1]
        pp = pp.append(p2)
        p2 = p2.loc[p2['DEAL_DT'].idxmax()].squeeze()
    except:
        p2 = None
        c2 = pd.DataFrame([])


    conn.close()

    return p1, p2, pp

#select * from MEUMS_LATEST_LIFEZONE where EPOPCON_ID='cjcis15a3e49e70200ba077c8b184d';

def get_ci_life_zone(epopcon_id_list):
    def get_ci_life_zone_jjw(epopcon_id_list):
        conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        epopcon_id_list = [ x for x in epopcon_id_list]
        epopcon_id_list = pd.DataFrame(epopcon_id_list)

        data = [tuple( x ) for x in epopcon_id_list.values]

        curs.execute("CREATE temporary TABLE temp_tbl ( EPOPCON_ID char(100) );")
        sql = "INSERT INTO temp_tbl(EPOPCON_ID) values (%s);"
        curs.executemany(sql, data)
        conn.commit()

        queryString = "select * from MEUMS_LATEST_LIFEZONE A join temp_tbl B on A.EPOPCON_ID=B.EPOPCON_ID;"
        curs.execute(queryString)

        try:
            p = pd.DataFrame( curs.fetchall() )
        except:
            p = pd.DataFrame([])

        conn.close()
        return p

    # CJ
    def get_ci_life_zone_cj(epopcon_id_list):
        conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        epopcon_id_list = [ x  for x in epopcon_id_list]
        epopcon_id_list = pd.DataFrame(epopcon_id_list)

        data = [tuple( x ) for x in epopcon_id_list.values]

        curs.execute("CREATE temporary TABLE temp_tbl ( EPOPCON_ID char(100) );")
        sql = "INSERT INTO temp_tbl(EPOPCON_ID) values (%s);"
        curs.executemany(sql, data)
        conn.commit()

        queryString = "select * from MEUMS_LATEST_LIFEZONE A join temp_tbl B on A.EPOPCON_ID=B.EPOPCON_ID;"
        curs.execute(queryString)

        try:
            p = pd.DataFrame( curs.fetchall() )
        except:
            p = pd.DataFrame([])

        conn.close()

        return p

    j_usr = [e for e in epopcon_id_list if e.startswith('ep')]
    c_usr = [e for e in epopcon_id_list if e.startswith('cj')]

    p1 = get_ci_life_zone_jjw(j_usr)
    p2 = get_ci_life_zone_cj(c_usr)

    print(len(j_usr), len(p1))
    print(len(c_usr), len(p2))

    p = pd.DataFrame([])
    p = p.append(p1)
    p = p.append(p2)

    p.reset_index(drop=True, inplace=True)

    return p

def get_ci_revisit_regDt(day):
    
    a=datetime.now()
    # JAJUWA
    def get_ci_revisit_regDt_jjw(date):
        conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        queryDateFrom = datetime.strftime(date, '%Y-%m-%d' + ' 00:00:00')
        queryDateTo = datetime.strftime(date, '%Y-%m-%d' + ' 23:59:59')
        queryString = "select * from MEUMS_COMP_REVISIT_HIS where REG_DT between '"+queryDateFrom+"' and '"+queryDateTo+"' and DEAL_DT between '2018-01-23 00:00:00' and '2018-03-01 00:00:00';"
        
        curs.execute(queryString)

        try:
            p = pd.DataFrame( curs.fetchall() )
        except:
            p = pd.DataFrame([])

        conn.close()

        return p

    # CJ
    def get_ci_revisit_regDt_cj(date):
        conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        queryDateFrom = datetime.strftime(date, '%Y-%m-%d' + ' 00:00:00')
        queryDateTo = datetime.strftime(date, '%Y-%m-%d' + ' 23:59:59')
        queryString = "select * from MEUMS_COMP_REVISIT_HIS where REG_DT between '"+queryDateFrom+"' and '"+queryDateTo+"' and DEAL_DT between '2018-01-23 00:00:00' and '2018-03-01 00:00:00';"
        curs.execute(queryString)

        try:
            p = pd.DataFrame( curs.fetchall() )
        except:
            p = pd.DataFrame([])

        conn.close()

        return p

    p1 = get_ci_revisit_regDt_jjw(day)
    p2 = get_ci_revisit_regDt_cj(day)

    p = pd.DataFrame([])
    p = p.append(p1)
    p = p.append(p2)

    p.reset_index(drop=True, inplace=True)
    print('get_ci_revisit_regDt : ', datetime.now()-a, len(p), 'revisit records.')
    return p




def get_min_max_revisit_regDt():
    conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute("select min(REG_DT), max(REG_DT) from MEUMS_COMP_REVISIT_HIS;")
    p1 = pd.DataFrame( curs.fetchall() )
    conn.close()

    conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    curs.execute("select min(REG_DT), max(REG_DT) from MEUMS_COMP_REVISIT_HIS;")
    p2 = pd.DataFrame( curs.fetchall() )
    conn.close()

    p = pd.DataFrame([])
    p = p.append(p1)
    p = p.append(p2)

    return p['min(REG_DT)'].min(), p['max(REG_DT)'].max()




def get_ci_company_by_id(company_id_list):
    a=datetime.now()
    conn = pymysql.connect(host='133.186.143.151', port=13306, user='eums', password='eums00!q', db='eums-shared', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    #curs.execute("CREATE temporary TABLE temp_tbl ( COMPANY_ID bigint, PRIMARY KEY (COMPANY_ID), UNIQUE INDEX COMPANY_ID_INDEX (COMPANY_ID) );")
    #curs.execute("CREATE temporary TABLE temp_tbl ( COMPANY_ID bigint, PRIMARY KEY (COMPANY_ID)  );")
    #curs.execute("CREATE temporary TABLE temp_tbl ( COMPANY_ID bigint   );")
    curs.execute("CREATE temporary TABLE temp_tbl ( COMPANY_ID bigint, UNIQUE INDEX COMPANY_ID_INDEX (COMPANY_ID) );")


    company_df = pd.DataFrame([])
    slice_list = []
    for i, e in enumerate(company_id_list):
        slice_list.append(e)
        if(len(slice_list) >= 1000 or i == len(company_id_list)-1):
            slice_list = [str(x) for x in slice_list]
            slice_list = pd.DataFrame(slice_list)

            data = [tuple( x ) for x in slice_list.values]

            sql = "INSERT INTO temp_tbl(COMPANY_ID) values (%s);"
            curs.executemany(sql, data)
            conn.commit()

            queryString = "select * from temp_tbl A join MEUMS_COMPANY B on A.COMPANY_ID=B.ID;"
            curs.execute(queryString)

            p = pd.DataFrame( curs.fetchall() )
            #curs.execute("TRUNCATE TABLE temp_tbl;")

            company_df=company_df.append(p)
            #print(len(slice_list), ' company IDs including ', p.CO_NAME.tolist()[0] )
            slice_list = []

    conn.close()

    company_df.reset_index(drop=True, inplace=True)

    print('get_ci_company_by_id : ', datetime.now()-a, len(company_df), 'company ids.')
    return company_df



def get_ci_company_by_id(company_id_list):
    a=datetime.now()
    conn = pymysql.connect(host='133.186.143.151', port=13306, user='eums', password='eums00!q', db='eums-shared', charset='utf8')
    #conn = pymysql.connect(host='192.168.0.50', port=3306, user='eums', password='eums00!q', db='eums-shared2', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    company_df = pd.DataFrame([])
    n = 1000
    list_list = [company_id_list[i:i+n] for i in range(0, len(company_id_list), n)]
    for slice_list in list_list:
        company_id_list_str = ','.join(str(e) for e in slice_list)
        queryString = "select * from MEUMS_COMPANY where status in ('1','0') and ID in ("+company_id_list_str+");"
        curs.execute(queryString)
        p = pd.DataFrame( curs.fetchall() )
        company_df = company_df.append(p)

    '''
    slice_list = []
    for i, e in enumerate(company_id_list):
        slice_list.append(e)
        if(len(slice_list) >= 1000 or i == len(company_id_list)-1):
            company_id_list_str = ','.join(str(e) for e in slice_list)

            queryString = "select * from MEUMS_COMPANY where ID in ("+company_id_list_str+");"
            curs.execute(queryString)
            p = pd.DataFrame( curs.fetchall() )
            company_df = company_df.append(p)

            slice_list = []
    '''

    conn.close()

    company_df.reset_index(drop=True, inplace=True)

    print('get_ci_company_by_id : ', datetime.now()-a, len(company_df), 'company ids.')
    return company_df



def get_ci_adid(epopcon_id_list):
    a=datetime.now()

    def get_ci_adid_jjw(epopcon_id_list):
        conn = pymysql.connect(host='133.186.135.21', user='eums', password='eums00!q', db='eums', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        adid_df = pd.DataFrame([])
        n = 500
        list_list = [epopcon_id_list[i:i+n] for i in range(0, len(epopcon_id_list), n)]
        for slice_list in list_list:
            epopcon_id_list_str = ','.join("'"+str(e)+"'" for e in slice_list)
            queryString = "select * from MEUMS_PUSHID_INFO where EPOPCON_ID in ("+epopcon_id_list_str+");"
            curs.execute(queryString)
            p = pd.DataFrame( curs.fetchall() )
            adid_df = adid_df.append(p)

        '''
        slice_list = []
        for i, e in enumerate(epopcon_id_list):
            slice_list.append(e)
            if(len(slice_list) >= 1000 or i == len(epopcon_id_list)-1):
                epopcon_id_list_str = ','.join("'"+str(e)+"'" for e in slice_list)

                queryString = "select * from MEUMS_PUSHID_INFO where EPOPCON_ID in ("+epopcon_id_list_str+");"
                curs.execute(queryString)
                p = pd.DataFrame( curs.fetchall() )
                adid_df = adid_df.append(p)

                slice_list = []
        '''
        conn.close()

        adid_df.reset_index(drop=True, inplace=True)

        return adid_df

    # CJ
    def get_ci_adid_cj(epopcon_id_list):
        conn = pymysql.connect(host='133.186.135.222', port=13306, user='eums', password='eums00!q', db='eums-business', charset='utf8')
        curs = conn.cursor(pymysql.cursors.DictCursor)

        adid_df = pd.DataFrame([])
        n = 500
        list_list = [epopcon_id_list[i:i+n] for i in range(0, len(epopcon_id_list), n)]
        for slice_list in list_list:
            epopcon_id_list_str = ','.join("'"+str(e)+"'" for e in slice_list)
            queryString = "select * from MEUMS_PUSHID_INFO where EPOPCON_ID in ("+epopcon_id_list_str+");"
            curs.execute(queryString)
            p = pd.DataFrame( curs.fetchall() )
            adid_df = adid_df.append(p)

        '''
        slice_list = []
        for i, e in enumerate(epopcon_id_list):
            slice_list.append(e)
            if(len(slice_list) >= 1000 or i == len(epopcon_id_list)-1):
                epopcon_id_list_str = ','.join("'"+str(e)+"'" for e in slice_list)

                queryString = "select * from MEUMS_PUSHID_INFO where EPOPCON_ID in ("+epopcon_id_list_str+");"
                curs.execute(queryString)
                p = pd.DataFrame( curs.fetchall() )
                adid_df = adid_df.append(p)

                slice_list = []
        '''

        conn.close()

        adid_df.reset_index(drop=True, inplace=True)

        return adid_df

    j_usr = [e for e in epopcon_id_list if e.startswith('ep')]
    c_usr = [e for e in epopcon_id_list if e.startswith('cj')]
    #print('jjw', len(j_usr) )
    #print('cj', len(c_usr) )

    p1 = get_ci_adid_jjw(j_usr)
    p2 = get_ci_adid_cj(c_usr)

    #print('jjw', len(j_usr), len(p1))
    #print('cj', len(c_usr), len(p2))

    p = pd.DataFrame([])
    p = p.append(p1)
    p = p.append(p2)

    p = p [['EPOPCON_ID', 'ADVTM_ID']]
    #p.drop_duplicates(inplace=True)
    p.reset_index(drop=True, inplace=True)

    print('get_ci_adid : ', datetime.now()-a)

    return p

def get_ci_code():
    conn = pymysql.connect(host='133.186.143.151', port=13306, user='eums', password='eums00!q', db='eums-shared', charset='utf8')
    #conn = pymysql.connect(host='192.168.0.50', port=3306, user='eums', password='eums00!q', db='eums-shared2', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    queryString = "select * from MEUMS_CODE;"
    curs.execute(queryString)
    p = pd.DataFrame( curs.fetchall() )

    conn.close()

    return p

def get_ci_code_cardcomp():
    cardcomp = get_ci_code()[['CODE', 'CODE_NAME', 'GROUP_CODE']]
    #cardcomp = cardcomp[cardcomp['GROUP_CODE'] == 'CARDCOMP'][['CODE', 'CODE_NAME']]
    cardcomp = cardcomp[cardcomp['GROUP_CODE'] == 'CARDCPDV'][['CODE', 'CODE_NAME']]

    return cardcomp


def revisit_in_dt_df_write(revisit_in_dt_df, industry):
    #del revisit_in_dt_df['ID']

    conn = pymysql.connect(host='192.168.0.50', port=3306, user='eums', password='eums00!q', db='eums-shared2', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    # 'EPOPCON_ID', 'COMPANY_ID', 'DEAL_DT', 'PAYMENT', 'CARD_NAME', 'ISSUED_COMPANY_ID', 'REG_DT', 'CO_NAME', 'CO_NAME_R', 'CATE', 'CATE1', 'TAG', 'ADVTM_ID'

    #data = [tuple( x ) for x in a.values]
    data = [list( x ) for x in revisit_in_dt_df.values]
    for d in data:
        d[2] = d[2].strftime('%Y-%m-%d %H:%M:%S')
        d[6] = d[6].strftime('%Y-%m-%d %H:%M:%S')
        d[10] == '' if d[10] != d[10] else d[10]
        d[11] == '' if d[11] != d[11] else d[11]
        sql = "INSERT INTO mezzo_"+industry+"(EPOPCON_ID, COMPANY_ID, DEAL_DT, PAYMENT, CARD_NAME, ISSUED_COMPANY_ID, REG_DT, CO_NAME, CO_NAME_R, CATE, CATE1, TAG, ADVTM_ID) values (" + ','.join('"'+str(e).replace('"', '_')+'"' for e in d) + ");"
        curs.execute(sql)

    conn.commit()
    conn.close()


def read_mezzo(industry):
    conn = pymysql.connect(host='192.168.0.50', port=3306, user='eums', password='eums00!q', db='eums-shared2', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM mezzo_"+industry+" ;"
    curs.execute(sql)
    p = pd.DataFrame( curs.fetchall() )
    conn.close()
    return p

def read_mezzo_park(industry):
    conn = pymysql.connect(host='192.168.0.50', port=3306, user='eums', password='eums00!q', db='eums-shared2', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM mezzo_"+industry+" WHERE CATE1='주차장';"
    curs.execute(sql)
    p = pd.DataFrame( curs.fetchall() )
    conn.close()
    return p

def export_to_db(df):
    from collections import Counter

    print('empty \'ADVTM_ID\'', len(df[df['ADVTM_ID'] == '']))
    df = df[df['ADVTM_ID'] != '']
    df = df[[ 'DEAL_DT', 'ADVTM_ID', 'BRAND_NAME', 'CO_NAME', 'CATE', 'CATE1', 'CARD_NAME', 'CARD_COMP', 'TAG', 'PAYMENT' ]]
    df = df.rename(columns = {'ADVTM_ID':'ADID'} )

    print(datetime.now())
    # df.sort_values(by=['DEAL_DT'], ascending=False, inplace=True)
    # print(datetime.now())
    
    # for i, r in df.iterrows():
    #     if(r.DEAL_DT > datetime.strptime('2018-01-23', '%Y-%m-%d')):
    #         df.at[i, 'DEAL_DT'] = r.DEAL_DT.replace(year=2017)
    #         #print(r.DEAL_DT)
    #     else:
    #         break
    # print(datetime.now())

    letter_counts = Counter(df.ADID.tolist())

    user_rank = pd.DataFrame.from_dict(letter_counts, orient='index' )
    user_rank.rename(columns={0: 'PAY_COUNT'}, inplace=True)
    user_rank['ADID'] = user_rank.index

    df = pd.merge(df, user_rank, how='left', on='ADID')
    #df.sort_values(by=['DEAL_DT'], ascending=False, inplace=True)
    df.sort_values(by=['PAY_COUNT'], ascending=False, inplace=True)

    df.reset_index(drop=True, inplace=True)
    print(datetime.now())


    return df


if __name__ == '__main__':
    None

    ind1='car'
    ind2='beauty'

    c=read_mezzo (ind1)
    b=read_mezzo (ind2)

    export_c = export_to_db(c, ind1)
    export_b = export_to_db(b, ind2)

    sample_c=export_c.iloc[:100]
    sample_b=export_b.iloc[:100]

    export_c.to_csv(ind1+'.csv')
    export_b.to_csv(ind2+'.csv')

    export_b.DEAL_DT.max()

    '''
    dateFrom = datetime.strptime('2016-03-05 00:00:00', '%Y-%m-%d %H:%M:%S')
    dateTo = datetime.strptime('2016-03-05 12:23:38', '%Y-%m-%d %H:%M:%S')
    p = get_ci_revisit_regDt(dateFrom, dateTo)
    company_id_list = p.COMPANY_ID.unique().tolist()
    company_df = get_ci_company_by_id(company_id_list)

    '''



def export_revisit_in_df(revisit_in_df, d):
    from collections import Counter

    card_comp = get_ci_code_cardcomp()
    revisit_in_df = pd.merge(revisit_in_df, card_comp, how='left', left_on='ISSUED_COMPANY_ID', right_on='CODE')
    revisit_in_df = revisit_in_df[['DEAL_DT', 'ADVTM_ID', 'CO_NAME', 'CATE', 'CATE1', 'CARD_NAME', 'CODE_NAME', 'TAG', 'PAYMENT' ]]

    letter_counts = Counter(revisit_in_df.ADVTM_ID.tolist())

    user_rank = pd.DataFrame.from_dict(letter_counts, orient='index' )
    user_rank.rename(columns={0: 'PAY_COUNT'}, inplace=True)
    user_rank['ADVTM_ID'] = user_rank.index

    revisit_in_df = pd.merge(revisit_in_df, user_rank, how='left', on='ADVTM_ID')
    revisit_in_df.sort_values(by=['DEAL_DT'], ascending=False, inplace=True)
    revisit_in_df.reset_index(drop=True, inplace=True)

    excelExport(revisit_in_df, 'revisit_in'+d.strftime('%Y-%m-%d'), d.strftime('%Y-%m-%d'))

def filter_industry(company, industry):
    filtered = pd.DataFrame([])

    if(industry == 'beauty'):
        filtered = filtered.append( company[company['CATE'] == '뷰티'] )
        filtered = filtered.append( company[company['CATE'] == '패션'] )
        filtered = filtered.append( company[company['CO_NAME'].str.contains('피부|코스메틱|cosmetics|화장품|요가|헤어|뷰티|큐티|beauty|성형|에스테틱|필라테스')] )
        filtered = filtered.append( company[company['TAG'].str.contains('피부|드럭스토어|코스메틱|cosmetics|화장품|요가|헤어|뷰티|큐티|beauty|성형|에스테틱|필라테스')] )
        filtered = filtered.append( company[company['CO_NAME'].str.contains('미용') & ~ company['CO_NAME'].str.contains('취미용품')] )
        filtered = filtered.append( company[company['TAG'].str.contains('미용') & ~ company['TAG'].str.contains('취미용품')] )
        filtered = filtered.append( company[company['CO_NAME'].str.contains('비만') & ~ company['CO_NAME'].str.contains('만두')] )
        filtered = filtered.append( company[company['TAG'].str.contains('비만') & ~ company['TAG'].str.contains('만두')] )
        filtered = filtered.append( company[company['CO_NAME'].str.contains('네일') & ~ company['CO_NAME'].str.contains('커피') ])
        filtered = filtered.append( company[company['TAG'].str.contains('네일')  & ~ company['TAG'].str.contains('커피') ])
        
    elif(industry == 'car'):
        filtered = filtered.append( company[company['CATE'] == '자동차'] )
        filtered = filtered.append( company[(company['CATE'] == '교통') & company['TAG'].str.contains('주유|충전|주차') ] )
        filtered = filtered.append( company[(company['CATE'] == '교통') & company['TAG'].str.contains('[렌|랜][트|터|타]') ] )
        filtered = filtered.append( company[company['CO_NAME'].str.contains('면허|휴게소|대리운전')] )
        filtered = filtered.append( company[company['CO_NAME'].str.contains('운전') & company['CO_NAME'].str.contains('학원') ])

    filtered.drop_duplicates(inplace=True)

    #filtered_names = filtered.CO_NAME.tolist()

    filtered_out = list ( set(company.COMPANY_ID.unique().tolist()) - set(filtered.COMPANY_ID.unique().tolist()) )
    #filtered_out = pd.DataFrame(filtered_out)
    #filtered_out.rename(columns={0: 'COMPANY_ID'}, inplace=True)

    return filtered, filtered_out

def load_snapshot(industry):
    try:
        revisit_in_df = pickle.load(open('revisit_in.'+industry, 'rb'))
    except:
        print('new revisit_in pickle')
        revisit_in_df = pd.DataFrame([])

    try:
        user_all = pickle.load(open('user_all.'+industry, 'rb'))
    except:
        print('new all user list pickle')
        user_all = []

    try:
        user_in_df = pickle.load(open('user_in.'+industry, 'rb'))
        user_in = user_in_df.EPOPCON_ID.unique().tolist()
    except:
        print('new industry in user df pickle')
        user_in_df = pd.DataFrame([])
        user_in = []
    try:
        user_ex = pickle.load(open('user_ex.'+industry, 'rb'))
    except:
        print('new industry ex user list pickle')
        user_ex = []

    try:
        comp_in_df = pickle.load(open('comp_in.'+industry, 'rb'))
        comp_in = comp_in_df.COMPANY_ID.unique().tolist()
    except:
        print('new industry in comp df pickle')
        comp_in_df = pd.DataFrame([])
        comp_in = []
    try:
        comp_ex = pickle.load(open('comp_ex.'+industry, 'rb'))
    except:
        print('new industry ex comp list pickle')
        comp_ex = []

    return revisit_in_df, user_in_df, comp_in_df, user_all, user_in, comp_in, user_ex, comp_ex





