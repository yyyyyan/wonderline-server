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


/** Trip routes */

export default router;