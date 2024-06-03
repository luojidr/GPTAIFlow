import signal

class TimeoutError(Exception):
    pass

def timeout_decorator(timeout=10):
    def timeout_function(f):
        def f2(*args,**kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError()

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout) # trigger alarm in timeout seconds
            try:
                retval = f(*args,**kwargs)
            finally:
                signal.signal(signal.SIGALRM, old_handler) # restore the existed signal handler
            signal.alarm(0) # clear alarm
            return retval
        return f2
    return timeout_function
