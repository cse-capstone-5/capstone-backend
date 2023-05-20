const express = require('express')
const { spawn } = require('child_process')
const cors = require('cors')
const app = express()
const port = 5001

app.use(cors({ origin: '*' }))

async function getData(keyword, ds, de, limit) {
    const result = spawn('python', ["fast_sentimeter.py", keyword, ds, de, limit])

    //https://stackoverflow.com/questions/58570325/how-to-turn-child-process-spawns-promise-syntax-to-async-await-syntax
    let error = ""
    for await (const chunk of result.stderr) {
        error += chunk
    }

    let data = "";
    for await (const chunk of result.stdout) {
        data += chunk;
    }
    // python 실행 결과 나오면 한글로 변환후 
    //https://validming99.tistory.com/117 한글 깨짐 참고
    let encoded = data.toString('utf8');

    const exitCode = await new Promise((resolve, reject) => {
        result.on('close', resolve)
    })

    if (exitCode) {
        return { status: 0, result: exitCode + error }
    } else {
        return { status: 1, result: encoded }
    }

}

// keyword
app.get('/keyword/:keyword/ds/:ds/de/:de/limit/:limit', async (req, res) => {
    const result = await getData(req.params.keyword, req.params.ds, req.params.de, req.params.limit)

    if (result.status == 0) {
        res.status(500).send(`server error! ${result.result}`)
    }
    else {
        res.send(result.result)
    }
})

// 접속 확인용
app.get('/', (req, res) => {
    res.send('캡스톤 5조 백엔드 서버입니다.')
})

app.listen(port, () => {
    console.log(`app listening on port ${port}`)
})