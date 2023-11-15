from definition import MyTask

if __name__ == "__main__":
    try:
        task = MyTask()
        task.parse_args()

        try:
            task.status_start()
            task.filename = task.handler()
            task.upload_file()
            task.status_end()
        except NotImplementedError:
            """operator didn't write a handler"""
            task.status_error('No handler function present')
        except Exception as e:
            """throw task error, update"""
            task.status_error(e)
    except Exception as e:
        """these errors are outside class"""
        task.status_error(e)
