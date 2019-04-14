class DateFormatter {
    getGenericYearMonthDay(date) {
        if (!date) date = new Date()
        return `${date.getFullYear()}-${date.getMonth()}-${date.getDay()}`
    }
    getGenericHourMinute(date) {
        if (!date) date = new Date()
        return `${date.getHours()}:${date.getMinutes()}`
    }
}
export default new DateFormatter()