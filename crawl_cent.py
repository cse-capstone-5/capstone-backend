# %%
from bs4 import BeautifulSoup as bs
import requests
import re
import datetime
from tqdm import tqdm
import sys
from pororo import Pororo
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import aiohttp
import nest_asyncio
from konlpy.tag import Okt
import time

#뷰어 링크
#https://nbviewer.org/gist/r3nas/e77d37a1e88d6dfcffc6dc78b0275d80
# %%
#sent = Pororo(task="sentiment", model="brainbert.base.ko.nsmc", lang="ko")
sent = Pororo(task="sentiment", model="brainbert.base.ko.shopping", lang="ko")
okt = Okt()
page_limit = 1

# %%
def get_cent(txt):
    return sent(txt,show_probs=True)['positive']-0.5

# %%
def get_noun(txt):
    return okt.nouns(txt)

# %%
def str_to_date(d):
    today = datetime.datetime.now()
    d = re.sub("[^0-9]","",d)
    yy = int(d[0:4])
    mm = int(d[4:6])
    dd = int(d[6:8])
    result = datetime.datetime(yy,mm,dd)
    if (today<result):
        return today
    return result

# %%
def date_to_str(d):
    d = str(d)
    d = [d[:4],d[5:7],d[8:10]]
    d = ".".join(d)
    return d

# %%
def to_period(ds,de,date_scale):
    result = []
    dif = relativedelta(days=int(date_scale))
    while(ds<de):
        result.append(date_to_str(ds))
        ds = ds+dif
        if(ds>=de):
            result.append(date_to_str(de))
    return result

# %%
def clean_txt(txt):
    erase_tag = '<[^>]*>'
    txt = re.sub(pattern=erase_tag, repl='', string=str(txt))
    return txt

# %%
def date_cal(before):
    if(len(before) >= 7):
        return before
        
    today = datetime.datetime.now()
    before = before[:-2]

    num = re.findall("\d+",before)
    kor = re.findall("[가-힣]+",before)
    num = int(num[0])
    kor = kor[0]

    if(kor == '일'):
        dif = relativedelta(days=num)
        today = today - dif
    elif (kor == '시간'):
        today = today - datetime.timedelta(hours=num)
    else:
        today = today - datetime.timedelta(minutes=num)
    
    return (date_to_str(today))

# %%
async def get_text(keyword,day):
    async with aiohttp.ClientSession() as sess:
        for p in range(page_limit):
            url = 'https://search.naver.com/search.naver?where=news&query={0}&pd=3&ds={1}&de={2}&start={3}'.format(keyword,day,day,p*10)
            async with sess.get(url,headers={'user-agent': 'Mozilla/5.0'}) as html:
                html = await html.text()
                try:
                    html = html[html.index('class="list_news"'):html.index('class="banner_area"')]
                except:
                    continue
                html = bs(html,"lxml")
                raw_title = html.select("li div.news_area > a.news_tit")
                title = [t.attrs['title'] for t in raw_title]
                num_res = len(raw_title)

                title = [t.attrs['title'] for t in raw_title if keyword in t.attrs['title']]
                raw_df = pd.DataFrame({'title':title,'date':day})
                global dataset
                dataset = pd.concat([raw_df,dataset],ignore_index=True)
                if(num_res != 10 or len(title)==0):
                    #print("end of articles")
                    break

# %%
async def async_crawl(keyword,ds,de):
    day_list = pd.date_range(ds,de)
    day_list = [date_to_str(d) for d in day_list]

    task = [get_text(keyword,d)for d in day_list]
    await (asyncio.wait(task))

# %%
async def main():
    keyword = "신천지"
    ds = str_to_date('20200201')
    de = str_to_date('20200301')
    await async_crawl(keyword,ds,de)

    dataset['date'] = pd.to_datetime(dataset['date'])
    dataset['nouns'] = dataset['title'].apply(get_noun)
    dataset['cent_val'] = dataset['title'].apply(get_cent)

    global result
    result = dataset.resample(on='date',rule='D').sum()
    result = result.fillna(0)

    for d in result['cent_val'].index:
        plist = (dataset['cent_val']>=0)&(dataset['date']==d)
        nlist = (dataset['cent_val']<0)&(dataset['date']==d)
        result.loc[d,'npos'] = plist.sum()
        result.loc[d,'nneg'] = nlist.sum()
        result.loc[d,'pos'] = dataset[plist]['cent_val'].sum()
        result.loc[d,'neg'] = dataset[nlist]['cent_val'].sum()

# %%
dataset = pd.DataFrame(columns=['title','date','cent_val'])
result = pd.DataFrame()
asyncio.run(main())