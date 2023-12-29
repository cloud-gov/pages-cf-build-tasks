from lib.task import BaseBuildTask
import subprocess


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[['-t', '--target']]
        )

    def handler(self):
        """scan"""
        filename = 'report.html'
        subprocess.run([
            'zap-baseline.py',
            '-t', self.args['target'],
            '-r', filename
        ], timeout=900)

        return f'/zap/wrk/{filename}'
