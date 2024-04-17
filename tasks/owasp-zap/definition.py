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

        tmp_report = 'report.json'
        templates_dir = '/build-task/reporter/templates'

        filename = f'/zap-scan-for-{owner}-{repository}-{buildid}.html'

        output = run([
            'zap-baseline.py',
            '-t', target,
            '-J', tmp_report,
            '-I'
        ], timeout=900, capture_output=True)

        output = run([
            'node',
            'build-task/reporter/generate-report.js',
            '--input',
            f'/zap/wrk/{tmp_report}',
            '--output',
            filename,
            '--templateDir',
            templates_dir,
            '--target',
            target,
            '--buildId',
            buildid

        ], capture_output=True)

        # regex test on output for count
        summary_regex = r'Issue Count: (\d+)'
        match = re.search(summary_regex, output.stdout)
        try:
            count = int(match.groups()[0])
        except Exception:
            count = 0

        return dict(
            artifact=filename,
            message=None,
            count=count,
        )
