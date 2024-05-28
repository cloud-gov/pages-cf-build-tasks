from lib import BaseBuildTask
from tempfile import NamedTemporaryFile
from humanize import naturalsize


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[['-t', '--target']]
        )

    def handler():
        """write a temporary file"""
        # access arg with self.args["target"]
        with NamedTemporaryFile(delete_on_close=False) as ntf:
            ntf.write(naturalsize(1000000))
            ntf.close()
            return ntf
