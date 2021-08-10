const fs = require("fs");

const express = require("express");
const rateLimit = require("express-rate-limit");
const helmet = require("helmet");
const compression = require("compression");

// import your routes
const imagesRoutes = require("./routes/images");
const HttpError = require("./models/httpError");

// Express Application
const app = express();

// serve static files here

// Can define rate-limiting as a middleware differently for different requests
// Don't define it before serving static files
app.use(
    rateLimit({
        max: 100, // limit each IP to 100 requests per windowMs
        windowMs: 25 * 60 * 1000, // 25 minutes
        message: "'Too many requests, please try again later!", // Error message sent to user when max is exceeded
    })
);

// Add security headers to response
app.use(helmet());

// Compress the response bodies
app.use(compression());

// Parse the request body & Request size limits
app.use(express.json({ limit: "100kb" }));

// Allowing CORS
app.use((req, res, next) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    );
    res.setHeader(
        "Access-Control-Allow-Methods",
        "GET, POST, PUT, PATCH, DELETE"
    );
    next();
});

// use your routes here
app.use("/images", imagesRoutes);

// Undefined Routes
app.use((req, res, next) => {
    const error = new HttpError("Could not find this route.", 404);
    throw error;
});

// Error Handler
app.use((error, req, res, next) => {
    if (req.file) {
        fs.unlink(req.file.path, (err) => console.log(err));
    }
    if (res.headerSent) {
        return next(error);
    }
    res.status(error.code || 500);
    res.json({ message: error.message || "An unknown error occurred!" });
});

// Running our express app
const port = process.env.PORT || 8000;
app.listen(port, () => {
    console.log("Server running!");
});
