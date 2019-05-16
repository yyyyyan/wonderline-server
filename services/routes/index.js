import express from 'express'
import multer from 'multer'
import userProcessor from './user-processor'
import tripProcessor from './trip-processor'
import httpConfig from './../../configs/http-config'
import dbConfig from './../../configs/db-config'
const router = express.Router()
const upload = multer({ dest: dbConfig.MEDIA_ROOT_PATH })

/** App statistic routes */
router.get('/statistic/user-nb', userProcessor.getUserNumber)
router.get('/statistic/trip-nb', tripProcessor.getTripNumber)

/** User routes */
router.get('/user', userProcessor.getUser)

/** Trip routes */
// TODO Replace id path by query id
router.get('/trip', tripProcessor.getTrip)
router.get('/trip/photos', tripProcessor.getPhotos)
router.get('/trip/comments', tripProcessor.getPhotoComments)
router.post('/trip/summary', tripProcessor.postSummary)
router.post('/trip/photos', upload.array('files', httpConfig.MAX_FILE_NB_PER_POST), tripProcessor.postPhotos)

export default router;