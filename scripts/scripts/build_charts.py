import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.rcParams.update({
    'font.family':'sans-serif','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
    'axes.grid':True,'grid.alpha':0.25,'figure.facecolor':'white','axes.facecolor':'white'
})
NAVY='#1B2A4A'; TEAL='#0E7C7B'; CORAL='#E8604C'; GOLD='#E3B23C'; GREY='#8A94A6'; BLUE='#3E6FE0'
PAL=[NAVY,TEAL,CORAL,GOLD,BLUE,GREY]

base='/mnt/user-data/uploads/'
fact=pd.read_csv(base+'fact_transactions_Updated_.csv')
worker=pd.read_csv(base+'dim_worker.csv')
channel=pd.read_csv(base+'dim_channel.csv')
market=pd.read_csv(base+'dim_market.csv')
date=pd.read_csv(base+'dim_date_updated.csv')
df=fact.merge(worker,on='worker_id',how='left').merge(channel,on='channel_id',how='left').merge(market,on='market_id',how='left').merge(date,on='date_id',how='left')
df['full_date']=pd.to_datetime(df['full_date'],format='%m/%d/%Y')
df['ym']=df['full_date'].dt.to_period('M').astype(str)
out='/home/claude/analysis/charts/'

# 1. Monthly fraud rate trend with 95% CI band
m = df.groupby('ym')['is_fraud_flagged'].agg(['mean','count'])
m['se']=np.sqrt(m['mean']*(1-m['mean'])/m['count'])
fig,ax=plt.subplots(figsize=(10,4.5))
x=range(len(m))
ax.plot(x,m['mean']*100,color=NAVY,lw=2,marker='o',ms=4,label='Monthly fraud rate')
ax.fill_between(x,(m['mean']-1.96*m['se'])*100,(m['mean']+1.96*m['se'])*100,color=NAVY,alpha=0.15,label='95% CI')
overall=df['is_fraud_flagged'].mean()*100
ax.axhline(overall,color=CORAL,ls='--',lw=1.5,label=f'Overall mean ({overall:.1f}%)')
ax.set_xticks(x); ax.set_xticklabels(m.index,rotation=45,ha='right',fontsize=8)
ax.set_ylabel('Fraud-flagged rate (%)')
ax.set_title('Monthly Fraud Rate: No Trend or Seasonality — Fluctuates Randomly Around 50%',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'01_monthly_fraud_rate.png',dpi=150); plt.close()

# 2. Fraud rate by channel_type with CI - not sig
g = df.groupby('channel_type')['is_fraud_flagged'].agg(['mean','count']).sort_values('mean')
g['se']=np.sqrt(g['mean']*(1-g['mean'])/g['count'])
fig,ax=plt.subplots(figsize=(8,4.5))
y=range(len(g))
ax.barh(y,g['mean']*100,xerr=g['se']*196,color=TEAL,alpha=0.85,capsize=4)
ax.axvline(overall,color=CORAL,ls='--',lw=1.5,label=f'Overall mean ({overall:.1f}%)')
ax.set_yticks(y); ax.set_yticklabels(g.index)
ax.set_xlabel('Fraud-flagged rate (%)')
ax.set_title('Fraud Rate by Channel Type — Differences Fall Within Noise (χ² p=0.13)',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'02_fraud_by_channel.png',dpi=150); plt.close()

# 3. Fraud rate by country
g = df.groupby('country')['is_fraud_flagged'].agg(['mean','count']).sort_values('mean')
g['se']=np.sqrt(g['mean']*(1-g['mean'])/g['count'])
fig,ax=plt.subplots(figsize=(8,4))
y=range(len(g))
ax.barh(y,g['mean']*100,xerr=g['se']*196,color=NAVY,alpha=0.85,capsize=4)
ax.axvline(overall,color=CORAL,ls='--',lw=1.5,label=f'Overall mean ({overall:.1f}%)')
ax.set_yticks(y); ax.set_yticklabels(g.index)
ax.set_xlabel('Fraud-flagged rate (%)')
ax.set_title('Fraud Rate by Country — Not Statistically Distinguishable (χ² p=0.51)',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'03_fraud_by_country.png',dpi=150); plt.close()

# 4. Fraud rate by tenure bucket
df['tenure_bucket']=pd.cut(df.account_tenure_days,[-1,90,365,730,1095,1460,1825],
    labels=['0-90d\n(new)','91-365d','1-2yr','2-3yr','3-4yr','4-5yr'])
g=df.groupby('tenure_bucket',observed=True)['is_fraud_flagged'].agg(['mean','count'])
g['se']=np.sqrt(g['mean']*(1-g['mean'])/g['count'])
fig,ax=plt.subplots(figsize=(8,4.5))
x=range(len(g))
ax.bar(x,g['mean']*100,yerr=g['se']*196,color=GOLD,alpha=0.9,capsize=4,edgecolor=NAVY)
ax.axhline(overall,color=CORAL,ls='--',lw=1.5,label=f'Overall mean ({overall:.1f}%)')
ax.set_xticks(x); ax.set_xticklabels(g.index)
ax.set_ylabel('Fraud-flagged rate (%)')
ax.set_title('Fraud Rate by Account Tenure — New Accounts Are NOT Higher Risk Here',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'04_fraud_by_tenure.png',dpi=150); plt.close()

# 5. Velocity score vs fraud flag - scatter/density showing no separation
fig,ax=plt.subplots(figsize=(8,4.5))
for flag,color,lbl in [(False,TEAL,'Not fraud-flagged'),(True,CORAL,'Fraud-flagged')]:
    sub=df[df.is_fraud_flagged==flag]['velocity_score']
    ax.hist(sub,bins=40,alpha=0.5,color=color,label=lbl,density=True)
ax.set_xlabel('Velocity score'); ax.set_ylabel('Density')
ax.set_title(f'Velocity Score Distribution by Fraud Flag — Correlation r={df["velocity_score"].corr(df["is_fraud_flagged"].astype(int)):.4f}',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'05_velocity_vs_fraud.png',dpi=150); plt.close()

# 6. Dispute rate by gig segment
g=df.groupby('gig_segment')['is_disputed'].agg(['mean','count']).sort_values('mean')
g['se']=np.sqrt(g['mean']*(1-g['mean'])/g['count'])
fig,ax=plt.subplots(figsize=(9,6))
y=range(len(g))
ax.barh(y,g['mean']*100,xerr=g['se']*196,color=BLUE,alpha=0.85,capsize=3)
d_overall=df['is_disputed'].mean()*100
ax.axvline(d_overall,color=CORAL,ls='--',lw=1.5,label=f'Overall mean ({d_overall:.1f}%)')
ax.set_yticks(y); ax.set_yticklabels(g.index,fontsize=9)
ax.set_xlabel('Dispute rate (%)')
ax.set_title('Dispute Rate by Gig Segment (χ² p=0.06)',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'06_dispute_by_segment.png',dpi=150); plt.close()

# 7. Month-end vs non month-end: cash-out and reversal rates
mm = df.groupby('is_month_end').agg(cashout_rate=('transaction_type', lambda s:(s=='Cash-Out').mean()),
                                       reversal_rate=('is_reversed','mean'))
mm.index=['Regular days','Month-end days']
fig,ax=plt.subplots(figsize=(7,4.5))
xw=np.arange(2); width=0.35
ax.bar(xw-width/2, mm['cashout_rate']*100, width, label='Cash-out share of txns', color=NAVY)
ax.bar(xw+width/2, mm['reversal_rate']*100, width, label='Reversal rate', color=CORAL)
ax.set_xticks(xw); ax.set_xticklabels(mm.index)
ax.set_ylabel('%')
ax.set_title('Month-End vs Regular Days — No Meaningful Spike Detected',fontsize=12,fontweight='bold',loc='left')
ax.legend(frameon=False,fontsize=9)
plt.tight_layout(); plt.savefig(out+'07_monthend_effect.png',dpi=150); plt.close()

# 8. Transaction type volume & value
g=df.groupby('transaction_type').agg(count=('transaction_id','count'),total_usd=('amount_usd','sum')).sort_values('total_usd')
fig,ax=plt.subplots(figsize=(9,6))
y=range(len(g))
ax.barh(y,g['total_usd']/1e6,color=TEAL)
ax.set_yticks(y); ax.set_yticklabels(g.index,fontsize=9)
ax.set_xlabel('Total value (USD millions)')
ax.set_title('Transaction Value by Type — Evenly Distributed Across 13 Types',fontsize=12,fontweight='bold',loc='left')
plt.tight_layout(); plt.savefig(out+'08_value_by_type.png',dpi=150); plt.close()

# 9. Correlation heatmap
import seaborn as sns
numcols=['amount_usd','velocity_score','fraud_loss_usd','processing_time_ms','account_tenure_days','risk_score']
tmp=df[numcols+['is_fraud_flagged','is_disputed','is_reversed']].copy()
for c in ['is_fraud_flagged','is_disputed','is_reversed']:
    tmp[c]=tmp[c].astype(int)
corr=tmp.corr()
fig,ax=plt.subplots(figsize=(8,6.5))
sns.heatmap(corr,annot=True,fmt='.2f',cmap='RdBu_r',center=0,vmin=-0.3,vmax=0.3,ax=ax,cbar_kws={'label':'Pearson r'})
ax.set_title('Correlation Matrix — Near-Zero Except the Mechanical Loss/Flag Pair',fontsize=11.5,fontweight='bold',loc='left')
plt.tight_layout(); plt.savefig(out+'09_correlation_heatmap.png',dpi=150); plt.close()

# 10. Fraud loss by country (dollar exposure - real magnitude even if rate is flat)
g=df.groupby('country').agg(fraud_loss=('fraud_loss_usd','sum'),total_value=('amount_usd','sum')).sort_values('fraud_loss')
fig,ax=plt.subplots(figsize=(8,4))
y=range(len(g))
ax.barh(y,g['fraud_loss']/1e6,color=CORAL,alpha=0.85)
ax.set_yticks(y); ax.set_yticklabels(g.index)
ax.set_xlabel('Total fraud loss exposure (USD millions)')
ax.set_title('Fraud Loss Exposure by Country — Near-Identical (Proportional to Volume)',fontsize=11.5,fontweight='bold',loc='left')
plt.tight_layout(); plt.savefig(out+'10_fraud_loss_by_country.png',dpi=150); plt.close()

print("Charts created:")
import os
for f in sorted(os.listdir(out)): print(" -",f)
