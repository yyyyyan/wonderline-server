import tripGetters from '../trip/getters'
import tripActions from '../trip/actions'
import httpProcessor from '../utils/http-processor'

class TripProcessor {
    getTripNumber(req, res) {
        tripGetters.getTripNumber()
            .then(data => httpProcessor.sendGenericGetSuccessRes(req, res, data),
                err => httpProcessor.sendGenericGetFailureRes(req, res, err))
    }
    postTripNumber(req, res) {
        tripActions.addTripNumber()
            .then(() => httpProcessor.sendGenericPostSuccessRes(req, res),
                err => httpProcessor.sendGenericPostFailureRes(req, res, err))
    }
    getTrip(req, res) {
        tripGetters.getTrip(req.params.id)
            .then(data => httpProcessor.sendGenericGetSuccessRes(req, res, data),
                err => httpProcessor.sendGenericGetFailureRes(req, res, err))
    }
    getPhotos(req, res) {
        tripGetters.getPhotos(req.params.id)
            .then(data => httpProcessor.sendGenericGetSuccessRes(req, res, data),
                err => httpProcessor.sendGenericGetFailureRes(req, res, err))
    }
    getPhotoComments(req, res) {
        tripGetters.getPhotoComments(req.params.id, req.params.pid)
            .then(data => httpProcessor.sendGenericGetSuccessRes(req, res, data),
                err => httpProcessor.sendGenericGetFailureRes(req, res, err))
    }
}

export default new TripProcessor()