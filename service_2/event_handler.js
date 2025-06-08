const nodemailer = require("nodemailer");
require("dotenv").config();
const { emailVerificationTemplate } = require("./mail_template");


const transport = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT),
    secure: false,
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASSWORD
    },
    tls: {
        rejectUnauthorized: false, // Sometimes needed for Gmail
    }
})

const emailVerificationHandler = (data) => {
    
    const mail = {
        from: process.env.SENDER_EMAIL,
        to: data.email,
        replyTo: process.env.REPLY_TO,
        subject: "Email Verification",
        html: emailVerificationTemplate(data.data),
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
}