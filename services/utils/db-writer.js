import dbConfig from '../../configs/db-config'
const fs = require('fs')

class DbWriter {
    async writeUser(userId, user) {
        return await this.writeJson(`/users/${userId}/user.json`, user)
    }
    async writeTrip(tripId, trip) {
        return await this.writeJson(`/trips/${tripId}/trip.json`, trip)
    }
    async writeTripPhotos(tripId, photos) {
        return await this.writeJson(`/trips/${tripId}/photos.json`, photos)
    }
    async writeTripComments(tripId, comments) {
        return await this.writeJson(`/trips/${tripId}/comments.json`, comments)
    }
    async writeDataCounter(counter) {
        return await this.writeJson('/data-counter.json', counter)
    }
    writeJson(filePath, data) {
        return new Promise((resolve, reject) => {
            const convertedData = JSON.stringify(data, null, 2)
            fs.writeFile(`${dbConfig.DB_ROOT_PATH}${filePath}`, convertedData, (err) => {
                if (err) return reject(err)
                resolve()
            })
        })
    }
}
export default new DbWriter()

