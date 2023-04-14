# capstone-backend

## 실행 방법

1. npm i
2. node index.js

## pororo 설치

1. conda 설치
2. 콘다 설치후 콘다 내부에서
   `conda create -n pororo_test python=3.8`
   `conda activate pororo_test`
   `conda install pytorch==1.6.0 torchvision==0.7.0 cudatoolkit=10.1 -c pytorch`
   `pip install pororo`
   또는 `pip install -i http://ftp.daumkakao.com/pypi/simple --trusted-host ftp.daumkakao.com pororo`
3. 다른 의존성 설치
   `pip install bs4 matplotlib pandas plotly aiohttp nest_asyncio konlpy`

## 리눅스에서 배포 방법

1. npm i pm2 -g
2. [리눅스에서 conda 실행](https://dambi-ml.tistory.com/6)
3. pm2 start index.js

[깃헙 개같은 push 오류 해결 방법](https://data-jj.tistory.com/49)
