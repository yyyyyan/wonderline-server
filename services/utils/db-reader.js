import dbConfig from '../../configs/db-config'
const fs = require('fs')

class DbReader {
    async readUsers() {
        return this.readJson(`/users/users.json`)
    }
    async readUser(userId) {
        return this.readJson(`/users/${userId}/user.json`)
    }
    async readUserAuthen(userId) {
        return this.readJson(`/users/${userId}/authen.json`)
    }
    async readTrip(tripId) {
        return this.readJson(`/trips/${tripId}/trip.json`)
    }
    async readTripPhotos(tripId) {
        return this.readJson(`/trips/${tripId}/photos.json`)
    }
    async readTripComments(tripId) {
        return this.readJson(`/trips/${tripId}/comments.json`)
    }
    async readDataCounter() {
        return this.readJson('/data-counter.json')
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

