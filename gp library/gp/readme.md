# Environment Variables

```
SNOWSQL_USER=
SNOWSQL_PWD=****
PYTHONPATH=c:\dev\da.etl\;c:\dev\da.main\Job\shared\
PYLINTRC=c:\dev\da.etl\.pylintrc
```

# Python Setup

```
conda update -all
pip install --upgrade boto3
pip install --upgrade snowflake-connector-python
```


# AWS Setup

* install: `pip install awscli --upgrade --user`

* configure: `aws configure`

```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: 
```