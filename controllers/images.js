const path = require("path");
const { spawn } = require("child_process");

const HttpError = require("../models/httpError");
const { deleteFile } = require("../utils/file");
const randomCaptions = require("../random_captions");

const LOCAL_ENV_PYTHON_INTERPRETER_PATH =
    "<VIRTUAL_ENV_PYTHON_INTERPRETER_PATH>" || "python";

const PYTHON_PATH =
    process.env.NODE_ENV === "production"
        ? "python"
        : LOCAL_ENV_PYTHON_INTERPRETER_PATH;

const PYTHON_SCRIPT_PATH = "generate_caption.py";

const generateImagePrediction = async (req, res, next) => {
    const pythonProcess = spawn(PYTHON_PATH, [
        path.resolve(PYTHON_SCRIPT_PATH),
        "image",
        req.file.path,
    ]);

    let prediction;

    pythonProcess.stdout.on("data", (data) => {
        prediction = data.toString();
        console.log(data);
    });

    pythonProcess.stderr.on("data", (data) => {
        prediction = data.toString();
        console.log(data);
    });

    pythonProcess.on("error", (err) => {
        console.log(err);
    });

    pythonProcess.on("close", (code) => {
        if (code === 0) {
            prediction = prediction.trim();
            res.send({ prediction });
            if (req.file?.path) deleteFile(req.file.path);
        } else {
            if (req.file?.path) deleteFile(req.file.path);
            const error = new HttpError(
                "An unknown error occurred! Please try again.",
                500
            );
            next(error);
        }
    });
};

const generateRandomPrediction = async (req, res, next) => {
    const index = Math.floor(Math.random() * 1000);
    res.send({ prediction: randomCaptions[index] });
};

module.exports = { generateImagePrediction, generateRandomPrediction };
