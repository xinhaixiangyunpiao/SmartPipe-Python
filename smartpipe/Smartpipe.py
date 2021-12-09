import os
import abc
import time
import threading
from multiprocessing import Process
from .Common import Signal

# Pipe Base Class
class SmartPipe(Process, metaclass=abc.ABCMeta):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes):
        # Process
        super().__init__()
        # time profile
        self.cnt = 0
        self.drop_num = 0
        self.time_recv = 0
        self.time_process = 0
        self.time_send = 0
        # local
        self.pre_Qs = pre_Qs
        self.next_Qs = next_Qs
        self.batch_size = batch_size
        self.processes = processes
        self.name = str([i[0].__name__ for i in self.processes])

    # recv
    def recvFromQueues(self):
        if len(self.pre_Qs) == 0:
            return None
        res = []
        for i in range(self.batch_size):
            line = []
            for q in self.pre_Qs:
                while q.empty():
                    pass
                item = q.get()
                line.append(item)
            if line[0] is Signal.End:
                break
            res.append(line)
        return res
    
    # send
    def sendToQueues(self, data, drop=False, time_wait=0):
        if len(self.next_Qs) == 0:
            return None
        for i in data:
            if drop:
                for q in self.next_Qs:
                    if q.full():
                        self.drop_num += 1
                        return None
            for q in self.next_Qs:
                q.put(i, block=True, timeout=time_wait)

    # print result
    def print_result(self):
        print('\033[1;35m' + self.name + ':\033[0m')
        print('\033[1;36m   Total Number: \033[0m', self.cnt)
        if len(self.pre_Qs) == 0:
            print('\033[1;36m   Drop Number: \033[0m', self.drop_num)
        print('\033[1;36m   Time Recv: \033[0m', round(self.time_recv, 4), '\033[1;36ms\033[0m')
        print('\033[1;36m   Time Process: \033[0m', round(self.time_process, 4), '\033[1;36ms\033[0m')
        print('\033[1;36m   Time Send: \033[0m', round(self.time_send, 4), '\033[1;36ms\033[0m')
        print('\033[1;36m   Time Total: \033[0m', round(self.time_recv + self.time_process + self.time_send, 4), '\033[1;36ms\033[0m')

    # process handle
    @abc.abstractmethod
    def handle(self, obj, input_data):
        pass
    
    # run
    def run(self):
        # Function object init.
        self.function_objs = []
        for process, params in self.processes:
            self.function_objs.append(process(params))
        # main loop
        while True:
            # recv
            time_start = time.perf_counter()
            data = self.recvFromQueues()
            self.time_recv += time.perf_counter() - time_start

            # judge quit - normal
            if data is not None:
                if len(data) == 0:
                    break

            # process
            time_start = time.perf_counter()
            for obj in self.function_objs:
                data = self.handle(obj, data)
            self.time_process += time.perf_counter() - time_start

            # judge quit - gen
            if len(self.next_Qs) != 0:
                if data is None:
                    break

            # send
            time_start = time.perf_counter()
            if len(self.pre_Qs) == 0:
                self.sendToQueues(data, drop=True)
            else:
                self.sendToQueues(data, time_wait=3)
            self.time_send += time.perf_counter() - time_start

            # local
            self.cnt += 1
            # if self.cnt % 50 == 0:
            #     print(self.name, self.cnt)

        # send finish signal
        for q in self.next_Qs:
            q.put(Signal.End, block=True, timeout=3)

        # release
        for obj in self.function_objs:
            obj.finish()
        
        # print result
        self.print_result()

# CpuPipe
class CpuPipe(SmartPipe):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes):
        super().__init__(pre_Qs, next_Qs, batch_size, processes)

    # handle
    def handle(self, obj, input_data):
        res = []
        if input_data == None:
            res = obj.loop()
        else:
            res = obj.loop(input_data)
        return res

# GpuPipe
class GpuPipe(SmartPipe):
    # init
    def __init__(self, pre_Qs, next_Qs, batch_size, processes, agent_conn_handle):
        super().__init__(pre_Qs, next_Qs, batch_size, processes)
        self.agent_conn_handle = agent_conn_handle

    # handle
    def handle(self, obj, input_data):
        # 托管到GPUAgent执行
        self.agent_conn_handle.send([obj.loop, input_data])
        res = self.agent.recv()
        return res

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
            process, input_data = task
            res = process(input_data)

            # 返回结果
            task_conn.send(res)                