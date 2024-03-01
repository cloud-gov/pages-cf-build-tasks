from lib.task import BaseBuildTask
import subprocess
import psutil
import time

class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[['-t', '--target']]
        )

    def handler(self):
        """scan"""
        filename = 'report.html'
        self.logger.info(f'Scanning {self.args["target"]}')

        disk = psutil.disk_usage("/")
        self.logger.info(f'CPU Usage Percentage: {psutil.cpu_percent()}')
        self.logger.info(f'Memory Usage Percentage: {psutil.virtual_memory().percent}')
        self.logger.info(f'Disk usage: {disk.used} / {disk.total}')

        time.sleep(3600)

        subprocess.run([
            'zap-baseline.py',
            '-t', self.args['target'],
            '-r', filename
        ], timeout=900)

        return f'/zap/wrk/{filename}'
