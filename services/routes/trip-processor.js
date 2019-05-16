import tripGetters from '../trip/getters'
import tripActions from '../trip/actions'
import httpProcessor from '../utils/http-processor'

class TripProcessor {
    getTripNumber(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongGetQueryRes(res)
        tripGetters.getTripNumber()
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    getTrip(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongGetQueryRes(res)
        tripGetters.getTrip(req.query.id)
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    getPhotos(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongGetQueryRes(res)
        tripGetters.getPhotos(req.query.id)
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    getPhotoComments(req, res) {
        if (!req.query.id || !req.query.photoId) return httpProcessor.sendWrongGetQueryRes(res)
        tripGetters.getPhotoComments(req.query.id, req.query.photoId)
            .then(data => httpProcessor.sendGenericGetSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericGetFailureRes(res, err))
    }
    postSummary(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongPostQueryRes(res)
        if (!req.body.summary) return httpProcessor.sendWrongPostDataRes(res)
        tripActions.updateSummary(req.query.id, req.body.summary)
            .then(data => httpProcessor.sendGenericPostSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericPostFailureRes(res, err))
    }
    postPhotos(req, res) {
        if (!req.query.id) return httpProcessor.sendWrongPostQueryRes(res)
        if (!req.files) return httpProcessor.sendWrongPostDataRes(res)
        tripActions.generatePhotosFromFiles(req.query.id, req.files)
            .then(photos => tripActions.addPhotos(req.query.id, photos, req.query.ownerId))
            .then(data => httpProcessor.sendGenericPostSuccessRes(res, data))
            .catch(err => httpProcessor.sendGenericPostFailureRes(res, err))
    }
}

export default new TripProcessor()