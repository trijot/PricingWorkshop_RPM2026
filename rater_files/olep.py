import pandas as pd
import numpy as np
import datetime as dt

rated = pd.read_csv('rated_policies.csv')

olp = rated[['policy', 'olp', 'eff_dt', 'current_premium']].copy() #fields of interest 
olp['eff_dt'] = pd.to_datetime(olp['eff_dt']).dt.normalize()
olp['exp_dt'] = olp['eff_dt'] + pd.DateOffset(years=1)
olp['total_days'] = (olp['exp_dt'] - olp['eff_dt']).apply(lambda x: x.days)
olp.loc[:,'exposure'] = 1.0 # exposure set to one car per policy

# timeline dataframe from first effective to last expiration
timeline = pd.DataFrame({
    'm_start': pd.date_range(
        start=olp.eff_dt.min().replace(day=1), 
        end=olp.exp_dt.max(), 
        freq='MS'
    )
})
timeline.loc[:,'m_next'] = timeline.m_start + pd.offsets.MonthBegin(1) #pair each month with the subsequent month for easier calculations

olep = olp.merge(timeline, how='cross') #cross join premium information onto the timeline 
olep = olep[ #then drop entries without exposure
    (olep.m_start < olep.exp_dt) & 
    (olep.m_next > olep.eff_dt)
].copy()

#grab arrays of first and last dates by policy
starts = np.maximum(olep.eff_dt, olep.m_start)
ends = np.minimum(olep.exp_dt, olep.m_next)

#calculate proportion of exposure in each month by policy and earn out premiums/exposures
olep.loc[:,'days_in_month'] = (ends - starts).dt.days
olep.loc[:,'ratio'] = olep.days_in_month / olep.total_days
olep.loc[:,'olep'] = olep.ratio * olep.olp
olep.loc[:,'ep'] = olep.ratio * olep.current_premium
olep.loc[:,'ee'] = olep.ratio * olep.exposure

#balance out totals to account for rounding floats
for col, source in [('olep', 'olp'), ('ep', 'current_premium'), ('ee', 'exposure')]:
    total_col = f'policy_total_{col}'
    diff_col = f'diff_{col}'
    olep.loc[:,total_col] = olep.groupby('policy')[col].transform('sum')
    olep.loc[:,diff_col] = olep[source] - olep[total_col]
olep = olep.sort_values(['policy', 'm_start'])
is_last = ~olep.duplicated('policy', keep='last')
olep.loc[is_last, 'olep'] += olep.loc[is_last, 'diff_olep']
olep.loc[is_last, 'ep'] += olep.loc[is_last, 'diff_ep']
olep.loc[is_last, 'ee'] += olep.loc[is_last, 'diff_ee']

olep.loc[:,'xym'] = olep.m_start.dt.strftime('%Y%m') #adding exposure year month as a key for the indication tables
olep = olep[['policy', 'm_start', 'xym', 'olep', 'ep', 'ee']]
olep.to_csv('olep.csv', index=False)
