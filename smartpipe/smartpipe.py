import abc
import time
import threading
from multiprocessing import Process
from common import Singal

# Pipe Base Class
class SmartPipe(Process, metaclass=abc.ABCMeta):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes):
        # Process
        super().__init__()
        # time profile
        self.time_recv = 0
        self.time_process = 0
        self.time_send = 0
        # local
        self.pre_Qs = pre_Qs
        self.next_Qs = next_Qs
        self.batch_size = batch_size
        self.processes = processes

    # recv
    def recvFromQueues(self, Qs, batch_size):
        res = []
        for i in range(batch_size):
            for q in Qs:
                while q.empty():
                    pass
            line = []
            for q in Qs:
                item = q.get()
                line.append(item)
            if line[0] == Signal.End:
                break
            res.append(line)
        return res
    
    # send
    def sendToQueues(self, Qs, data, time_wait):
        for i in data:
            for q in Qs:
                q.put(i, block=True, timeout=time_wait)

    # process handle
    @abc.abstractmethod
    def handle(self, process, paras, input_data):
        pass
    
    # run
    def run(self):
        while True:
            # recv
            time_start = time.time()
            data = recvFromQueues(self.pre_Qs, self.batch_size)
            self.time_recv += time.time() - time_start

            # judge quit
            if data == None or len(data[0]) == 0:
                break

            # process
            time_start = time.time()
            for process, paras in self.processes:
                data = self.handle(process, paras, data)
            self.time_process += time.time() - time_start

            # send
            time_start = time.time()
            sendToQueues(self.next_Qs, self.batch_size, 3)
            self.time_send += time.time() - time_start

        # send finish signal
        for q in next_Qs:
            q.put(Signal.End, block=True, timeout=3)

# CpuPipe
class CpuPipe(SmartPipe):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes):
        super().__init__()
    
    # handle
    def handle(self, process, paras, input_data):
        # 直接在当前进程中执行
        process(input_data, paras)

# StatefulCpuPipe
class StatefulCpuPipe(SmartPipe):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes):
        super().__init__()
        self.table = []
    
    # handle
    def handle(self, process, paras, input_data):
        # process会更新状态表
        process(input_data, paras, self.table)

# GpuPipe
class GpuPipe(SmartPipe):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes, agent_conn_handle):
        super().__init__()
        self.agent_conn_handle = agent_conn_handle

    # handle
    def handle(self, process, paras, input_data):
        # 托管到GPUAgent执行
        self.agent_conn_handle.send([process, paras, input_data])
        self.agent.recv()

# GPUAgent
class GpuAgent(Process):
    # init
    def __init__(self, task_conns):
        super().__init__()
        # 加载会用到的模型

        # 任务队列
        self.task_conns = task_conns
        self.tasks_Q = Queue(maxsize=200)
        self.recv_thread = threading.Thread(target=self.recv)
        self.recv_thread.start()

    # recv
    def recv(self):
        # round robin
        while True:
            for task_conn in self.task_conns:
                if task_conn.poll():
                    task = task_conn.recv()
                    if self.tasks_Q.full():
                        raise Exception("task_Q is full.")
                    self.tasks_Q.put([task_conn, task])
            time.sleep(0.02)

    # run
    def run(self):
        while True:
            # 从任务队列头取出任务
            while self.tasks_Q.empty():
                pass
            task_conn, task = self.tasks_Q.get()

            # 执行任务
            process, paras, input_data = task
            process(paras, input_data)

            # 告知进程执行完毕
            task_conn.send("finished.")                