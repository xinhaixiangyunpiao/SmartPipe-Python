from enum import Enum

# 在不同管道间传输的信号
class Signal(Enum):
    End = 0
    AskForGpuResource = 1
    Accept = 2
    Finished = 3