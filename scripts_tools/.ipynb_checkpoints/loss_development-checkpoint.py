import pandas as pd
import numpy as np
import datetime as dt

rated = pd.read_csv('../rater_files/rated_policies.csv')
loss = rated[rated.coll_loss > 0].copy()
loss.eff_dt=pd.to_datetime(loss.eff_dt)
loss.loc[:,'py'] = loss.eff_dt.dt.year
loss.loc[:,'exp_dt'] = loss.eff_dt + pd.offsets.DateOffset(years=1) - pd.Timedelta(days=1)
loss.loc[:,'ly_start'] = pd.to_datetime(loss.loss_year.astype(str) + '-01-01')
loss.loc[:,'ly_end'] = pd.to_datetime(loss.loss_year.astype(str) + '-12-31')
loss.loc[:,'valid_start'] = np.maximum(loss.eff_dt, loss.ly_start)
loss.loc[:,'valid_end'] = np.minimum(loss.exp_dt, loss.ly_end)

diff = (loss.valid_end - loss.valid_start).dt.days
loss.loc[:,'loss_dt'] = loss.valid_start + pd.to_timedelta(np.random.rand(len(loss)) * diff, unit='D')
loss.loc[:,'start_month'] = loss.loss_dt.dt.to_period('M').dt.to_timestamp()

master_months = pd.date_range(start='2020-01-01', end='2025-12-01', freq='MS')
calendar = pd.DataFrame({'eval_dt': master_months, 'key': 1})
loss.loc[:,'key'] = 1

expanded = pd.merge(loss, calendar, on='key').drop('key', axis=1)
expanded = expanded[expanded.eval_dt >= expanded.start_month].copy()
expanded.loc[:,'maturity'] = (
    (expanded.eval_dt.dt.year - expanded.start_month.dt.year) * 12 +
    (expanded.eval_dt.dt.month - expanded.start_month.dt.month)
)+1

unique_claims = expanded[['policy', 'coll_loss']].drop_duplicates()
n_claims = len(unique_claims)
ids = unique_claims.policy.values
ultimates = unique_claims.coll_loss.values

n_slots = 6 
timings = (np.random.beta(1, 3, size=(n_claims, n_slots)) * 35 + 1).astype(int)
alphas = 1 + (timings / 36) * 5
gamma_samples = np.random.gamma(alphas, 1)
weights = gamma_samples / gamma_samples.sum(axis=1, keepdims=True)
payment_amounts = weights * ultimates[:, np.newaxis]

pay_matrix = np.zeros((n_claims, 37))
for i in range(n_claims):
    for slot in range(n_slots):
        m = timings[i, slot]
        pay_matrix[i, m:] += payment_amounts[i, slot]

lookup = {cid: pay_matrix[i] for i, cid in enumerate(ids)}

expanded.loc[:,'paid'] = [lookup[cid][int(min(m, 36))] if m > 0 else 0.0 
                   for cid, m in zip(expanded.policy, expanded.maturity)]

expanded.loc[:,'reporting_pct'] = 1 - (0.8 ** (expanded.maturity + 1))
noise = np.random.uniform(0.8, 1.2, size=len(expanded))
expanded.loc[:,'incurred'] = expanded.paid + (expanded.coll_loss - expanded.paid) * expanded.reporting_pct * noise
expanded.loc[:,'incurred'] = np.maximum(expanded.incurred, expanded.paid)

results = expanded[['policy', 'maturity', 'loss_dt', 'eval_dt', 'paid', 'incurred']].copy()
results = results.sort_values(by=['policy', 'eval_dt'])
results = results[results.eval_dt.dt.year <= 2025]
results.loc[:,'aym'] = results.loss_dt.apply(lambda t: f'{t.year}{t.month:02d}')
results.loc[:,'eval_dt'] = results.eval_dt.apply(lambda t: f'{t.year}{t.month:02d}')

results.to_csv('loss_development.zip', index=False, compression={'method': 'zip', 'archive_name': 'loss_development.csv'})
results.to_csv('loss_development.csv',index=False)

