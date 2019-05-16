import userGetters from '../user/getters'
import userActions from '../user/actions'
import httpProcessor from '../utils/http-processor'

class UserProcessor {
    getUserNumber(req, res) {
        userGetters.getUserNumber()
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    getUser(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongGetQueryGet(res)
        userGetters.getUser(req.query.id)
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
}

export default new UserProcessor()