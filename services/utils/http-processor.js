import httpConfig from '../../configs/http-config'
import msgConfig from '../../configs/msg-config'

class HttpProcessor {
    sendGenericGetSuccessRes(res, data) {
        return res.status(httpConfig.GET_SUCCESS_CODE).send({success: 'true', payload: data})
    }
    sendGenericGetFailureRes(res, err) {
        console.log(`[Http Processor] GET failed: ${err}`)
        return res.status(httpConfig.GET_SUCCESS_CODE).send({success: 'false', msg: err})
    }
    sendWrongGetQueryRes(res) {
        this.sendGenericGetFailureRes(res, msgConfig.GET_WRONG_QUERY)
    }
    sendGenericPostSuccessRes(res, data, msg) {
        return res.status(httpConfig.POST_SUCCESS_CODE).send({success: 'true', payload: data, msg: msg})
    }
    sendGenericPostFailureRes(res, err) {
        console.log(`[Http Processor] POST failed: ${err}`)
        return res.status(httpConfig.POST_SUCCESS_CODE).send({success: 'false', msg: err})
    }
    sendWrongPostQueryRes(res) {
        this.sendGenericPostFailureRes(res, msgConfig.POST_WRONG_QUERY)
    }
    sendWrongPostDataRes(res) {
        this.sendGenericPostFailureRes(res, msgConfig.POST_WRONG_DATA)
    }
}

export default new HttpProcessor()