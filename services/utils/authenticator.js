import dbReader from './db-reader'

class Authenticator {
    async getUserIdIfLoginAuthenticated(email, password) {
        const users = await dbReader.readUsers()
        if (!users[email]) return null
        const authen = await dbReader.readUserAuthen(users[email])
        if (password !== authen.password) return null
        return users[email]
    }
    async isAnyUserInTrip(userIds, tripId) {

    }
    async isUserInTrip(tripId, userId) {
        const trip = await dbReader.readTrip(tripId)
        return trip.users.find(tripUserId => userId === tripUserId)
    }
}
export default new Authenticator()