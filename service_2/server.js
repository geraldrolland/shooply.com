require("dotenv").config();
const express = require("express");
const {runEmailConsumer} = require("./email_consumer")
const cors = require("cors");
const app = express();


// Middleware to parse JSON bodies
app.use(express.json());

// Middleware to handle CORS
app.use(cors({
    origin: "http://127.0.0.1:8000",
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"]
}));

runEmailConsumer().catch(err => {
    console.error("Error running consumer:", err);
});

app.listen(process.env.PORT, async () => {
    console.log("server  started at http://localhost:3000/");
})