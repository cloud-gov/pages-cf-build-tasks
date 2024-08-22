import argparse
import boto3
import json
import os
import requests
import logging
from lib.utils import decrypt, decrypt_dict_values


class BaseBuildTask:
    def __init__(self, extra_args):
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
        self.logger = logging.getLogger(name=type(self).__name__)
        self.parser = argparse.ArgumentParser()

        # single default argument
        self.parser.add_argument('-p', '--params', dest='params',
                                 help='A JSON encoded string',
                                 metavar="'{\"foo\": \"bar\"}'")

        # custom arguments
        for arg in extra_args:
            self.parser.add_argument(*arg)

    def parse_args(self):
        args = self.parser.parse_args()

        # default argument handling
        encrypted_params = json.loads(args.params)
        params = decrypt_dict_values(encrypted_params, self.encryption_key)

        self.status_callback = params["STATUS_CALLBACK"]
        self.task_id = params["TASK_ID"]
        self.aws_default_region = params["AWS_DEFAULT_REGION"]
        self.aws_access_key_id = params["AWS_ACCESS_KEY_ID"]
        self.aws_secret_access_key = params["AWS_SECRET_ACCESS_KEY"]
        self.bucket = params["BUCKET"]

        self.s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_default_region
        )

        self.args = {}
        # custom argument handling
        for k, v in args.__dict__.items():
            if k != 'params':
                self.args[k] = decrypt(v, self.encryption_key)

    def set_encryption_key(self):
        deploy_env = os.getenv("DEPLOY_ENV")
        vcap_services = json.loads(os.getenv("VCAP_SERVICES", "{}"))

        encryption_ups = next(
            ups
            for ups in vcap_services["user-provided"]
            if ups["name"] == f"pages-{deploy_env}-encryption"
        )

        encryption_key = encryption_ups["credentials"]["key"]

        self.encryption_key = encryption_key

    def status_start(self):
        """callback"""
        self.logger.info(f'Task {self.task_id} is starting')
        requests.put(self.status_callback, json={
            "status": "processing"
        })

    def status_end(self):
        """callback"""
        self.logger.info(f'Task {self.task_id} is complete')
        requests.put(self.status_callback, json={
            "artifact": self.key,
            "message": self.results["message"],
            "count": self.results["count"],
            "status": "success"
        })

    def status_error(self, err):
        """callback"""
        self.logger.error(f'Task {self.task_id} errored: {err}')
        requests.put(self.status_callback, json={
            "status": "error",
            "message": err
        })

    def upload_results(self):
        """upload file to S3"""
        results_dir = self.results["artifact"]
        self.key = f'_tasks/artifacts/{self.task_id}/'

        for filename in os.listdir(results_dir):
            base = os.path.basename(filename)
            s3key = f'{self.key}{base}'

            self.s3_client.upload_file(
                Filename=f'{results_dir}/{filename}',
                Bucket=self.bucket,
                Key=s3key,
            )

    def handler():
        raise NotImplementedError
