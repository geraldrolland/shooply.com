const {emailVerificationHandler} = require("./event_handler")
const email_event_mapper = (data) => {
    switch(data.event) {
        case "email_verification":
            emailVerificationHandler(data.data);
            break;

        default:
            console.error("unknown event type");
    }
}

module.exports = {
    email_event_mapper,
}