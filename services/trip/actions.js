import dbReader from '../utils/db-reader'
import dbWriter from '../utils/db-writer'

class Actions {
    async addTripNumber() {
        const dataCounter = await dbReader.readDataCounter()
        dataCounter.tripNb = dataCounter.tripNb + 1
        return dbWriter.writeDataCounter(dataCounter)
    }
}
export default new Actions()