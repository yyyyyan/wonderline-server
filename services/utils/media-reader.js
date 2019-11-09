import dbConfig from '../../configs/db-config'
import dateFormatter from './date-formatter'
const gm = require('gm')

class MediaReader {
    async readTripPhoto(tripId, photoId) {
        const photoSrc = `/trips/${tripId}/${photoId}.png`
        const photoSize =
            await this.readImgSize(`${dbConfig.MEDIA_ROOT_PATH}${photoSrc}`)
        // TODO get real loc, date, time
        return {
            id: photoId,
            loc: "Local device",
            date: dateFormatter.getGenericYearMonthDay(),
            time: dateFormatter.getGenericHourMinute(),
            width: photoSize.width,
            height: photoSize.height,
            src: photoSrc,
            owner: "?"
        }
    }
    readImgSize(imageSrc) {
        return new Promise((resolve, reject) => {
            gm(imageSrc).size((err, size) => {
                if (err) reject(err)
                resolve(size)
            })
        })
    }
}
export default new MediaReader()