#!/usr/bin/bash

# https://stackoverflow.com/questions/59895/how-to-get-the-source-directory-of-a-bash-script-from-within-the-script-itself/246128#246128
# https://stackoverflow.com/questions/40282696/trap-command-explanation
# https://unix.stackexchange.com/questions/57013/zip-all-files-in-directory

# To run: 
# /mnt/c/dev/da.main/Job/shared/gp/upload_to_s3.sh gp.da.temp pika job_pika6_load
# aws s3 ls s3://gp.da.temp/kg/batch/job/pika/

# Stops scripts if any simple command fails
set -e 

BUCKET=$1
PROJECT=$2
JOB=$3

echo "CURRENT DIR ==> $PWD"
echo "BUCKET ==> $BUCKET"
echo "PROJECT ==> $PROJECT"
echo "JOB ==> $JOB"

# Run as ./mnt/c/dev/da.main/Job/shared/gp/upload_to_s3.sh BUCKET PROJECT JOB

create_working_dir() {

    # Get full directory name of the script, no matter where it is called from
    DIR="$( cd "$( dirname $"{BASH_SOURCE[0]}" )" && pwd)"

    # Create temporary directory
    WORK_DIR=$(mktemp -d -p $DIR)

    # Check if tmp dir was created
    if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
        echo "Could not create temp dir"
        exit 1 
    fi

    # delete the temp directory
    cleanup() {
        rm -rf "$WORK_DIR"
        echo "Deleted temp working directory $WORK_DIR"
    }

    # register the cleanup function to be called on the EXIT
    trap cleanup EXIT

}

# Copy all files to be zipped to temporary folder
copy_files() {

    create_working_dir

    # Steps
    if [[ -d "steps" ]]; then
        cp -r steps/*.sql steps/*.py $WORK_DIR
    fi 

    # JSON files
    if [[ $(find . -type f -name '*.json') ]] ; then 
        cp *.json $WORK_DIR
    fi

    # main.py
    if [[ -f "main.py" ]] ; then
        cp main.py $WORK_DIR
    else
        echo "NO MAIN.PY FOUND IN FOLDER"
    fi

}

zip_and_push_to_s3() {

    copy_files

    # Zip files in temporary folder
    zip -r $JOB.zip $WORK_DIR

    # Upload to s3 path
    { # try
        aws s3 cp $JOB.zip s3://$BUCKET/kg/batch/job/$PROJECT/$JOB.zip && \
        echo "UPLOAD SUCCESSFUL"
    } || { # catch
        echo "UPLOAD FAILED"
    }

}

zip_and_push_to_s3