import express from 'express'
import bodyParser from 'body-parser'
import router from './services/routes'
import httpConfig from './configs/http-config'
const cors = require('cors')

const app = express()
app.use(cors())
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: false }))
app.use(express.static('public'))
app.use(router)

app.listen(httpConfig.SERVER_PORT, () => {
    console.log(`Server running on localhost: ${httpConfig.SERVER_PORT}`)
})