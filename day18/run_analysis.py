import pandas as pd, numpy as np
import os
os.chdir('/Users/macbookpro/Desktop/股')

df = pd.read_csv('data/茅台.csv')
df['日期'] = pd.to_datetime(df['日期'])
df = df.set_index('日期').sort_index()

N, k = 20, 2
df['BB_Mid'] = df['收盘'].rolling(N).mean()
df['BB_Std'] = df['收盘'].rolling(N).std(ddof=0)
df['BB_Up'] = df['BB_Mid'] + k * df['BB_Std']
df['BB_Lo'] = df['BB_Mid'] - k * df['BB_Std']

last_N = df['收盘'].iloc[-N:]
middle = last_N.mean()
std = last_N.std(ddof=0)
upper = middle + k * std
lower = middle - k * std

print('=== 1.手算布林带 ===')
print(f'中轨={middle:.2f} 标准差={std:.2f}')
print(f'上轨={upper:.2f} 下轨={lower:.2f}')
print(f'当前收盘={df["收盘"].iloc[-1]:.2f} 带宽={upper-lower:.2f}')

df['BB_%B'] = (df['收盘'] - df['BB_Lo']) / (df['BB_Up'] - df['BB_Lo'])
df['BB_BW'] = (df['BB_Up'] - df['BB_Lo']) / df['BB_Mid']
print(f'%B={df["BB_%B"].iloc[-1]:.3f} 带宽%={df["BB_BW"].iloc[-1]*100:.1f}')
sq = df['BB_BW'].quantile(0.2)
print(f'挤压阈值={sq*100:.1f}% 是否挤压={"是" if df["BB_BW"].iloc[-1]<sq else "否"}')

df['Vol_MA5'] = df['成交量'].rolling(5).mean()
df['量比'] = df['成交量'] / df['Vol_MA5']
df['放量'] = df['量比'] > 1.5
df['缩量'] = df['量比'] < 0.5
df['涨'] = df['收盘'] > df['收盘'].shift(1)
df['跌'] = df['收盘'] < df['收盘'].shift(1)

print()
print('=== 2.量价四象限 ===')
print(f'总交易日:{len(df)} 放量日:{df["放量"].sum()} 缩量日:{df["缩量"].sum()}')
for l,c in [('涨+放量',df['涨']&df['放量']),('涨+缩量',df['涨']&df['缩量']),
            ('跌+放量',df['跌']&df['放量']),('跌+缩量',df['跌']&df['缩量'])]:
    rets=[(df['收盘'].iloc[df.index.get_loc(d)+5]/df['收盘'].iloc[df.index.get_loc(d)]-1)*100
          for d in df[c].index if df.index.get_loc(d)+5<len(df)]
    if rets: print(f'{l}: {c.sum()}天 | 5天后涨{sum(r>0 for r in rets)}/{len(rets)} | 均值{np.mean(rets):.2f}%')

df['碰下轨']=(df['收盘']<=df['BB_Lo']*1.02)&(df['收盘']>=df['BB_Lo']*0.98)
print()
print('=== 3.碰轨验证 ===')
d120=df.iloc[-120:]
print(f'近120天碰下轨:{d120["碰下轨"].sum()}次')
for l,c in [('下轨+放量',df['碰下轨']&df['放量']),('下轨+缩量',df['碰下轨']&df['缩量'])]:
    rets=[(df['收盘'].iloc[df.index.get_loc(d)+5]/df['收盘'].iloc[df.index.get_loc(d)]-1)*100
          for d in df[c].index if df.index.get_loc(d)+5<len(df)]
    if rets: print(f'{l}: 涨{sum(r>0 for r in rets)}/{len(rets)} 均值{np.mean(rets):.2f}%')

print()
print('=== 4.三股对比 ===')
for n,p in [('茅台','茅台'),('招商银行','招商银行'),('比亚迪','比亚迪')]:
    s=pd.read_csv(f'data/{p}.csv'); s['日期']=pd.to_datetime(s['日期']); s=s.set_index('日期').sort_index()
    m=s['收盘'].rolling(20).mean(); st=s['收盘'].rolling(20).std(ddof=0)
    up=m+2*st; lo=m-2*st; bb=(s['收盘']-lo)/(up-lo); bw=(up-lo)/m
    print(f'{n}: 收盘{s["收盘"].iloc[-1]:.2f} | %B={bb.iloc[-1]:.3f} | 带宽={bw.iloc[-1]*100:.1f}%')
