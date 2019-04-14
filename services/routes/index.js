import express from 'express'
import multer from 'multer'
import userProcessor from './user-processor'
import tripProcessor from './trip-processor'
import httpConfig from './../../configs/http-config'
import dbConfig from './../../configs/db-config'
const router = express.Router()
const upload = multer({ dest: dbConfig.MEDIA_ROOT_PATH })

/** For testing*/
router.get('/statistic/user-nb', userProcessor.getUserNumber)
router.post('/statistic/user-nb', userProcessor.getUserNumber)
router.get('/statistic/trip-nb', tripProcessor.getTripNumber)
router.post('/statistic/trip-nb', tripProcessor.postTripNumber)

/** User routes */
router.get('/user/:id', userProcessor.getUser)

/** Trip routes */
router.get('/trip/:id', tripProcessor.getTrip)
router.get('/trip/:id/photos', tripProcessor.getPhotos)
router.get('/trip/:id/comments', tripProcessor.getPhotoComments)
router.post('/trip/:id/photos', upload.array('files', httpConfig.MAX_FILE_NB_PER_POST), tripProcessor.postPhotos)

export default router;