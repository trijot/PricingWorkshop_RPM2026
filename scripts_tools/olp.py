import pandas as pd
import numpy as np
import datetime as dt

pol=pd.read_csv(r"C:\Users\seant\Desktop\GIT\PricingWorkshop_RPM2026\Personal Auto Policy Data and Rate Tables\Personal Auto Dataset and Premiums.csv")
pol.columns=pol.columns.str.lower().str.replace(' ','_')
tables=pd.read_excel('rate_tables.xlsx',sheet_name=None)

rated=pol.copy() #copy the policy table for rating
rated.loc[:,'policy']=rated.index.to_list() #policyid
rated=rated.dropna(subset=['vehicle_symbol','vendor_mileage']) #drop five instances of nan rating variables
rated.loc[:,'f_base_rate']=tables['base_rate'].base_rate[0] #set the base rate
#merge basic rating tables onto rating variables
for t in ['vendor_mileage','homeowner','passive_restraint',
          'tnc_coverage','vehicle_symbol','claims_free_years',
          'good_student','convictions','driver_training','state']:
    rated=rated.merge(tables[t],how='left',on=t)

#nearest merge on vehicle age to handle ages above the table maximum
rated=pd.merge_asof(
    rated.sort_values('vehicle_age'),
    tables['vehicle_age'],
    on='vehicle_age',
    direction='backward')

#driver class merges on the intersection of three variables
rated=rated.merge(
    tables['driver_class'],how='left',
    on=['policyholder_age','marital_status','policyholder_sex'])

#uw_points is a calculated field before merging to the uw_points rating table
rated.loc[:,'uw_points']=1+rated[
    ['claims_free_points','good_student_points','convictions_points','driver_training_points']
    ].sum(axis=1)
rated=rated.merge(tables['uw_points'],how='left',on='uw_points')

#multiplicative rating algorithm to arrive at pure premium
rated.loc[:,'olp']=rated[[f for f in rated.columns if f.startswith('f_')]].product(axis=1)
rated.loc[:,'expenses']=rated.olp*0.2+30
rated['eff_dt'] = pd.to_datetime(rated.policyeffectivedate)
rated.loc[:,'eym']=rated.eff_dt.apply(lambda t: f'{t.year}{t.month:02d}')

rated.to_csv('rated_policies.zip', index=False, compression={'method': 'zip', 'archive_name': 'rated_policies.csv'})
rated.to_csv('rated_policies.csv',index=False)


