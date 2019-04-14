import dbReader from '../utils/db-reader'
import dbWriter from '../utils/db-writer'
import tripGetters from './getters'
import tripUtil from './utils'
import mediaReader from "../utils/media-reader";
import mediaWriter from "../utils/media-writer";

class Actions {
    async addTripNumber() {
        const dataCounter = await dbReader.readDataCounter()
        dataCounter.tripNb = dataCounter.tripNb + 1
        return dbWriter.writeDataCounter(dataCounter)
    }
    async generatePhotosFromFiles(tripId, files) {
        let photoIndex = await tripGetters.getPhotoNb(tripId)
        return await Promise.all(files.map(async file => {
            photoIndex += 1
            const photoId = await mediaWriter.updateTripPhotoPath(file, tripId, photoIndex)
            return await mediaReader.readTripPhoto(tripId, photoId)
        }))
    }
    async addPhotos(tripId, newPhotos, ownerId) {
        const trip = await dbReader.readTrip(tripId)
        const photos = await dbReader.readTripPhotos(tripId)
        newPhotos.forEach(photo => {
            photo.owner = ownerId
            photos[photo.id] = photo
            trip.photoNb += 1
            trip.dailyInfos = tripUtil.generateDailyInfosWhenAddingPhoto(trip.dailyInfos, photo)
        })
        return await Promise.all([dbWriter.writeTrip(tripId, trip),
            dbWriter.writeTripPhotos(tripId, photos)])
    }
}
export default new Actions()