const path = require('path')
export default {
    DB_ROOT_PATH: path.join(__dirname, '../database'),
    MEDIA_ROOT_PATH: path.join(__dirname, '../public'),
    DEFAULT_AVATAR_REL_PATH: '/assets/default_avatar.png'
}