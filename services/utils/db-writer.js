import dbConfig from '../../configs/db-config'
const fs = require('fs')

class DbWriter {
    async writeUsers(users) {
        return this.writeJson(`/users/users.json`, users)
    }
    async createTripDir(tripId) {
        return this.createDir(`/trips/${tripId}`)
    }
    async createUserDir(userId) {
        return this.createDir(`/users/${userId}`)
    }
    async writeUser(userId, user) {
        return this.writeJson(`/users/${userId}/user.json`, user)
    }
    async writeUserAuthen(userId, authen) {
        return this.writeJson(`/users/${userId}/authen.json`, authen)
    }
    async writeTrip(tripId, trip) {
        return this.writeJson(`/trips/${tripId}/trip.json`, trip)
    }
    async writeTripPhotos(tripId, photos) {
        return this.writeJson(`/trips/${tripId}/photos.json`, photos)
    }
    async writeTripComments(tripId, comments) {
        return this.writeJson(`/trips/${tripId}/comments.json`, comments)
    }
    async writeDataCounter(counter) {
        return this.writeJson('/data-counter.json', counter)
    }
    createDir(dirPath) {
        return new Promise((resolve, reject) => {
            fs.mkdir(`${dbConfig.DB_ROOT_PATH}${dirPath}`, (err) => {
                if (err) return reject(err)
                resolve()
            })
        })
    }
    writeJson(filePath, data) {
        return new Promise((resolve, reject) => {
            const convertedData = JSON.stringify(data, null, 2)
            fs.writeFile(`${dbConfig.DB_ROOT_PATH}${filePath}`, convertedData, {recursive: true}, (err) => {
                if (err) return reject(err)
                resolve()
            })
        })
    }
}
export default new DbWriter()

