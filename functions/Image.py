import cv2
import time

# 生成图片相关
class Gen:
    # 从视频生成
    def genFromVideo(paras):
        cap, fps = paras
        time_start = time.perf_counter()
        ret, frame = cap.read()
        if ret:
            while time.perf_counter() - time_start <= 1/(float)(fps):
                pass
            return frame
        else:
            return None

# Resize相关
class Resize:
    # resize
    def resize(data, paras):
        h,w = paras
        res = []
        for line in data:
            img = cv2.resize(line[0], (h,w))
            res.append(img)
        return res

# Crop相关
class Crop:
    def crop(data, paras):
        res = []
        for line in data:
            image, rect = line
            x1, y1, x2, y2 = rect
            Y = image.shape[0]
            X = image.shape[1]
            Y1 = y1*Y
            Y2 = y2*Y
            X1 = x1*X
            X2 = x2*X
            img = image[Y1:Y2, X1:X2]
            res.append(img)
        return res

# Show相关
class Show:
    # show
    def show(data, paras):
        cv2.imshow("img", paras[0])

# Save相关
class Save:
    # save
    def save(data, paras):
        videoWriter = paras[0]
        for line in data:
            videoWriter.write(line[0])