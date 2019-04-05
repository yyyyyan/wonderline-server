import httpConfig from '../../configs/http-config'

class Utils {
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