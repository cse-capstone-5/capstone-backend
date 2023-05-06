const express = require('express')
const { spawn } = require('child_process')
const iconv = require('iconv-lite');
const app = express()
const port = 5000

//캐시용
let cache = {}

async function getData(keyword) {
    // 자식 프로세스 생성 sentimeter.py 실행하고 argv로 keyword 보냄
    const result = spawn('conda', ['run', "-n", "pororo", "python", "sentimeter.py", keyword])

    //https://stackoverflow.com/questions/58570325/how-to-turn-child-process-spawns-promise-syntax-to-async-await-syntax
    let data = "";
    for await (const chunk of result.stdout) {
        data += chunk;
    }
    // python 실행 결과 나오면 한글로 변환후 
    //https://validming99.tistory.com/117 한글 깨짐 참고
    let encoded = data.toString('utf8');
    // let result = iconv.decode(data, 'euc-kr')
    console.log(encoded);
    cache[keyword] = JSON.parse(encoded)

    result.stderr.on('data', function (data) {
        let encoded = data.toString('utf8');
        console.log(encoded);
    });

}

// keyword
app.get('/keyword/:keyword', async (req, res) => {
    if (!cache[req.params.keyword]) {
        //캐시 안에 없다면 파이썬 돌림
        await getData(req.params.keyword)
    }
    console.log("keyword " + Object.keys(cache))
    res.send(cache[req.params.keyword])
})

// article
app.get('/article/keyword/:keyword', async (req, res) => {
    if (!cache[req.params.keyword]) {
        //캐시 안에 없다면 파이썬 돌림
        await getData(req.params.keyword)
    }
    console.log("article " + Object.keys(cache))
    res.send({ "result": cache[req.params.keyword]['article'] })
})


// word-cloud
app.get('/word-cloud/keyword/:keyword', async (req, res) => {
    if (!cache[req.params.keyword]) {
        //캐시 안에 없다면 파이썬 돌림
        await getData(req.params.keyword)
    }
    console.log("word-cloud " + Object.keys(cache))
    res.send({ "result": cache[req.params.keyword]['wordCloud'] })
})

// line-chart
app.get('/line-chart/keyword/:keyword', async (req, res) => {
    if (!cache[req.params.keyword]) {
        //캐시 안에 없다면 파이썬 돌림
        await getData(req.params.keyword)
    }
    console.log("line-chart " + Object.keys(cache))
    res.send({ "result": cache[req.params.keyword]['lineChart'] })
})

// 접속 확인용
app.get('/', (req, res) => {
    res.send('캡스톤 5조 백엔드 서버입니다.')
})

app.listen(port, () => {
    console.log(`app listening on port ${port}`)
})