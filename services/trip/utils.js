import httpConfig from '../../configs/http-config'

class Utils {
    generateReducedTrip(trip) {
        return {
            id: trip.id,
            name: trip.name,
            users: trip.users,
            beginDate: trip.dailyInfos[0].date,
            endDate: trip.dailyInfos[trip.dailyInfos.length-1].date,
            coverPhoto: trip.coverPhoto
        }
    }
    generateDailyInfosWithCoverPhotos(dailyInfos, photos) {
        // TODO find a better way to avoid triple loops
        dailyInfos = dailyInfos.map(dailyInfo => {
            dailyInfo.locs = dailyInfo.locs.map(loc => {
                loc.covers = loc.covers.map(cover => {
                    cover.photo = photos[cover.photoId]
                    cover.photo.src = this.generateCompletePhotoSrc(cover.photo.src)
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
    generateDailyInfosWhenAddingPhoto(dailyInfos, photo) {
        const dateIndex = dailyInfos.findIndex(dailyInfo => dailyInfo.date === photo.date)
        if (dateIndex < 0)
            dailyInfos.push(this.generateDailyInfo(photo))
        else if (!dailyInfos[dateIndex].locs.some(loc => loc.name === photo.loc))
            dailyInfos[dateIndex].locs.push(this.generateDailyLoc(photo))
        return dailyInfos
    }
    generateDailyInfo(photo) {
        return {date: photo.date, locs: [this.generateDailyLoc(photo)]}
    }
    generateDailyLoc(photo) {
        return {name: photo.loc, covers: [{photoId: photo.id, comment: ""}]}
    }
}

export default new Utils()