import dbReader from '../utils/db-reader'
import dbWriter from '../utils/db-writer'
import tripGetters from './getters'
import tripUtil from './utils'
import mediaReader from '../utils/media-reader'
import mediaWriter from '../utils/media-writer'
import authenticator from '../utils/authenticator'
import msgConfig from '../../configs/msg-config'

class Actions {
    async addTripNumber() {
        const dataCounter = await dbReader.readDataCounter()
        dataCounter.tripNb = dataCounter.tripNb + 1
        return dbWriter.writeDataCounter(dataCounter)
    }
    async createTrip(userId) {
        const user = await dbReader.readUser(userId)
        if (!user) throw msgConfig
        const trip = tripUtil.generateNewTrip(userId, await tripGetters.getTripNumber())
        await dbWriter.createTripDir(trip.id)
        await dbWriter.writeTrip(trip.id, trip)
        await dbWriter.writeTripPhotos(trip.id, {})
        await dbWriter.writeTripComments(trip.id, {})
        await this.addTripNumber()
        return tripGetters.getTrip(trip.id)
    }
    async updateSummary(tripId, summary, userId) {
        if (!await authenticator.isUserInTrip(tripId, userId)) throw msgConfig.POST_TRIP_SUMMARY_NOT_ALLOWED
        const trip = await dbReader.readTrip(tripId)
        if (!!summary.name) trip.name = summary.name
        if (!!summary.description) trip.description = summary.description
        await dbWriter.writeTrip(tripId, trip)
        return tripGetters.getTrip(tripId)
    }
    async generatePhotosFromFiles(tripId, files) {
        let photoIndex = await tripGetters.getPhotoNb(tripId)
        return Promise.all(files.map(async file => {
            photoIndex += 1
            const photoId = await mediaWriter.updateTripPhotoPath(file, tripId, photoIndex)
            return mediaReader.readTripPhoto(tripId, photoId)
        }))
    }
    async addPhotos(tripId, newPhotos, ownerId) {
        if (!await authenticator.isUserInTrip(tripId, ownerId)) throw msgConfig.POST_TRIP_PHOTOS_NOT_ALLOWED
        const trip = await dbReader.readTrip(tripId)
        const photos = await dbReader.readTripPhotos(tripId)
        newPhotos.forEach(photo => {
            photo.owner = ownerId
            photos[photo.id] = photo
            trip.photoNb += 1
            trip.dailyInfos = tripUtil.generateDailyInfosWhenAddingPhoto(trip.dailyInfos, photo)
        })
        await Promise.all([dbWriter.writeTrip(tripId, trip), dbWriter.writeTripPhotos(tripId, photos)])
        return { trip: await tripGetters.getTrip(tripId), photos: await tripGetters.getPhotos(tripId) }
    }
}
export default new Actions()