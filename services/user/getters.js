import dbReader from '../utils/db-reader'
import tripGetters from '../trip/getters'

class Getters {
    async getUserNumber() {
        const dataCounter = await dbReader.readDataCounter()
        return dataCounter.userNb
    }
}
export default new Getters()