import threading

class Async_Handler(object):
    def __init__(self, data, method, callback, callback_data):
        self.data = data
        self.method = method
        self.callback = callback
        self.callback_data = callback_data

    def execute(self):
        self.execute_without_callback()
        self.callback(self.callback_data)

    def execute_without_callback(self):
        thr = threading.Thread(target=self.method, args=self.data, kwargs={})
        thr.start() # will run "foo"


class Async_Handler_Queue(Async_Handler):
    def __init__(self, method, callback, queue, data, kwargs={}):
        self.exec_method = method
        Async_Handler.__init__(self, data, self.function, callback, None)
        self.queue = queue
        self.kwargs = kwargs

    def execute(self):
        function = self.function
        if len(self.data) == 0:
            function = self.function_without_data
        thr = threading.Thread(target=function, args=self.data, kwargs=self.kwargs)
        thr.start() # will run "foo"

        data = self.queue.get()
        if len(self.kwargs) > 0:
            self.callback(data, **self.kwargs)
        else:
            self.callback(data)

    def function(self, data, **kwargs):
        if len(kwargs) > 0:
            result = self.exec_method(data, **kwargs)
        else:
            result = self.exec_method(data)
        self.queue.put(result)

    def function_without_data(self):
        result = self.exec_method()
        self.queue.put(result)