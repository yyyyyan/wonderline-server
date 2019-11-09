import userGetters from './getters'
import userUtils from './utils'
import dbReader from '../utils/db-reader'
import dbWriter from '../utils/db-writer'
import msgConfig from '../../configs/msg-config'

class Actions {
    async addUserNumber() {
        let dataCounter = await dbReader.readDataCounter()
        dataCounter.userNb = dataCounter.userNb + 1
        return dbWriter.writeDataCounter(dataCounter)
    }
    async createUser(userInfo) {
        const users = await dbReader.readUsers()
        if (!!users[userInfo.email]) throw msgConfig.POST_USER_EMAIL_DUPLICATED
        const user = userUtils.generateNewUser(userInfo, await userGetters.getUserNumber())
        users[userInfo.email] = user.id
        await dbWriter.writeUsers(users)
        await dbWriter.createUserDir(user.id)
        await dbWriter.writeUserAuthen(user.id, userUtils.generateUserAuthen(userInfo))
        await dbWriter.writeUser(user.id, user)
        await this.addUserNumber()
        return userGetters.getUser(user.id)
    }

}
export default new Actions()