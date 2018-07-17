# Perform imports here:
import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN

engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.50:3306/eums?charset=utf8mb4", encoding = 'utf8' ,
                   pool_size=20,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

# id_query = """select EPOPCON_ID
# from MEUMS_COMP_REVISIT
# where CNT>300
# """
#
# id_list = pd.read_sql_query(id_query, engine)
# id_list.to_pickle('id')


id_list = pd.read_pickle('id')['EPOPCON_ID']

all_size, out_size = [1, 1]

result_list=[]
it=0
for id in id_list:
    print('find '+id+'...({}%)'.format(it*100//len(id_list)))
    data_query = """
    select EPOPCON_ID, COMPANY_ID, CO_NAME, LATITUDE, LONGITUDE, DEAL_DT, CARD_NAME, CATE, CATE1, PAYMENT
    from MEUMS_COMP_REVISIT_HIS join MEUMS_COMPANY  on MEUMS_COMPANY.ID = MEUMS_COMP_REVISIT_HIS.COMPANY_ID
    where EPOPCON_ID = '{}'
    """.format(id)

    test = pd.read_sql_query(data_query, engine)
    test = test.dropna(axis = 0)
    feature = test[['LONGITUDE', 'LATITUDE']]

    model = DBSCAN(eps=0.2, min_samples=max(3, len(feature) // 100))
    predict = pd.DataFrame(model.fit_predict(feature))
    predict.columns = ['predict']
    if len(predict.predict)>=3:
        test= pd.concat([test, predict], axis=1)
        test=test[test.predict==-1]
        result_list.append(test)

    it+=1
    result = pd.concat(result_list)

print('Start concat...')
result.to_pickle('result_all')

