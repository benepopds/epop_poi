#This functions are implementation of a paper: Estimation Frequency of Change
#http://ilpubs.stanford.edu:8090/471/1/2000-4.pdf

#We can assume that the change of stock amounts follows poisson distribution
#Then, by estimating the parameter, we can model the real world and predict the futuer
#We call the parameter lambda from poisson model as 'R_score'
#The unit time can be setted as you wand: "period"

#get r_scores from a week(n=7)
def calculate_r(x, n=7):
    x_c = n - x
    #0.5 for continuity correction
    r = -math.log( (x_c + 0.5) / (n + 0.5) )
    return r

#get r_score from a item
#there must be only one item(#stocks can be plural)
#weight is empirical adjustment. dont care about it
def get_r_from_df(target, period, weight=1.5, return_raw=False):

    resampled = target.resample(period)['isChanged'].sum()
    n_chnaged = sum(resampled > 0)
    n_summed = len(resampled)
    #n_summed = target.COLLECT_DAY.nunique()
    r_result = calculate_r(x=n_chnaged, n = n_summed) * weight
    
    if return_raw:
        return resampled, r_result
    else:
        return r_result


#get r scores from items
def get_r_scores(items_df, period):
    thisweek = datetime.datetime.today().isocalendar()[1]
    items_df.columns = items_df.columns.str.upper()
    items_df = items_df.sort_index()
    items_df['REG_DT'] = pd.to_datetime(items_df['REG_DT'])
    items_df['WEEK'] = thisweek - items_df['REG_DT'].dt.week
    r_aggr = []

    for idx_item, group_item in items_df.groupby('ITEM_ID'):        
        groups = []
        group_item = group_item.sort_index()
        r_lst = []

        for idx, group in group_item.groupby('STOCK_ID'):
            if len(group) >= 1:
                group = group.sort_values("REG_DT")
                change_v = np.where(np.append([0], np.diff(group.STOCK_AMOUNT.values)) !=0, 1, 0)
                group = group.assign(isChanged = change_v)
                groups.append(group)

        target = pd.concat(groups)
        target = target.assign(COLLECT_DAY = pd.to_datetime(target.COLLECT_DAY))
        target = target.set_index('COLLECT_DAY', drop=False)
        
        #the weights of R exponentially decay. 
        for week, week_item in target.groupby('WEEK'):
            r = get_r_from_df(week_item, period, return_raw=False)
            r_lst.append((idx_item, week, r))

        r_df = pd.DataFrame(r_lst, columns = ['ITEM_ID', 'WEEK', 'R_SCORE'])
        weight = np.power(0.5,r_df['WEEK'])
        weighed_r = sum(weight*r_df['R_SCORE']) / sum(weight)

        r_aggr.append((idx_item,weighed_r))

    return r_aggr