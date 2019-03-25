import dbReader from '../utils/db-reader'
import dbWriter from '../utils/db-writer'

class Actions {
    async addUserNumber() {
        let dataCounter = await dbReader.readDataCounter()
        dataCounter.userNb = dataCounter.userNb + 1
        return dbWriter.writeDataCounter(dataCounter)
    }
}
export default new Actions()