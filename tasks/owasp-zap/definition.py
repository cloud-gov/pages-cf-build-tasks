from lib import BuildTask
import subprocess


class MyTask(BuildTask):
    def __init__(self):
        # need to add "target" arg parser
        self._extra_parsers

    def handler():
        """scan"""
        subprocess.run([
            'zap-baseline.py',
            '-t', args.target, 
            '-r', 'report.html'
        ], timeout=900)
    