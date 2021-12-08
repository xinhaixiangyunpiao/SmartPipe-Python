from multiprocessing import Pipe, Queue
from smartpipe import CpuPipe, GpuPipe, GpuAgent
from functions.functions import Image, Table
from models.models import yolo, retinanet, lprnet

"""
    测试内容：使用smartpipe和multiProcessing中的Pipe和Queue高效构建APP
    测试方式：构建一个车牌号识别的APP
    APP：车牌号识别，输出每一帧中的车辆车牌号。
    APP流程：
        | Name   | Type | Input        | Output       | Function              | Params     |
        | Task0  | CPU  | None         | Task1, Task5 | Image - Gen           | video, fps |
        | Task1  | CPU  | Task0        | Task2        | Image - Resize        | h,w        |
        | Task2  | CPU  | Task1        | Task3        | yolo-preprocess       |            |
        | Task3  | GPU  | Task2        | Task4        | yolo-inference        |            |
        | Task4  | CPU  | Task3        | Task5        | yolo-postprocess      |            |
        | Task5  | CPU  | Task0, Task4 | Task6, Task9 | Image - Crop          | h,w        |
        | Task6  | CPU  | Task5        | Task7        | Retinanet-preprocess  |            |
        | Task7  | GPU  | Task6        | Task8        | Retinanet-inference   |            |
        | Task8  | CPU  | Task7        | Task9        | Retinanet-postprocess |            |
        | Task9  | CPU  | Task5, Task8 | Task10       | Image - Crop          | h,w        |
        | Task10 | CPU  | Task9        | Task11       | lprnet-preprocess     |            |
        | Task11 | GPU  | Task10       | Task12       | lprnet-inference      |            |
        | Task12 | CPU  | Task11       | Task13       | lprnet-postprocess    |            |
        | Task13 | CPU  | Task12       | Task14       | Table - Gen           |            |
        | Task14 | CPU  | Task13       | None         | Table - Print         |            | 
    DAG：
                                 ↑￣￣￣￣￣￣￣￣￣￣↓
        0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14
        ↓＿＿＿＿＿＿＿＿＿＿＿＿＿↑     
"""

if __name__ == "__main__":
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
    task0 = CpuPipe(pre_Qs=[], next_Qs=[q_0_1, q_0_5], batch_size=1, processes=[[Image.Gen, [video,fps]]])
    task1 = CpuPipe(pre_Qs=[q_0_1], next_Qs=[q_1_2], batch_size=1, processes=[[Image.Resize, [h,w]]])
    task2 = CpuPipe(pre_Qs=[q_1_2], next_Qs=[q_2_3], batch_size=1, processes=[[yolo.preprocess, [h,w]]])
    task3 = GpuPipe(pre_Qs=[q_2_3], next_Qs=[q_3_4], batch_size=1, processes=[[yolo.inference, []]], agent_conn_handle=agent_conn3)
    task4 = CpuPipe(pre_Qs=[q_3_4], next_Qs=[q_4_5], batch_size=1, processes=[[yolo.postprocess, []]])
    task5 = CpuPipe(pre_Qs=[q_0_5, q_4_5], next_Qs=[q_5_6, q_5_9], batch_size=1, processes=[[Image.Crop, [h,w]]])
    task6 = CpuPipe(pre_Qs=[q_5_6], next_Qs=[q_6_7], batch_size=1, processes=[[retinanet.preprocess, []]])
    task7 = GpuPipe(pre_Qs=[q_6_7], next_Qs=[q_7_8], batch_size=1, processes=[[retinanet.inference, []]], agent_conn_handle=agent_conn7)
    task8 = CpuPipe(pre_Qs=[q_7_8], next_Qs=[q_8_9], batch_size=1, processes=[[retinanet.postprocess, []]])
    task9 = CpuPipe(pre_Qs=[q_5_9, q_8_9], next_Qs=[q_9_10], batch_size=1, processes=[[Image.Crop, [h,w]]])
    task10 = CpuPipe(pre_Qs=[q_9_10], next_Qs=[q_10_11], batch_size=1, processes=[[lprnet.preprocess, []]])
    task11 = GpuPipe(pre_Qs=[q_10_11], next_Qs=[q_11_12], batch_size=1, processes=[[lprnet.inference, []]], agent_conn_handle=agent_conn11)
    task12 = CpuPipe(pre_Qs=[q_11_12], next_Qs=[q_12_13], batch_size=1, processes=[[lprnet.postprocess, []]])
    task13 = CpuPipe(pre_Qs=[q_12_13], next_Qs=[q_13_14], batch_size=1, processes=[[Table.Gen, []]])
    task14 = CpuPipe(pre_Qs=[q_13_14], next_Qs=[], batch_size=1, processes=[[Table.print, []]])

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
    task11.start()
    task12.start()
    task13.start()
    task14.start()


