from lib.definition import BuildTask
import traceback


if __name__ == "__main__":
    try:
        task = BuildTask()
        task.set_encryption_key()
        task.parse_args()

        try:
            task.status_start()
            task.results = task.handler()
            task.upload_file()
            task.status_end()
        except NotImplementedError:
            """operator didn't write a handler"""
            task.status_error("No handler function present")
        except Exception:
            """throw task error, update"""
            task.status_error(traceback.format_exc())
    except Exception:
        """these errors are outside the class"""
        # logger might not be setup
        traceback.print_exc()
