# Polly Audio Annunciator

## About

This tool will output spoken audio from Amazon AWS Polly based on the data provided to it.  This is useful to create pre-defined phrases and have the audio locally, which improves performance of your home automation and reduces ongoing costs to zero, while still giving you high-quality audio feedback.

## IMPORTANT: USING THIS SCRIPT MAY INCUR COST TO YOU

AWS charges by the character for the Polly service.  See https://aws.amazon.com/polly/ for pricing information, including their free tier offer.  Constantly using this script to generate output will certainly *cost you money*.  Use at your own risk.

## Required Installation and Configuration

An Amazon AWS account is required.

### Amazon AWS CLI

The easiest way to configure AWS on the system is using AWS CLI.  To install: 

`curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"`

`unzip awscli-bundle.zip`

`sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws`

`aws configure`

### ffmpeg

ffmpeg is used to prepend audio files, and is required regardless if you choose to prepend a file.  Installation varies by OS, but for Mac OSX simply use brew to install:

`brew update && brew install ffmpeg`

### Python Required Packages

Multiple Python libraries are required.  To install:

`pip3 install requests boto3 pydub`


## Usage

Usage instructions are provided by calling the script and appending `-h` to the end of the path.

## Example JSON file

An example JSON file is included in this package to illustrate the required and optional fields in your request.