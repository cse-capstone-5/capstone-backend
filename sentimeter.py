# %%
from bs4 import BeautifulSoup as bs
import requests
import re
import datetime
from tqdm import tqdm
import sys
from pororo import Pororo
from dateutil.relativedelta import relativedelta
import pandas as pd
import asyncio
import aiohttp
import nest_asyncio
from konlpy.tag import Okt
from collections import Counter
import time
from wordcloud import WordCloud
import json
import warnings
warnings.filterwarnings("ignore")

# %%
def get_sent(txt):
    return sent(txt,show_probs=True)['positive']-0.5

# %%
def get_noun(txt):
    return okt.nouns(txt)

# %%
def split_sentence(txt):
    txt = txt.split(' ')
    txt = [t for t in txt if t]
    return txt

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
    sent_data = []
    dif = relativedelta(days=int(date_scale))
    while(ds<de):
        sent_data.append(date_to_str(ds))
        ds = ds+dif
        if(ds>=de):
            result.append(date_to_str(de))
    return result

# %%
def erase_tag(txt):
    pattern = '<[^>]*>'
    txt = re.sub(pattern, repl='', string=str(txt))
    return txt

# %%
def clean_txt(txt):
    pattern = '[^ㄱ-ㅎㅏ-ㅣ가-힣0-9\s]'
    txt = re.sub(pattern, repl=' ', string=str(txt))
    pattern = '\s+'
    txt = re.sub(pattern,repl=' ',string=str(txt))
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
    async with aiohttp.ClientSession() as sess: # aiohttp를 사용하여 비동기적으로 세션을 생성합니다.
        for p in range(int(limit_per_day/10)): # 페이지 수 만큼 반복합니다.
            url = 'https://search.naver.com/search.naver?where=news&query={0}&pd=3&ds={1}&de={2}&start={3}'.format(keyword,day,day,p*10) # 검색어, 날짜, 페이지 번호를 이용하여 url을 생성합니다.
            async with sess.get(url,headers={'user-agent': 'Mozilla/5.0'}) as html: # 생성한 url로 get 요청을 보냅니다.
                html = await html.text() # 응답받은 html을 text로 변환합니다.
                try:
                    html = html[html.index('class="list_news"'):html.index('class="banner_area"')] # 뉴스 리스트가 있는 부분만 추출합니다.
                except:
                    continue # 뉴스 리스트가 없으면 다음 페이지로 넘어갑니다.
                html = bs(html,"lxml") # 추출한 html을 bs4로 파싱합니다.
                article_info = html.select("li div.news_area > a")
                titles = [t.attrs['title'] for t in article_info] # 뉴스 제목만 추출합니다.
                urls = [u.attrs['href'] for u in article_info] 
                num_res = len(titles) # 추출한 뉴스 수를 저장합니다.
                
                tmp = [[t,u] for t,u in zip(titles,urls) if keyword in t]
                titles,urls = [],[]

                for t in tmp:
                    titles.append(t[0])
                    urls.append(t[1])

                raw_df = pd.DataFrame({'title':titles,'url':urls,'date':day}) # 추출한 뉴스 제목과 날짜를 데이터프레임으로 생성합니다.
                global news_data
                news_data = pd.concat([raw_df,news_data],ignore_index=True) # 추출한 데이터프레임을 전역 변수 dataset에 추가합니다.
                if(num_res != 10 or len(titles)==0): # 추출한 뉴스 수가 10개가 아니거나 검색어가 포함된 뉴스가 없으면 반복문을 종료합니다.
                    #print("end of articles")
                    break

# %%
async def async_crawl(keyword,ds,de):
    day_list = pd.date_range(ds,de)
    day_list = [date_to_str(d) for d in day_list]

    task = [get_text(keyword,d)for d in day_list]
    await (asyncio.wait(task))

# %%
def word_cloud(df):
    word = sum(df['split'],[])
    vocab = Counter(word)
    vocab = vocab.most_common(vocab_size)
    wc = {"wordCloud" : dict(vocab)}
    return json.dumps(wc)

# %%
def get_article():
    sent_data['num_diff'] = sent_data['sent_val']
    sent_data['sent_diff'] = sent_data['sent_val'].diff()
    sent_data['sent_diff'] = sent_data['sent_diff'].apply(abs)
    posmax = sent_data['num_diff'].max()
    posday = sent_data.loc[sent_data['num_diff']==posmax]['sent_val'].idxmax()
    negmax = sent_data['num_diff'].min()
    negday = sent_data.loc[sent_data['num_diff']==negmax]['sent_val'].idxmax()
    repday = sent_data['sent_diff'].idxmax()
    days = [repday,posday,negday]
    articles = {}
    
    for d in days:
        tmp=get_represent(news_data.loc[news_data['date'] == d])
        articles[tmp['title']]=tmp['url']
        
    return list(articles.items())

# %%
def get_represent(df):
    word = sum(df['split'],[])
    vocab = Counter(word)
    vocab = vocab.most_common(vocab_size)
    word_idx = {}
    i = 1
    for (word,freq) in vocab:
        word_idx[word] = i
        i=i+1
    
    for idx in df.index:
        val = 0
        for w in df.loc[idx,'split']:
            if w in word_idx:
                val = val + word_idx[w]
            else:
                val = val + len(word_idx)
        val = val/len(df.loc[idx,'split'])
        df.loc[idx,'represent'] = val
    
    return df.loc[df['represent'].idxmin()]

# %%
def get_linechart():
    lineChart = []
    for row in sent_data.itertuples():
        tmp = {"name":str(row[0]),"count":row[3]}
        lineChart.append(tmp)
    return lineChart

# %%
async def crawl_sent_analysis(keyword):
    #print("crawling")
    await async_crawl(keyword,ds,de)
    news_data['date'] = pd.to_datetime(news_data['date'])
    #print("cleaning text")
    news_data['title'] = news_data['title'].apply(clean_txt)
    #print("split sentence")
    news_data['split'] = news_data['title'].apply(split_sentence)
    #print("sentment analysis")
    news_data['sent_val'] = news_data['title'].apply(get_sent)
    #print("done")
    
    global sent_data
    sent_data = news_data.resample(on='date',rule='D').sum()
    #sent_data = sent_data.fillna(0)

    for d in sent_data['sent_val'].index:
        plist = (news_data['sent_val']>=0)&(news_data['date']==d)
        nlist = (news_data['sent_val']<0)&(news_data['date']==d)
        sent_data.loc[d,'npos'] = plist.sum()
        sent_data.loc[d,'nneg'] = nlist.sum()
        sent_data.loc[d,'pos'] = news_data[plist]['sent_val'].sum()
        sent_data.loc[d,'neg'] = news_data[nlist]['sent_val'].sum()
    sent_data['diff'] = sent_data['sent_val'].diff()

    result = {}
    result["article"] = get_article()
    result["wordCloud"] = word_cloud(news_data)
    result["lineChart"] = get_linechart()
    print(json.dumps(result,ensure_ascii = False))

# %%
#sent = Pororo(task="sentiment", model="brainbert.base.ko.nsmc", lang="ko")
sent = Pororo(task="sentiment", model="brainbert.base.ko.shopping", lang="ko")
okt = Okt()
limit_per_day = 10
vocab_size = 100
news_data = pd.DataFrame(columns=['title','url','date','sent_val'])
sent_data = pd.DataFrame()
#keyword = "전세"
ds = str_to_date('20230401')
de = str_to_date('20230501')

# %%
if __name__ == '__main__':
    #await crawl_sent_analysis(sys.argv[1])
    asyncio.run(crawl_sent_analysis(sys.argv[1]))


