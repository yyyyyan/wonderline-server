import dbConfig from '../../configs/db-config'
const fs = require('fs')

class MediaWriter {
    updateTripPhotoPath(file, tripId, photoIndex) {
        const tripIndex = tripId.slice(5)
        const photoId = `photo_${tripIndex}_${photoIndex}`
        const tempPath = file.path
        // TODO make image format dynamic (jpeg, png ...)
        const targetPath = `${dbConfig.MEDIA_ROOT_PATH}/trips/${tripId}/${photoId}.png`
        return new Promise((resolve, reject) => {
            fs.rename(tempPath, targetPath, err => {
                if (err) return reject(err)
                resolve(photoId)
            })
        })
    }
}
export default new MediaWriter()