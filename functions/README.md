# Image
## Gen
- opencv的VideoCapture对象传递到另一个进程就不能read了，所以使用此方法的Pipe应是一个带状态的Pipe
- 震惊，python调用类中的函数，就会进入另一个进程?
- 一个继承Process的类，其init函数和run函数是两个进程。
- 本质是使用Process创建进程后，其初始化函数在父进程中，只有run函数在子进程中。