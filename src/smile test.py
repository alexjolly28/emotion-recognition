from statistics import mode
from face import overlay_img_above_facial_frame
import cv2
import serial
from keras.models import load_model
import numpy as np

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

# ser = serial.Serial('/dev/cu.usbmodem1421',9600)

# parameters for loading data and images
detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')
IMAGE_PATH = 'happ.png'
hat = cv2.imread(IMAGE_PATH, -1)
# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []
# starting video streaming
cv2.namedWindow('window_frame')
video_capture = cv2.VideoCapture(0)
while True:
    bgr_image = video_capture.read()[1]
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    faces = detect_faces(face_detection, gray_image)
    #l_img = cv2.imread(rgb_image)
    #s_img = cv2.imread("bean.jpg")



    for face_coordinates in faces:

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        #print(x1,x2,y1,y2)
        gray_face = gray_image[y1:y2, x1:x2]
        area = (y2-y1) * (x2-x1)

        if area >500 and area <800 :
            print("tst")
            try:
             gray_face = cv2.resize(gray_face, (emotion_target_size))
            except :
                continue
            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_prediction = emotion_classifier.predict(gray_face)
            emotion_probability = np.max(emotion_prediction)
            #print("emotion probability" , emotion_probability)
    #print("\n")
            #print("emotion prediction" , emotion_prediction)

            emotion_label_arg = np.argmax(emotion_prediction)
            #print("emotion label " , emotion_label_arg)
            emotion_text = emotion_labels[emotion_label_arg]
            print(emotion_text)
            emotion_window.append(emotion_text)
            if len(emotion_window) > frame_window:
                emotion_window.pop(0)
            try:
                emotion_mode = mode(emotion_window)
            except:
                continue
            #if emotion_text == 'angry':
            #    color = emotion_probability * np.asarray((255, 0, 0))
            #elif emotion_text == 'sad':
                #color = emotion_probability * np.asarray((0, 0, 255))
            if emotion_text == 'happy':
                color = np.asarray((255, 255, 0))
            # elif emotion_text == 'surprise':
            #     color = emotion_probability * np.asarray((0, 255, 255))
            else:
                color = np.asarray((0, 255, 0))

            #print("this is " , color)
            color = color.astype(int)
            color = color.tolist()

            if emotion_probability >0.80 :
                        if emotion_text == 'happy' and area >= 500:
                            draw_bounding_box(face_coordinates, rgb_image, color)
                            draw_text(face_coordinates, rgb_image, emotion_mode,
                                      color, 0, -45, 1, 1)
                            #print("emotion probability" , emotion_probability)
                            print("you are HAPPY !!!!!!!!")
                            # ser.write(b'1')

                            frameo = overlay_img_above_facial_frame(rgb_image, x1, x2, y1, y2, hat)

                            #cv2.imshow('dst_rt', l_img)
                            print(area)
                            break
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    #bgr_image = cv2.cvtColor(l_img, cv2.COLOR_RGB2BGR)

    cv2.imshow('window_frame', bgr_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
