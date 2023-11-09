import argparse
import boto3
import requests

class BuildTask:
    def __init__(self, params, parser):
        pass

    def argument_parser():
        parser = argparse.ArgumentParser(description='Run an owasp zap scan task')
        parser.add_argument('-t', '--target', dest='target',
                            help='The target URL to scan')
        parser.add_argument('-p', '--params', dest='params',
                            help='A JSON encoded string',
                            metavar="'{\"foo\": \"bar\"}'")
        args = parser.parse_args()

    def status_start():
        """callback"""

    def status_end():
        """callback"""

    def status_error():
        """callback"""

    def upload_file():
        """"""

    def handler():
        NotImplementedError