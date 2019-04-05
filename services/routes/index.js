import express from 'express'
import userProcessor from './user-processor'
import tripProcessor from './trip-processor'
const router = express.Router()

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
router.get('/trip/:id/comments/:pid', tripProcessor.getPhotoComments)

export default router;