import httpConfig from '../../configs/http-config'

class HttpProcessor {
    sendGenericGetSuccessRes(req, res, data) {
        return res.status(httpConfig.GET_SUCCESS_CODE).send({success: 'true', payload: data})
    }
    sendGenericGetFailureRes(req, res, err) {
        console.log(`[Http Processor] GET failed: ${err}`)
    }
    sendGenericPostSuccessRes(req, res) {
        return res.status(httpConfig.POST_SUCCESS_CODE).send({success: 'true'})
    }
    sendGenericPostFailureRes(req, res, err) {
        console.log(`[Http Processor] POST failed: ${err}`)
    }
}

export default new HttpProcessor()