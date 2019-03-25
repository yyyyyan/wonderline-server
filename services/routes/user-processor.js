import userGetters from '../user/getters'
import userActions from '../user/actions'
import httpProcessor from '../utils/http-processor'

class UserProcessor {
    getUserNumber(req, res) {
        userGetters.getUserNumber()
            .then((data) => httpProcessor.sendGenericGetSuccessRes(req, res, data),
                (err) => httpProcessor.sendGenericGetFailureRes(req, res, err))
    }
    postUserNumber(req, res) {
        userActions.addUserNumber()
            .then(() => httpProcessor.sendGenericPostSuccessRes(req, res),
                (err) => httpProcessor.sendGenericPostFailureRes(req, res, err))
    }
}

export default new UserProcessor()