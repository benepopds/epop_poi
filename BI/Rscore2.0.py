def calculate_r(x, n=7):
    x_c = n - x
    #0.5 for continuity correction
    r = -math.log( (x_c + 0.5) / (n + 0.5) )
    return r


def r_by_week(df, period):
    resampled = df.resample(period)['isChanged'].sum()
    return calculate_r(x=sum(resampled > 0), n=max(len(resampled), 7)) * 1.5 #weight
    

def get_weighed_r_from_df(target, period='1D'):
    
    if len(target)==0: return -1
    elif target.isChanged.sum()==0: return 0

    r = target.groupby('week_dist').apply(r_by_week, '1D').reset_index()
    r.columns = ['WEEK', 'R_SCORE']
    weight = np.exp(-r['WEEK'])
    weighed_r = sum(weight*r['R_SCORE']) / sum(weight)
    
    return weighed_r
    


    
def get_r_scores(parq):
    items_df = pd.read_parquet(parq)
    items_df.columns = items_df.columns.str.upper()
    items_df = items_df.assign(REG_DT = pd.to_datetime(items_df['REG_DT']))
    max_reg = items_df.REG_DT.max()
    items_df = items_df.assign(week_dist = (max_reg-items_df.REG_DT).dt.days//7)
    
    r_aggr = []    
    for idx_item, group_item in items_df.groupby('ITEM_ID'):        
        groups = []
        
        for idx, group in group_item.groupby('STOCK_ID'):
            group = group.sort_values("REG_DT")
            group = group.assign(isChanged = np.where(np.append([0], np.diff(group.STOCK_AMOUNT.values)) !=0, 1, 0))
            groups.append(group)
        target = pd.concat(groups)
        
        #for RESAMPLE
        target = target.assign(COLLECT_DAY = pd.to_datetime(target.COLLECT_DAY))
        target = target.set_index('COLLECT_DAY', drop=False)
        r_aggr.append((idx_item, get_weighed_r_from_df(target)))
    
    return pd.DataFrame(r_aggr, columns=["ITEM_ID", "R_SCORE"])