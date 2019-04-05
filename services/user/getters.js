import dbReader from '../utils/db-reader'
import userUtil from './utils'
import tripGetters from '../trip/getters'

class Getters {
    async getUserNumber() {
        const dataCounter = await dbReader.readDataCounter()
        return dataCounter.userNb
    }
    async getUser(userId) {
        const user = await dbReader.readUser(userId)
        user.friends = await Promise.all(user.friends.map(async id => {
            return await this.getReducedUser(id)
        }))
        user.trips = await Promise.all(user.trips.map(async id => {
            return await tripGetters.getReducedTrip(id)
        }))
        return userUtil.generateUserWithCompleteSrc(user)
    }
    // TODO Find a way to avoid code duplication
    async getReducedUser(userId) {
        return userUtil.generateReducedUser(await dbReader.readUser(userId))
    }
}
export default new Getters()