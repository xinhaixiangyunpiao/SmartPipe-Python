# SmartPipe

# 测试
## 阶段一
- 测试内容：测试SmartPipe中CPU相关API
- 测试方式：测试一个简单的三阶段CPU APP
- APP：视频流Resize
- APP流程：
    | Name   | Type | Stateful | Input | Output | Function       | Params       | State        |
    | ------ | ---- | -------- | ----- | ------ | ---------------| ------------ | ------------ |
    | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen    | path,fps     | videoCapture |
    | Task1  | CPU  | No       | Task0 | Task2  | Image - Resize | h,w          |              |
    | Task2  | CPU  | Yes      | Task1 | None   | Image - Save   | path,h,w,fps | videoWriter  |
- DAG：
```
    0 -> 1 -> 2
```
- 测试代码：
![测试代码](https://github.com/xinhaixiangyunpiao/MarkDown_Image_Repository/blob/master/5.png?raw=true)
- 预期结果：
    - 根据Profile：
        - Task0：gen 4k :
- 测试结果：
![测试结果](https://github.com/xinhaixiangyunpiao/MarkDown_Image_Repository/blob/master/6.png?raw=true)

## 阶段二
- 测试内容：测试SmartPipe中Crop操作，并验证Smart程序的健壮性，验证batch_size
- 测试方式：裁剪图片中的某个部分，输出视频
- APP：裁剪中心区域
- APP流程：
    | Name   | Type | Stateful | Input | Output | Function     | Params      | State        |
    | ------ | ---- | -------- | ----- | ------ | ------------ | ----------- | ------------ |
    | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen  | path,fps    | videoCapture |
    | Task1  | CPU  | No       | Task0 | Task2  | Image - Crop | h1,w1,h2,w2 |              |
    | Task2  | CPU  | Yes      | Task1 | None   | Image - Save | path        | videoWriter  |
- DAG：
```
    0 -> 1 -> 2
```
- 测试结果：

## 阶段三
- 测试内容：测试多队列，以及多队列对性能的积极影响
- 测试方式：resize的APP，resize使用多个进程去做。
- APP：视频流resize并输入视频
- APP流程：
    | Name   | Type | Stateful | Input | Output | Function       | Params    | State        |
    | ------ | ---- | -------- | ----- | ------ | -------------- | --------- | ------------ |
    | Task0  | CPU  | Yes      | None  | Task1  | Image - Gen    | path,fps  | videoCapture |
    | Task1  | CPU  | No       | Task0 | Task2  | Image - Resize | h,w       |              |
    | Task2  | CPU  | Yes      | Task1 | None   | Image - Save   | path      | videoWriter  | 
- DAG：
```
    0 -> 1 -> 2
```
- Execute：
```
    0 -> 1 -> 2
         1
```
- 测试结果：

## 阶段四
- 测试内容：测试SmartPipe中CPU和GPU相关API
- 测试方式：构造一个车辆识别的APP，并成功运行。
- APP：车辆图片裁剪并输出视频
- APP流程：
    | Name   | Type | Stateful | Input        | Output       | Function              | Params     | State        |
    | ------ | ---- | -------- | ------------ | ------------ | --------------------- | ---------- | ------------ |
    | Task0  | CPU  | Yes      | None         | Task1        | Image - Gen           | path,fps   | videoCapture |
    | Task1  | CPU  | No       | Task0        | Task2        | Image - Resize        | h,w        |              |
    | Task2  | CPU  | No       | Task1        | Task3        | yolo-preprocess       |            |              |
    | Task3  | GPU  | No       | Task2        | Task4        | yolo-inference        |            |              |
    | Task4  | CPU  | No       | Task3        | Task5        | yolo-postprocess      |            |              |
    | Task5  | CPU  | No       | Task0, Task4 | Task6        | Image - Crop          |            |              |
    | Task6  | CPU  | No       | Task5        | Task1        | Image - Resize        | h,w        |              |
    | Task7  | CPU  | Yes      | Task6        | None         | Image - Save          | path       | videoWriter  |
- DAG：
```
    0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
```
- 测试结果：


## 阶段五
- 测试内容：多GPU任务,DAG图带分支测试
- 测试方式：构建一个车牌号识别的APP
- APP：车牌号识别，输出每一帧中的车辆车牌号
- APP流程：
    | Name   | Type | Stateful | Input        | Output       | Function              | Params     | State        |
    | ------ | ---- | -------- | ------------ | ------------ | --------------------- | ---------- | ------------ |
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
- DAG：
```
                                ↑￣￣￣￣￣￣￣￣￣￣↓
    0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14
    ↓＿＿＿＿＿＿＿＿＿＿＿＿＿↑     
```
- 测试结果：