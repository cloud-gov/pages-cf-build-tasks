from lib.task import BaseBuildTask
import subprocess


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[['-t', '--target']]
        )

    def handler(self):
        """scan"""
        report = 'report.html'
        subprocess.run([
            'zap-baseline.py',
            '-t', self.args['target'],
            '-r', report
        ], timeout=900)

        subprocess.run([
            'node',
            'build-task/reporter/generate-report.js',
            '--input',
            report,
            '--output',
            filename,
            '--target',
            target
            
        ])

        # bundle
        filename = f'/vulnerability-scan-for-{owner}-{repository}-{buildid}'  # noqa: E501
        return f'/zap/wrk/{filename}'
