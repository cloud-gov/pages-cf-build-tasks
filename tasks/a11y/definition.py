from lib.task import BaseBuildTask
import subprocess
from scraper.spider import process, A11ySpider


class BuildTask(BaseBuildTask):
    def __init__(self):
        super().__init__(
            extra_args=[['-t', '--target']]
        )

    def handler(self):
        """scan"""
        filename = 'report.html'

        data = []  # accumulates the urls during .start()
        process.crawl(A11ySpider, target=self.args['target'], data=data)
        process.start()

        for url in data:
            subprocess.run([
                'axe',
                '--chrome-options="no-sandbox,disable-setuid-sandbox,disable-dev-shm-usage"',
                url,
                '--dir',
                'results'
            ], timeout=900)

        return f'{filename}'
