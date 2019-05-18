import userGetters from '../user/getters'
import userActions from '../user/actions'
import httpProcessor from '../utils/http-processor'
import msgConfig from '../../configs/msg-config'

class UserProcessor {
    getUserNumber(req, res) {
        userGetters.getUserNumber()
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    getLoginUser(req, res) {
        if (!req.query.email || !req.query.password) return httpProcessor.sendWrongGetQueryRes(res)
        userGetters.getLoginUser(req.query.email, req.query.password)
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    getUser(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongGetQueryRes(res)
        userGetters.getUser(req.query.id)
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    postNewUser(req, res) {
        const user = req.body.user
        if (!user.name || !user.email || !user.password) return httpProcessor.sendWrongPostDataRes(res)
        userActions.createUser(user)
            .then(data => httpProcessor.sendGenericPostSuccessRes(res, data, msgConfig.POST_USER_SUCCESS))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
}

export default new UserProcessor()