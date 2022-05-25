#!/bin/bash

whoami

echo "No profile command"

aws s3 ls

echo "With HCP"

aws s3 ls --profile hcp

export AWS_CONFIG_FILE=/home/chiaracaldinelli/.aws/credentials

echo "Explicit path specified"

echo "No profile command"

aws s3 ls

echo "With HCP"

aws s3 ls --profile hcp
