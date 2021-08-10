const express = require("express");

const fileUpload = require("../middleware/fileUpload");
const imagesController = require("../controllers/images");

const router = express.Router();

// define your routes here

router.post(
    "/",
    fileUpload.single("image"),
    imagesController.generateImagePrediction
);

router.get("/", imagesController.generateRandomPrediction);

module.exports = router;
