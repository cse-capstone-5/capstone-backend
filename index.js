const express = require('express')
const { spawn } = require('child_process')
const iconv = require('iconv-lite');
const app = express()
const port = 5000

// word-cloud
app.get('/word-cloud/keyword/:keyword', (req, res) => {
    console.log(req.params)

    // 자식 프로세스 생성 test.py 실행하고 argv로 url에서 keyword 받은것 보냄
    const result = spawn('conda', ['run', "-n", "pororo", "python", "test.py", req.params.keyword])

    // python 실행 결과 나오면 한글로 변환후 
    //https://validming99.tistory.com/117 한글 깨짐 참고
    result.stdout.on('data', function (data) {
        let result = data.toString('utf8');
        // let result = iconv.decode(data, 'euc-kr')
        console.log(result);
        res.send(`${result}`)
    });

    result.stderr.on('data', function (data) {
        let result = data.toString('utf8');
        console.log(result);
        res.status(500)
        res.send('Server Error!')
    });


})

app.get('/line-chart/keyword/:keyword/interval/:timeInterval/start/:startDate/end/:endDate', (req, res) => {
    console.log(req.params)
    res.send(`line-chart ${JSON.stringify(req.params)}`)
})

app.listen(port, () => {
    console.log(`app listening on port ${port}`)
})