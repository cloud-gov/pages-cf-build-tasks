from lib import BuildTask
from tempfile import NamedTemporaryFile
from humanize import naturalsize


class MyTask(BuildTask):
    def __init__(self):
        self._extra_parsers

    def handler():
        """do my thing"""
        with NamedTemporaryFile(delete_on_close=False) as ntf:
            ntf.write(naturalsize(1000000))
            ntf.close()
            return ntf
    