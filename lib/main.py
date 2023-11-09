from definition import MyTask

if __name__ == "__main__":
    try:
        MyTask(params, target, kwargs)
        MyTask.argument_parser()
        # catch task initialization failure?

        try:
            MyTask.status_start()
            MyTask.handler()
            MyTask.store_thing()
            MyTask.status_end()
        except SpecificException:
            """throw task error, update"""
            MyTask.status_error()
    except Exception as e:
        """these errors are outside class"""

