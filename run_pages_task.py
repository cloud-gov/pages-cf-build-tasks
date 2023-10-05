#!/usr/bin/python
import argparse
import subprocess
import boto3
import requests
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an owasp zap scan task')
    parser.add_argument('-t', '--target', dest='target',
                        help='The target URL to scan')
    parser.add_argument('-p', '--params', dest='params',
                        help='A JSON encoded string',
                        metavar="'{\"foo\": \"bar\"}'")
    args = parser.parse_args()

    if args.params:
        params = json.loads(args.params)

    try:
        # Scan
        subprocess.run([
            'zap-baseline.py',
            '-t', args.target, 
            '-r', 'report.html'
        ], timeout=900)

        # Upload
        key = f'_tasks/artifacts/{params["TASK_ID"]}/report.html'
        s3_client = boto3.client(
            service_name='s3',
            aws_access_key_id=params["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=params["AWS_SECRET_ACCESS_KEY"],
            region_name=params["AWS_DEFAULT_REGION"]
        )

        s3_client.upload_file(
            Filename='/zap/wrk/report.html',
            Bucket=params["BUCKET"],
            Key=key,
        )

        # Update Status
        requests.put(params["STATUS_CALLBACK"], json={
            "artifact": key,
            "status": "success"
        })
    except Exception as e:
        print(e)
        requests.put(params["STATUS_CALLBACK"], json={
            "status": "error"
        })
