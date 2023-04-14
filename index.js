const express = require('express')
const { spawn } = require('child_process')
const iconv = require('iconv-lite');
const app = express()
const port = 5000

app.get('/word-cloud/keyword/:keyword', (req, res) => {
    console.log(req.params)
    const result = spawn('python', ['test.py', req.params.keyword])

    result.stdout.on('data', function (data) {
        let result = iconv.decode(data, 'euc-kr')
        console.log(result);
        res.send(`wordcount ${JSON.stringify(req.params)} ${result}`)
    });

    result.stderr.on('data', function (data) {
        let result = iconv.decode(data, 'euc-kr')
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