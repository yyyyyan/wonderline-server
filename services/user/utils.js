import dbConfig from '../../configs/db-config'
import httpConfig from '../../configs/http-config'

class Utils {
    generateNewUser(newUser, userNb) {
        return {
            id: `user_${userNb + 1}`,
            name: newUser.name,
            signature: newUser.signature || '',
            avatarSrc: dbConfig.DEFAULT_AVATAR_REL_PATH,
            profileBkgSrc: dbConfig.DEFAULT_PROFILE_BKG_REL_PATH,
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
        user.profileBkgSrc = httpConfig.SERVER_ADDRESS + user.profileBkgSrc
        return user
    }
    generateReducedUser(user) {
        user = this.generateUserWithCompleteSrc(user)
        return {
            id: user.id,
            name: user.name,
            signature: user.signature,
            avatarSrc: user.avatarSrc,
            profileBkgSrc: user.profileBkgSrc
        }
    }
}

export default new Utils()