import re

from lib.task import BaseBuildTask
from lib.utils import run


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[
                ['-t', '--target'],
                ['-b', '--buildid'],
                ['-o', '--owner'],
                ['-r', '--repository']]
        )

    def handler(self):
        """scan"""
        target = self.args['target']
        buildid = self.args['buildid']
        owner = self.args['owner']
        repository = self.args['repository']

        filename = f'zap-scan-for-{owner}-{repository}-{buildid}.html'

        output = run([
            'zap-baseline.py',
            '-t', target,
            '-r', filename,
        ], timeout=900, capture_output=True)

        # regex test on output for count
        summary_regex = r'FAIL-NEW:\s+(\d+)\s+FAIL-INPROG:\s+(\d+)\s+WARN-NEW:\s+(\d+)\s+WARN-INPROG:\s+(\d+)\s+INFO:\s+(\d+)\s+IGNORE:\s+(\d+)\s+PASS:\s+(\d+)'  # noqa: E501
        match = re.search(summary_regex, output.stdout)

        # sum everything except pass
        try:
            count = sum([int(n) for n in match.groups()[0:6]])
        except Exception:
            count = 0

        return dict(
            artifact=f'/zap/wrk/{filename}',
            message=None,
            count=count,
        )
