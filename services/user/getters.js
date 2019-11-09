import dbReader from '../utils/db-reader'
import authenticator from '../utils/authenticator'
import userUtil from './utils'
import tripGetters from '../trip/getters'
import msgConfig from '../../configs/msg-config'

class Getters {
    async getUserNumber() {
        const dataCounter = await dbReader.readDataCounter()
        return dataCounter.userNb
    }
    async getLoginUser(email, password) {
        const id = await authenticator.getUserIdIfLoginAuthenticated(email, password)
        if (!id) throw msgConfig.GET_LOGIN_USER_INPUT_INVALID
        return this.getUser(id)
    }
    async getUser(userId) {
        const user = await dbReader.readUser(userId)
        user.friends = await Promise.all(user.friends.map(async id => this.getReducedUser(id)))
        user.trips = await Promise.all(user.trips.map(async id => tripGetters.getReducedTrip(id)))
        return userUtil.generateUserWithCompleteSrc(user)
    }
    // TODO Find a way to avoid code duplication
    async getReducedUser(userId) {
        return userUtil.generateReducedUser(await dbReader.readUser(userId))
    }
}
export default new Getters()