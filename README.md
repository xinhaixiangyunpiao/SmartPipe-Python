# SmartPipe

# 测试结果
## 测试一

# 核心结构
- Task
    - 每个Task是DAG图中的一个Node。
    - 可以是CPU任务，也可以是GPU任务。
    - 默认模型的执行是GPU任务，其余操作（模型的前后处理，图片变换操作，表的修改操作）均为CPU任务。
    - 每个Task会不同大小的输入会有一个时间函数关系：t = f(input_size)
- APP
    - ServiceType
        - request-guarantee
        - best-effort
    - Qutoa
        - throughout
        - time delay
        - time delay shake
        - packet loss
    - Tasks
        - Task[]
        - DAG
    - Request Frequency

- SmartPipe
    - Pipe
        - PipeHead
            - 一种没有输出，只有输出的节点类型。
        - PipeBody
            - 有输出也有输出的节点类型。
                - CPUBody：CPU任务
                - GPUBody：GPU任务
        - PipeTail
            - 一种只有输出没有输入的节点类型。
    - Smart
        - 根据策略决定任务的batch_size。
        - 根据资源决定任务的并行度。

- Constraint
    - Resource
        - Memory
        - CPU Number
            - core number
        - GPU Number
        - CPU
            - type
        - GPU
            - type
            - memory
    - Request
        - quota
            - throughtput: request reply number / min
            - time delay: maximum acceptable time delay (ms)
            - time delay shake: time delay standard deviation (ms)
            - packet loss rate: percentage

- Strategy
    - Lazy: meet applications minimum requirements.
    - Balance: meet requirement, auto adjust to improve performance.
    - Strong: maximize node resource utilize.

# 亮点
- 提供了通用的APP任务框架，可以直接组合不同任务和数据源构建应用，函数式编程。
- 可以自适应节点资源和目标约束，自动调节每个（进程）线程的体量（任务数，或者每个任务的batch_size）以在集群资源约束下完成对设定目标的自动优化。
- GPU上的推理任务单独进程管理，减少Context开销。在PyTorch 1.7的基础上对单卡多模型执行进行了显存优化，结合调度算法隐藏模型参数传输开销。
- 对APP提供 best-effort（受理APP，尽最大努力完成目标） 或者 request-guarantee（无法保证时不受理APP）的服务，可以自行设置，同时还可以设置APP的执行目标（吞吐，时延，抖动，丢包率）。

# models
- Deeplab-Xception
- Deepsort
- East
- ESDR
- FCN
- GCN
- MTCNN
- openpose
- unet
- yolo

# functions
- Image
    - Gen
    - Crop
    - Resize
    - Show
- Table
    - Filter
    - Select
    - Merge
    - Print
- Model
    - PreProcess
    - Inference
    - PostProcess

# data sources
- images

- videos

# 目前支持的Pipe
- PipeHead
- PipeBody
    - CPUBody
    - GPuBody
- pipeTail

# 编程模式
- json文件确定配置APP
    - 从库中取资源构建APP
    - 加入系统中执行

# 编程设想
- 要构建一个APP，主要就是构建多个进程组成的DAG图。
    - 每个进程可以从模板创建，模板有以下几种：
        - SmartPipe
            - 一个智能的流水线基类。
            -计时机制
            - PipeHead，继承自PipeHead
                - 只有输出，没有输入
                - batch操作
                - process
                - 输出机制
            - PipeBody
                - 有输入也有输出
                - batch操作、
                - 输入输出机制
                - CPUBody
                    - process集合
                - GPUBody
                    - model
                    - 托管至GPUAgent
            - PipeTail
                - 只有输入，没有输出
                - batch操作
                - process

- 所有GPU相关的操作卸载到GPU上：GPUAgent