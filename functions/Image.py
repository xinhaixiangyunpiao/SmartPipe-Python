import cv2
import time

# 生成图片相关
class Gen:
    # 从视频生成
    class genFromVideo:
        def __init__(self, paras):
            self.path, self.fps = paras
            self.cap = cv2.VideoCapture(self.path)
            self.time_start = time.perf_counter()
            self.cnt = 0
        
        def loop(self):
            ret, frame = self.cap.read()
            if ret:
                while time.perf_counter() - self.time_start <= self.cnt/(float)(self.fps):
                    pass
                self.cnt += 1
                return [frame]
            else:
                return None

        def finish(self):
            self.cap.release()

# Resize相关
class Resize:
    # resize
    class resize:
        def __init__(self, paras):
            self.h, self.w = paras
        
        def loop(self, data):
            # time.sleep(0.25)
            res = []
            for line in data:
                img = cv2.resize(line[0], (self.w, self.h))
                res.append(img)
            return res
        
        def finish(self):
            pass

# Save相关
class Save:
    # save
    class save:
        def __init__(self, paras):
            self.path, self.h, self.w, self.fps = paras
            self.videoWriter = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc('I', '4', '2', '0'), self.fps, (self.w, self.h))

        def loop(self, data):
            # time.sleep(0.25)
            for line in data:
                self.videoWriter.write(line[0])
            return None

        def finish(self):
            self.videoWriter.release()


class Trans:
    # tans
    class trans:
        def __init__(self, paras):
            pass
        
        # loop
        def loop(self, data):
            return data
        
        # finish
        def finish(self):
            pass
# # Crop相关
# class Crop:
#     def crop(data, paras):
#         res = []
#         for line in data:
#             image, rect = line
#             x1, y1, x2, y2 = rect
#             Y = image.shape[0]
#             X = image.shape[1]
#             Y1 = y1*Y
#             Y2 = y2*Y
#             X1 = x1*X
#             X2 = x2*X
#             img = image[Y1:Y2, X1:X2]
#             res.append(img)
#         return res

# # Show相关
# class Show:
#     # show
#     def show(data, paras):
#         cv2.imshow("img", paras[0])