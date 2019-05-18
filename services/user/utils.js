import dbConfig from '../../configs/db-config'
import httpConfig from '../../configs/http-config'

class Utils {
    generateNewUser(newUser, userNb) {
        return {
            id: `user_${userNb + 1}`,
            name: newUser.name,
            avatarSrc: dbConfig.DEFAULT_AVATAR_REL_PATH,
            friends: [],
            trips: []
        }
    }
    generateUserAuthen(user) {
        return {
            email: user.email,
            password: user.password
        }
    }
    generateUserWithCompleteSrc(user) {
        user.avatarSrc = httpConfig.SERVER_ADDRESS + user.avatarSrc
        return user
    }
    generateReducedUser(user) {
        user = this.generateUserWithCompleteSrc(user)
        return {
            id: user.id,
            name: user.name,
            avatarSrc: user.avatarSrc
        }
    }
}

export default new Utils()