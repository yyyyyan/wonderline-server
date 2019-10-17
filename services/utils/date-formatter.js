class DateFormatter {
    getGenericYearMonthDay(date) {
        if (!date) date = new Date()
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDay()}`
    }
    getGenericHourMinute(date) {
        if (!date) date = new Date()
        return `${date.getHours()}:${date.getMinutes()}`
    }
    getGenericTimeStamp(date) {
        if (!date) date = new Date()
        return date.getTime()
    }
}
export default new DateFormatter()