import cv2
import numpy as np
import onnxruntime as rt
from sklearn import preprocessing 

class faceEmbeddingExtractor:
    def __init__(self, modelFile):
        sessOptions = rt.SessionOptions()
        sessOptions.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_ALL    
        self.embeddingExtractor = rt.InferenceSession(modelFile, sessOptions)
        self.inputNodeName = self.embeddingExtractor.get_inputs()[0].name

    def extract(self, alignFaces):
        alignFaces = alignFaces.transpose(0,3,1,2).astype(np.float32)
        embeddings = self.embeddingExtractor.run([], {self.inputNodeName: alignFaces})[0]
        embeddings = preprocessing.normalize(embeddings)

        return embeddings