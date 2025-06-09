const nodemailer = require("nodemailer");
require("dotenv").config();
const { emailVerificationTemplate } = require("./mail_template");


const transport = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT),
    secure: process.env.SMTP_PORT === '465',
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASSWORD
    },
    tls: {
        rejectUnauthorized: false, // Sometimes needed for Gmail
    }
})

const emailVerificationHandler = ({email, verification_link}) => {  
    const mail = {
        from: process.env.SENDER_EMAIL,
        to: email,
        replyTo: process.env.REPLY_TO,
        subject: "Email Verification",
        html: emailVerificationTemplate(verification_link),
        priority: "high",
        date: new Date(),
    };
    transport.sendMail(mail, (err, info) => {
        if (err) {
            console.error(err);
        } else {
            console.log(info.response);
        }
    })
}

module.exports = {
    emailVerificationHandler,
};