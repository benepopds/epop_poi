#Service team crawl the items on MWS_COLT_EXECUTE_PLAN (servers can be differ for each sites)
#You need to specify the followings: "ITEM_NUM", "SERVER"(server to crawl), "ACT_DT"(time to crawl), "REG_DT"(the time you registed)
#You MUST TELL SERVICE TEAM BEFORE QUEUING
#You can not crawl the items whose ITEM_NUM does not exist in MWS_COLT_ITEM. It can raise an error.
#Similiarly, you can not crawl the closed item. It can raise an error, too YOU NEED TO CHECK IT EVERYTIME
##CAUTION: both of the errors can be severe. 
#Following code is a part of example
import datetime
from pytz import timezone  #When using jupyter from server instance, time zone can be set as in abroad
import pandas as pd



time_now = datetime.datetime.now()
act_df = pd.DataFrame(pd.date_range(
    start=(ceil_dt(time_now, datetime.timedelta(minutes=10))+datetime.timedelta(days=0)).strftime("%Y-%m-%d %H:%M:%S"),
    end=(time_now+datetime.timedelta(days=0)).strftime("%Y-%m-%d") + ' 23:50:00',
    freq='10Min'))
act_df.columns = ['ACT_DT']
act_df = act_df.assign(COLLECT_SITE='www.gsshop.gfk', REG_DT=time_now)

pd_que = pd.concat([act_df.assign(ITEM_NUM=i) for i in df_ref_que.ITEM_NUM])
pd_que.to_sql('MWS_COLT_ITEM_EXECUTE_PLAN', if_exists='append', con=engine, index=False)
