import cv2
import numpy as np
import pandas as pd

from keras.optimizers import SGD
from udfs.anujdutt9.CNN_Keras.cnn.neural_network import CNN
from src.udfs.abstract_udfs import AbstractClassifierUDF
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace

class MnistCNN(AbstractClassifierUDF):

    @property
    def name(self) -> str:
        return 'MnistCNN'

    def __init__(self):
        super().__init__()
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.clf = CNN.build(width=28, height=28, depth=1, total_classes=10,
                Saved_Weights_Path='udfs/anujdutt9/CNN_Keras/cnn_weights.hdf5')
        self.clf.compile(loss="categorical_crossentropy", optimizer=sgd,
                metrics=["accuracy"])

    @property
    def input_format(self):
        return FrameInfo(1, 28, 28, ColorSpace.RGB)

    @property
    def labels(self):
        return list([str(num) for num in range(10)])

    def classify(self, df: pd.DataFrame):
        ret = pd.DataFrame()
        ret['label'] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        frame = frames[0]
        image = np.array(frame).astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_32F)
        image = image[np.newaxis, np.newaxis, ...]
        probs = self.clf.predict(image)
        prediction = probs.argmax(axis=1)
        return str(prediction[0])
