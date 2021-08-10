## PYTHON SCRIPT BUILT SO AS TO EXECUTE FROM NODE.JS SERVER

## AVAILABLE COMMANDS

# > python generate_caption.py generate
# generates captions for all the dev set images and store them in random_captions.txt

# > python generate_caption.py image <path_to_image>
# predict caption for the provided image

# IMPORTS
import sys
import numpy as np
from pickle import load
from tensorflow.keras.applications.resnet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.lite.python import interpreter as interpreter_wrapper

# Path to root dataset folder on mounted drive
project_root_path = "./Python/"
models_root_path = project_root_path + "Models/"
variables_root_path = project_root_path + "Variables/"

# Function to load data from .pkl file at filepath
def loadData(filepath):
    with open(filepath, "rb") as encoded_pickle:
        return load(encoded_pickle)


# Loading Variables
max_caption_length = loadData(variables_root_path + "max_caption_length.pickle")
dev_dataset = loadData(variables_root_path + "dev_dataset.pickle")

# resnet_model = load_model(models_root_path + "resnet_model.h5")

encoded_dev_images = loadData(variables_root_path + "encoded_dev_images_resnet.pickle")

index_to_word = loadData(variables_root_path + "index_to_word.pickle")
word_to_index = loadData(variables_root_path + "word_to_index.pickle")

loaded_language_model = load_model(models_root_path + "language_model_2")

# Load the TFLite model and allocate tensors.
interpreter = interpreter_wrapper.Interpreter(
    model_path=models_root_path + "/resnet_model.tflite"
)
interpreter.allocate_tensors()
# Get input and output tensors.
input_index = interpreter.get_input_details()[0]["index"]
output_index = interpreter.get_output_details()[0]["index"]

# FUNCTION TO PREDICT CAPTION FROM FEATURE VECTOR
def predict(feature_vec):
    partial_caption = "startseq"
    for i in range(max_caption_length):
        # integer encode input sequence
        seq = [
            word_to_index[word]
            for word in partial_caption.split()
            if word in word_to_index
        ]
        # pad input
        seq = pad_sequences([seq], maxlen=max_caption_length)
        # predict next word
        model_softMax_output = loaded_language_model.predict(
            [feature_vec, seq], verbose=0
        )
        # convert probability to integer
        word_index = np.argmax(model_softMax_output)
        # map integer to word
        word = index_to_word[word_index]
        partial_caption += " " + word
        if word == "endseq":
            break
    final_caption = partial_caption.split()[1:-1]
    final_caption = " ".join(final_caption)
    return final_caption


# FUNCTION TO CONVERT IMAGE TO FEATURE VECTOR
def image_to_feature_vec(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    # convert the image pixels to a numpy array
    x = image.img_to_array(img)
    # prepare the image for the ResNet model
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    # get features
    interpreter.set_tensor(input_index, x)
    interpreter.invoke()
    feature_vec = interpreter.get_tensor(output_index)
    # reshape data for the model
    feature_vec = np.reshape(feature_vec, feature_vec.shape[1])
    return feature_vec.reshape((1, 2048))


# FUNCTION TO GENERATE CAPTIONS FOR ALL DEV DATASET IMAGES
def generate_captions():
    with open("./random_captions.txt", "w") as file:
        for i in range(0, 1000):
            key = list(dev_dataset.keys())[i]
            feature_vec = encoded_dev_images[key].reshape((1, 2048))
            file.write('"{}${}",\n'.format(key, predict(feature_vec)))


# FUNCTION TO GENERATE CAPTION FROM IMAGE WITH PROVIDED PATH
def generate_caption_from_image(image_path):
    feature_vec = image_to_feature_vec(image_path)
    print("{}".format(predict(feature_vec)))
    sys.stdout.flush()  # Return printed output back to Node.js server


if __name__ == "__main__":
    if sys.argv[1] == "generate":
        generate_captions()
    elif sys.argv[1] == "image":
        generate_caption_from_image(sys.argv[2])
