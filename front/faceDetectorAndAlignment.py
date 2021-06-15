import cv2
import numpy as np
import onnxruntime as rt
class faceDetectorAndAlignment:
    def __init__(self, modelFile, processScale):
        sessOptions = rt.SessionOptions()
        sessOptions.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_ALL 

        self.detector = rt.InferenceSession(modelFile, sessOptions)
        self.transDst = np.array([
                [30.2946, 51.6963],
                [65.5318, 51.5014],
                [48.0252, 71.7366],
                [33.5493, 92.3655],
                [62.7299, 92.2041]], dtype=np.float32)
        self.transDst[:, 0] += 8.0
        self.processScale = processScale

    def calcImageScale(self, h, w):
        hNew, wNew = int(np.ceil(h / 32) * 32), int(np.ceil(w / 32) * 32)
        ratioH, ratioW = hNew / h, wNew / w
        return (hNew, wNew), (ratioH, ratioW)

    def nms(self, dets, thresh):
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        scores = dets[:, 4]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= thresh)[0]
            order = order[inds + 1]

        return keep

    def map2Box(self, probs, scales, offsets, landmarks, size, threshold=0.5):
        probs = np.squeeze(probs)
        probs0, probs1 = np.where(probs > threshold)

        scale0, scale1 = scales[0, 0, :, :], scales[0, 1, :, :]
        offset0, offset1 = offsets[0, 0, :, :], offsets[0, 1, :, :]

        faceBoxes = []
        faceLandmarks = []

        if len(probs0) > 0:
            for scaleNo in range(len(probs0)):
                ### T.4 ###
                s0 = np.exp(scale0[probs0[scaleNo], probs1[scaleNo]]) * 4
                s1 = np.exp(scale1[probs0[scaleNo], probs1[scaleNo]]) * 4

                o0 = offset0[probs0[scaleNo], probs1[scaleNo]] 
                o1 = offset1[probs0[scaleNo], probs1[scaleNo]]

                s = probs[probs0[scaleNo], probs1[scaleNo]]

                ### Eq.5 ###
                x1 = np.clip((probs1[scaleNo] + o1 + 0.5) * 4 - s1 / 2, 0, size[1])
                y1 = np.clip((probs0[scaleNo] + o0 + 0.5) * 4 - s0 / 2, 0, size[0])
                x2 = np.clip(x1 + s1, 0, size[1])
                y2 = np.clip(y1 + s0, 0, size[0])

                faceBoxes.append([x1, y1, x2, y2, s])

                faceLandmark = []
                for j in range(5):
                    faceLandmark.append(landmarks[0, j * 2 + 1, probs0[scaleNo], probs1[scaleNo]] * s1 + x1)
                    faceLandmark.append(landmarks[0, j * 2, probs0[scaleNo], probs1[scaleNo]] * s0 + y1)
                faceLandmarks.append(faceLandmark)

            faceBoxes = np.asarray(faceBoxes, dtype=np.float32)
            faceLandmarks = np.asarray(faceLandmarks, dtype=np.float32)

            keepIdx = self.nms(faceBoxes, 0.3)
            faceBoxes = faceBoxes[keepIdx, :]
            
            faceLandmarks = faceLandmarks[keepIdx, :]
        return faceBoxes, faceLandmarks

    def scaleOutput(self, faceBoxes, faceLandmarks, ratioW, ratioH):
        faceBoxes[:, 0:4:2], faceBoxes[:, 1:4:2] = faceBoxes[:, 0:4:2] / ratioW, faceBoxes[:, 1:4:2] / ratioH
        faceLandmarks[:, 0:10:2], faceLandmarks[:, 1:10:2] = faceLandmarks[:,0:10:2] / ratioW, faceLandmarks[:, 1:10:2] / ratioH
        return faceBoxes, faceLandmarks

    def faceAligner(self, inputImage, faceLandmarks=None, targetSize=(112,112)):
        
        alignFaces = np.empty((faceLandmarks.shape[0], targetSize[0], targetSize[1], 3), dtype=np.uint8)
        for bboxNo in range(faceLandmarks.shape[0]):
            faceLandmark = faceLandmarks[bboxNo].reshape(5,2)
            dst = faceLandmark.astype(np.float32)
            M = self.umeyama(dst, self.transDst)[0:2, :]
            alignFaces[bboxNo,:,:,:] = cv2.warpAffine(inputImage, M, (targetSize[1], targetSize[0]), borderValue=0.0)
        return alignFaces

    def detect(self, inputFrame):
        inputFrameRGB = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2RGB)

        if self.processScale !=1:
            processFrame = cv2.resize(inputFrame,None, fx=self.processScale, fy=self.processScale)
        else:
            processFrame = inputFrame
        h, w = processFrame.shape[0], processFrame.shape[1]
        (hNew, wNew), (ratioH, ratioW) = self.calcImageScale(h, w)

        if len(processFrame.shape) != 3:
            processFrame = cv2.cvtColor(processFrame, cv2.COLOR_GRAY2BGR)
        processFrameRGB = cv2.cvtColor(processFrame, cv2.COLOR_BGR2RGB)

        processBlob = cv2.resize(processFrameRGB, (wNew, hNew))
        processBlob = processBlob.transpose(2,0,1)[np.newaxis].astype(np.float32)
        probs, scales, offsets, landmarks = self.detector.run(["537", "538", "539", "540"], {'input.1': processBlob})

        faceBoxes, faceLandmarks = self.map2Box(probs, scales, offsets, landmarks, size=(hNew, wNew), threshold=0.5)

        if len(faceBoxes) >= 1:
            ## Rescale to process scale ###
            faceBoxes, faceLandmarks = self.scaleOutput(faceBoxes, faceLandmarks, ratioW * self.processScale, ratioH * self.processScale)

            alignedFace = self.faceAligner(inputFrameRGB, faceLandmarks, targetSize=(112,112))

            return faceBoxes, faceLandmarks, alignedFace
        else:
            return np.empty((0,5)), np.empty((0,10)), np.empty((0,112,112,3))

    def umeyama(self, src, dst, estimate_scale=True):
        num = src.shape[0]
        dim = src.shape[1]

        # Compute mean of src and dst.
        src_mean = src.mean(axis=0)
        dst_mean = dst.mean(axis=0)

        # Subtract mean from src and dst.
        src_demean = src - src_mean
        dst_demean = dst - dst_mean

        # Eq. (38).
        A = np.dot(dst_demean.T, src_demean) / num

        # Eq. (39).
        d = np.ones((dim,), dtype=np.double)
        if np.linalg.det(A) < 0:
            d[dim - 1] = -1

        T = np.eye(dim + 1, dtype=np.double)

        U, S, V = np.linalg.svd(A)

        # Eq. (40) and (43).
        rank = np.linalg.matrix_rank(A)
        if rank == 0:
            return np.nan * T
        elif rank == dim - 1:
            if np.linalg.det(U) * np.linalg.det(V) > 0:
                T[:dim, :dim] = np.dot(U, V)
            else:
                s = d[dim - 1]
                d[dim - 1] = -1
                T[:dim, :dim] = np.dot(U, np.dot(np.diag(d), V))
                d[dim - 1] = s
        else:
            T[:dim, :dim] = np.dot(U, np.dot(np.diag(d), V.T))

        if estimate_scale:
            # Eq. (41) and (42).
            scale = 1.0 / src_demean.var(axis=0).sum() * np.dot(S, d)
        else:
            scale = 1.0

        T[:dim, dim] = dst_mean - scale * np.dot(T[:dim, :dim], src_mean.T)
        T[:dim, :dim] *= scale

        return T
