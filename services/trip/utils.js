import httpConfig from '../../configs/http-config'

class Utils {
    generateReducedTrip(trip) {
        return {
            id: trip.id,
            name: trip.name,
            users: trip.users,
            beginDate: trip.dailyInfos[0].date,
            endDate: trip.dailyInfos[trip.dailyInfos.length-1].date,
            coverPhotoId: trip.coverPhotoId,
            coverPhotoSrc: trip.coverPhotoSrc
        }
    }
    generateDailyInfosWithCoverPhotoSrc(dailyInfos, photos) {
        // TODO find a better way to avoid triple loops
        dailyInfos = dailyInfos.map(dailyInfo => {
            dailyInfo.locs = dailyInfo.locs.map(loc => {
                loc.covers = loc.covers.map(cover => {
                    cover.photoSrc = this.generateCompletePhotoSrc(photos[cover.photoId].src)
                    return cover
                })
                return loc
            })
            return dailyInfo
        })
        return dailyInfos
    }
    generatePhotosWithCompleteSrc(photos) {
        for (let id in photos)
            photos[id].src = this.generateCompletePhotoSrc(photos[id].src)
        return photos
    }
    generateCompletePhotoSrc(photoSrc) {
        return httpConfig.SERVER_ADDRESS + photoSrc
    }
    generateCommentWithUserInfo(comment, user) {
        comment.userName = user.name
        comment.userAvatarSrc = user.avatarSrc
        return comment
    }
}

export default new Utils()