import dbConfig from '../../configs/db-config'
const fs = require('fs')

class DbReader {
    async readUser(userId) {
        return await this.readJson(`users/${userId}/user.json`)
    }
    async readTrip(tripId) {
        return await this.readJson(`trips/${tripId}/trip.json`)
    }
    async readTripDailyInfos(tripId) {
        return await this.readJson(`trips/${tripId}/daily-infos.json`)
    }
    async readTripPhotos(tripId) {
        return await this.readJson(`trips/${tripId}/photos.json`)
    }
    async readTripComments(tripId) {
        return await this.readJson(`trips/${tripId}/comments.json`)
    }
    async readDataCounter() {
        return await this.readJson('data-counter.json')
    }
    readJson(filePath) {
        return new Promise(function(resolve, reject) {
            fs.readFile(`${dbConfig.DB_ROOT_PATH}${filePath}`, (err, data) => {
                if (err) return reject(err)
                resolve(JSON.parse(data))
            })
        })
    }
}
export default new DbReader()

