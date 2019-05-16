import dbReader from '../utils/db-reader'
import tripUtil from './utils'
import userGetters from '../user/getters'

class Getters {
    async getTripNumber() {
        const dataCounter = await dbReader.readDataCounter()
        return dataCounter.tripNb
    }
    async getTrip(tripId) {
        const trip = await dbReader.readTrip(tripId)
        trip.users = await Promise.all(trip.users.map(async id => {
            return userGetters.getReducedUser(id)
        }))
        trip.dailyInfos =
            tripUtil.generateDailyInfosWithCoverPhotos(trip.dailyInfos, await dbReader.readTripPhotos(tripId))
        return trip
    }
    // TODO Find a way to avoid code duplication
    async getReducedTrip(tripId) {
        const trip = await dbReader.readTrip(tripId)
        trip.users = await Promise.all(trip.users.map(async id => {
            return userGetters.getReducedUser(id)
        }))
        const photos = await dbReader.readTripPhotos(tripId)
        trip.coverPhoto = photos[trip.coverPhotoId]
        trip.coverPhoto.src = tripUtil.generateCompletePhotoSrc(trip.coverPhoto.src)
        return tripUtil.generateReducedTrip(trip)
    }
    async getPhotos(tripId) {
        return tripUtil.generatePhotosWithCompleteSrc(await dbReader.readTripPhotos(tripId))
    }
    async getPhotoNb(tripId) {
        const trip = await dbReader.readTrip(tripId)
        return trip.photoNb
    }
    async getPhotoComments(tripId, photoId) {
        const comments = await dbReader.readTripComments(tripId)
        if (!comments || !comments[photoId])
            return null
        return Promise.all(comments[photoId].map(async comment => {
            return tripUtil.generateCommentWithUserInfo(comment, await userGetters.getUser(comment.userId))
        }))
    }
}
export default new Getters()