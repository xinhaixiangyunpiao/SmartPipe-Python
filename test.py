import os
import cv2
from multiprocessing import Pipe, Queue, Process
from smartpipe import CpuPipe, GpuPipe, GpuAgent
from functions import Image, Table
from models import Model

# select test
TEST_STAGE = 0

# time delay test
if TEST_STAGE == -1:
    # Queue
    size = 200
    q_0_1 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)
    q_2_3 = Queue(maxsize=size)
    q_3_4 = Queue(maxsize=size)
    q_4_5 = Queue(maxsize=size)
    q_5_6 = Queue(maxsize=size)
    q_6_7 = Queue(maxsize=size)
    q_7_8 = Queue(maxsize=size)
    q_8_9 = Queue(maxsize=size)
    q_9_10 = Queue(maxsize=size)

    # CpuPipe
    video_path = "/data/lx/SmartPipe/data_source/videos/out_960*540.avi"
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1], batch_size=1, processes=[[Image.Gen.genFromVideo, [video_path,10]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Trans.trans, []]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[q_2_3], batch_size=1, processes=[[Image.Trans.trans, []]])
    task3 = CpuPipe(pre_Qs=[q_2_3], next_Qs=[q_3_4], batch_size=1, processes=[[Image.Trans.trans, []]])
    task4 = CpuPipe(pre_Qs=[q_3_4], next_Qs=[q_4_5], batch_size=1, processes=[[Image.Trans.trans, []]])
    task5 = CpuPipe(pre_Qs=[q_4_5], next_Qs=[q_5_6], batch_size=1, processes=[[Image.Trans.trans, []]])
    task6 = CpuPipe(pre_Qs=[q_5_6], next_Qs=[q_6_7], batch_size=1, processes=[[Image.Trans.trans, []]])
    task7 = CpuPipe(pre_Qs=[q_6_7], next_Qs=[q_7_8], batch_size=1, processes=[[Image.Trans.trans, []]])
    task8 = CpuPipe(pre_Qs=[q_7_8], next_Qs=[q_8_9], batch_size=1, processes=[[Image.Trans.trans, []]])
    task9 = CpuPipe(pre_Qs=[q_8_9], next_Qs=[q_9_10], batch_size=1, processes=[[Image.Trans.trans, []]])
    task10 = CpuPipe(pre_Qs=[q_9_10], next_Qs=[], batch_size=1, processes=[[Image.Trans.trans, []]])
    
    # start
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

"""
    ???????????????
    ?????????????????????SmartPipe???CPU??????API
    ?????????????????????????????????????????????CPU APP
    APP????????????Resize
    APP?????????
        | Name   | Type | Stateful | Input | Output | Function       | Params       | State        |
        | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen    | path,fps     | videoCapture |
        | Task1  | CPU  | No       | Task0 | Task2  | Image - Resize | h,w          |              |
        | Task2  | CPU  | Yes      | Task1 | None   | Image - Save   | path,h,w,fps | videoWriter  |
    DAG???
        0 -> 1 -> 2
"""

if TEST_STAGE == 0:
    # Queue
    size = 200
    q_0_1 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)

    # CpuPipe
    video_path = "/data/lx/SmartPipe/data_source/videos/road.webm"
    save_path = "/data/lx/SmartPipe/data_source/videos/out.avi"
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1], batch_size=1, processes=[[Image.Gen.genFromVideo, [video_path,25]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize.resize, [540,960]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[], batch_size=1, processes=[[Image.Save.save, [save_path,540,960,25]]])

    # start 
    task0.start()
    task1.start()
    task2.start()

""" 
    ???????????????
    ?????????????????????SmartPipe???Crop??????????????????Smart???????????????????????????batch_size
    ????????????????????????????????????????????????????????????
    APP?????????????????????
    APP?????????
        | Name   | Type | Stateful | Input | Output | Function     | Params      | State        |
        | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen  | path,fps    | videoCapture |
        | Task1  | CPU  | No       | Task0 | Task2  | Image - Crop | h1,w1,h2,w2 |              |
        | Task2  | CPU  | Yes      | Task1 | None   | Image - Save | path        | videoWriter  |
    DAG???
        0 -> 1 -> 2
"""
if TEST_STAGE == 1:
    # Queue
    size = 200
    q_0_1 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)

    # CpuPipe
    video_path = "/data/lx/SmartPipe/data_source/videos/out_1902*1080.avi.webm"
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1], batch_size=1, processes=[[Image.Gen.genFromVideo, [video_path,20]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Crop.crop_with_params, [h1,h2,w1,w2]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[], batch_size=1, processes=[[Image.Save.save, [save_path]]])

    # start 
    task0.start()
    task1.start()
    task2.start()

"""
    ???????????????
    ????????????????????????????????????????????????????????????????????????
    ???????????????resize???APP???resize???????????????????????????
    APP????????????resize???????????????
    APP?????????
        | Name   | Type | Stateful | Input | Output | Function       | Params    | State        |
        | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen    | path,fps  | videoCapture |
        | Task1  | CPU  | No       | Task0 | Task2  | Image - Resize | h,w       |              |
        | Task2  | CPU  | Yes      | Task1 | None   | Image - Save   | path      | videoWriter  | 
    DAG???
        0 -> 1 -> 2
    Execute:
        0 -> 1 -> 2
             1
"""
if TEST_STAGE == 2:
    # Queue
    size = 200
    q_0_1 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)

    # CpuPipe
    video_path = "/data/lx/SmartPipe/data_source/videos/new.webm"
    save_path = "/data/lx/SmartPipe/data_source/videos/out.avi"
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1], batch_size=1, processes=[[Image.Gen.genFromVideo, [video_path,20]]])
    task1_0 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize.resize, [540,960]]])
    task1_1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize.resize, [540,960]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[], batch_size=1, processes=[[Image.Save.save, [save_path]]])

    # start 
    task0.start()
    task1_0.start()
    task1_1.start()
    task2.start()

"""
    ???????????????
    ?????????????????????SmartPipe???CPU???GPU??????API
    ??????????????????????????????????????????APP?????????????????????
    APP????????????????????????????????????
    APP?????????
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
    # Queue
    size = 0
    q_0_1 = Queue(maxsize=size)
    q_1_2 = Queue(maxsize=size)
    q_2_3 = Queue(maxsize=size)
    q_3_4 = Queue(maxsize=size)
    q_4_5 = Queue(maxsize=size)
    q_5_6 = Queue(maxsize=size)
    q_6_7 = Queue(maxsize=size)
    q_7_8 = Queue(maxsize=size)

    # CpuPipe and GpuPipe
    video_path = "/data/lx/SmartPipe/data_source/videos/new.webm"
    save_path = "/data/lx/SmartPipe/data_source/videos/out.avi"
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1], batch_size=1, processes=[[Image.Gen.genFromVideo, [video_path,25]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize.resize, [540,960]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[q_2_3], batch_size=1, processes=[[Model.yolo.preprocess, []]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[], batch_size=1, processes=[[Image.Save.save, [save_path]]])


"""
    ???????????????
    ??????????????????GPU??????,DAG??????????????????
    ?????????????????????????????????????????????APP
    APP?????????????????????????????????????????????????????????
    APP?????????
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
    DAG???
                                 ????????????????????????????????????
        0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14
        ?????????????????????????????????????????????     
"""
# ???????????????
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