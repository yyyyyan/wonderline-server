import httpConfig from '../../configs/http-config'

class HttpProcessor {
    sendGenericGetSuccessRes(res, data) {
        return res.status(httpConfig.GET_SUCCESS_CODE).send({success: 'true', payload: data})
    }
    sendGenericGetFailureRes(res, err) {
        console.log(`[Http Processor] GET failed: ${err}`)
    }
    sendWrongGetQueryRes(res) {
        this.sendGenericGetFailureRes(res, 'Wrong query')
    }
    sendGenericPostSuccessRes(res, data) {
        return res.status(httpConfig.POST_SUCCESS_CODE).send({success: 'true', payload: data})
    }
    sendGenericPostFailureRes(res, err) {
        console.log(`[Http Processor] POST failed: ${err}`)
    }
    sendWrongPostQueryRes(res) {
        this.sendGenericPostFailureRes(res, 'Wrong query')
    }
    sendWrongPostDataRes(res) {
        this.sendGenericPostFailureRes(res, 'Wrong data')
    }
}

export default new HttpProcessor()