import dbReader from '../utils/db-reader'
import userGetters from '../user/getters'

class Getters {
    async getTripNumber() {
        const dataCounter = await dbReader.readDataCounter()
        return dataCounter.tripNb
    }
    async getTripPhotos() {

    }
}
export default new Getters()