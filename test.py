import os
import cv2
from multiprocessing import Pipe, Queue, Process
from smartpipe import CpuPipe, GpuPipe, GpuAgent
from functions import Image, Table
from models import Model

TEST_STAGE = 0

"""
    阶段一测试
    测试内容：测试SmartPipe中CPU相关API
    测试方式：测试一个简单的三阶段CPU APP
    APP：视频流Resize
    APP流程：
        | Name   | Type | Stateful | Input | Output | Function       | Params    | State        |
        | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen    | path,fps  | videoCapture |
        | Task1  | CPU  | No       | Task0 | Task2  | Image - Resize | h,w       |              |
        | Task2  | CPU  | Yes      | Task1 | None   | Image - Save   | path      | videoWriter  |
    DAG：
        0 -> 1 -> 2
"""

if TEST_STAGE == 0:
    # Queue
    size = 200
    q_0_1 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)

    # CpuPipe
    video_path = "/data/lx/SmartPipe/data_source/videos/new.webm"
    save_path = "/data/lx/SmartPipe/data_source/videos/out.avi"
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1], batch_size=1, processes=[[Image.Gen.genFromVideo, [video_path,25]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize.resize, [540,960]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[], batch_size=1, processes=[[Image.Save.save, [save_path]]])
    # start 
    task0.start()
    task1.start()
    task2.start()

"""
    阶段二测试
    测试内容：测试SmartPipe中CPU和GPU相关API
    测试方式：构造一个车辆识别的APP，并成功运行。
    APP：车辆图片裁剪并输出视频
    APP流程：
        | Name   | Type | Stateful | Input        | Output       | Function              | Params     | State        |
        | Task0  | CPU  | Yes      | None         | Task1        | Image - Gen           | path,fps   | videoCapture |
        | Task1  | CPU  | No       | Task0        | Task2        | Image - Resize        | h,w        |              |
        | Task2  | CPU  | No       | Task1        | Task3        | yolo-preprocess       |            |              |
        | Task3  | GPU  | No       | Task2        | Task4        | yolo-inference        |            |              |
        | Task4  | CPU  | No       | Task3        | Task5        | yolo-postprocess      |            |              |
        | Task5  | CPU  | No       | Task0, Task4 | Task6        | Image - Crop          |            |              |
        | Task6  | CPU  | No       | Task5        | Task1        | Image - Resize        | h,w        |              |
        | Task7  | CPU  | Yes      | Task6        | None         | Image - Save          | path       | videoWriter  |
    DAG:
        0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
"""
if TEST_STAGE == 1:
    pass

"""
    阶段三测试
    测试内容：多GPU任务,DAG图带分支测试
    测试方式：构建一个车牌号识别的APP
    APP：车牌号识别，输出每一帧中的车辆车牌号
    APP流程：
        | Name   | Type | Stateful | Input        | Output       | Function              | Params     | State        |
        | Task0  | CPU  | Yes      | None         | Task1, Task5 | Image - Gen           | path,fps   | VideoCapture |
        | Task1  | CPU  | No       | Task0        | Task2        | Image - Resize        | h,w        |              |
        | Task2  | CPU  | No       | Task1        | Task3        | yolo-preprocess       |            |              |
        | Task3  | GPU  | No       | Task2        | Task4        | yolo-inference        |            |              |
        | Task4  | CPU  | No       | Task3        | Task5        | yolo-postprocess      |            |              |
        | Task5  | CPU  | No       | Task0, Task4 | Task6, Task9 | Image - Crop          |            |              |
        | Task6  | CPU  | No       | Task5        | Task7        | Retinanet-preprocess  |            |              |
        | Task7  | GPU  | No       | Task6        | Task8        | Retinanet-inference   |            |              |
        | Task8  | CPU  | No       | Task7        | Task9        | Retinanet-postprocess |            |              |
        | Task9  | CPU  | No       | Task5, Task8 | Task10       | Image - Crop          |            |              |
        | Task10 | CPU  | No       | Task9        | Task11       | lprnet-preprocess     |            |              |
        | Task11 | GPU  | No       | Task10       | Task12       | lprnet-inference      |            |              |
        | Task12 | CPU  | No       | Task11       | Task13       | lprnet-postprocess    |            |              |
        | Task13 | CPU  | Yes      | Task12       | Task14       | Table - Build         |            |              |
        | Task14 | CPU  | No       | Task13       | None         | Table - Print         |            |              |
    DAG：
                                 ↑￣￣￣￣￣￣￣￣￣￣↓
        0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14
        ↓＿＿＿＿＿＿＿＿＿＿＿＿＿↑     
"""
# 阶段三测试
if TEST_STAGE == 2:
    # Pipe
    task3_conn, agent_conn3 = Pipe()
    task7_conn, agent_conn7 = Pipe()
    task11_conn, agent_conn11 = Pipe()
    
    # Queue
    size = 200
    q_0_1 = Queue(maxsize=size)
    q_0_5 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)
    q_2_3 = Queue(maxsize=size)
    q_3_4 = Queue(maxsize=size)
    q_4_5 = Queue(maxsize=size)
    q_5_6 = Queue(maxsize=size)
    q_5_9 = Queue(maxsize=size)
    q_6_7 = Queue(maxsize=size)
    q_7_8 = Queue(maxsize=size)
    q_8_9 = Queue(maxsize=size)
    q_9_10 = Queue(maxsize=size)
    q_10_11 = Queue(maxsize=size)
    q_11_12 = Queue(maxsize=size)
    q_12_13 = Queue(maxsize=size)
    q_13_14 = Queue(maxsize=size)

    # GpuAgent
    gpuAgent = GpuAgent([task3_conn, task7_conn, task11_conn])

    # CpuPipe, GpuPipe
    cap = cv2.VideoCapture("data_source/videos/new.webm")
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1, q_0_5], batch_size=1, processes=[[Image.Gen.genFromVideo, [cap,25]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize.resize, [540,960]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[q_2_3], batch_size=1, processes=[[Model.yolo.preprocess, []]])
    task3 = GpuPipe(pre_Qs=[q_2_3], next_Qs=[q_3_4], batch_size=1, processes=[[Model.yolo.inference, []]], agent_conn_handle=agent_conn3)
    task4 = CpuPipe(pre_Qs=[q_3_4], next_Qs=[q_4_5], batch_size=1, processes=[[Model.yolo.postprocess, []]])
    task5 = CpuPipe(pre_Qs=[q_0_5, q_4_5], next_Qs=[q_5_6, q_5_9], batch_size=1, processes=[[Image.Crop.crop, []]])
    task6 = CpuPipe(pre_Qs=[q_5_6], next_Qs=[q_6_7], batch_size=1, processes=[[Model.retinanet.preprocess, []]])
    task7 = GpuPipe(pre_Qs=[q_6_7], next_Qs=[q_7_8], batch_size=1, processes=[[Model.retinanet.inference, []]], agent_conn_handle=agent_conn7)
    task8 = CpuPipe(pre_Qs=[q_7_8], next_Qs=[q_8_9], batch_size=1, processes=[[Model.retinanet.postprocess, []]])
    task9 = CpuPipe(pre_Qs=[q_5_9, q_8_9], next_Qs=[q_9_10], batch_size=1, processes=[[Image.Crop.crop, []]])
    task10 = CpuPipe(pre_Qs=[q_9_10], next_Qs=[q_10_11], batch_size=1, processes=[[Model.lprnet.preprocess, []]])
    task11 = GpuPipe(pre_Qs=[q_10_11], next_Qs=[q_11_12], batch_size=1, processes=[[Model.lprnet.inference, []]], agent_conn_handle=agent_conn11)
    task12 = CpuPipe(pre_Qs=[q_11_12], next_Qs=[q_12_13], batch_size=1, processes=[[Model.lprnet.postprocess, []]])
    task13 = StatefulCpuPipe(pre_Qs=[q_12_13], next_Qs=[q_13_14], batch_size=1, processes=[[Table.Build.build, []]])
    task14 = CpuPipe(pre_Qs=[q_13_14], next_Qs=[], batch_size=1, processes=[[Table.Print.print, []]])

    # start
    gpuAgent.start()
    task0.start()
    task1.start()
    task2.start()
    task3.start()
    task4.start()
    task5.start()
    task6.start()
    task7.start()
    task8.start()
    task9.start()
    task10.start()
    task11.start()
    task12.start()
    task13.start()
    task14.start()