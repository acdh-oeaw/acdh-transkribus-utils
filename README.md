# acdh-transkribus-utils

[![PyPI version](https://badge.fury.io/py/acdh-transkribus-utils.svg)](https://badge.fury.io/py/acdh-transkribus-utils)
[![flake8 Lint](https://github.com/acdh-oeaw/acdh-transkribus-utils/actions/workflows/lint.yml/badge.svg)](https://github.com/acdh-oeaw/acdh-transkribus-utils/actions/workflows/lint.yml)
[![Test](https://github.com/acdh-oeaw/acdh-transkribus-utils/actions/workflows/test.yml/badge.svg)](https://github.com/acdh-oeaw/acdh-transkribus-utils/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/acdh-oeaw/acdh-transkribus-utils/graph/badge.svg?token=QOY62C0X5Y)](https://codecov.io/gh/acdh-oeaw/acdh-transkribus-utils)

A python package providing some utility functions for interacting with the [Transkribus-API](https://transkribus.eu/wiki/index.php/REST_Interface)


## Installation

`pip install acdh-transkribus-utils`


## Usage

### Authentication

Set Transkribus-Credentials as environment variables: 

```bash
export TRANSKRIBUS_USER=some@mail.com
export TRANSKRIBUS_PASSWORD=verysecret
```
(or create a file called `env.secret` similar to `env.dummy` and run  `source export_env_variables.sh`)
you can pass in your credentials also as params e.g. 

```python
import os

from transkribus_utils.transkribus_utils import ACDHTranskribusUtils


tr_user = os.environ.get("TRANSKRIBUS_USER")
tr_pw = os.environ.get("TRANSKRIBUS_PASSWORD")

client = ACDHTranskribusUtils(user=tr_user, password=tr_pw)
```

### List all collections

```python
collections = client.list_collections()
for x in collections[-7:]:
    print(x["colId"], x["colName"])

# 188933 bv-play
# 188991 Kasten_blau_45_11
# 190357 acdh-transkribus-utils
# 193145 palm
# 195363 Österreichische Bundesverfassung: Datenset A
# 196428 Österreichische Bundesverfassung: Datenset B
# 196429 Österreichische Bundesverfassung: Datenset C
```

### List all documents from a given collection 

```python
col_id = 142911
documents = client.list_docs(col_id)
n = -3
for x in documents[n:]:
    print(x["docId"], x["title"], x["author"], x["nrOfPages"])

# 950920 Kasten_blau_44_9_0050 Pfalz-Neuburg, Eleonore Magdalena Theresia von 1
# 950921 Kasten_blau_44_9_0037 Pfalz, Johann Wilhelm Joseph Janaz von der 4
# 950922 Kasten_blau_44_9_0239 Pfalz, Johann Wilhelm Joseph Janaz von der 1


```
### Download METS files from Collection

```python
from transkribus_utils.transkribus_utils import ACDHTranskribusUtils

COL_ID = 51052
client = ACDHTranskribusUtils()
client.collection_to_mets(COL_ID)
# downloads a METS for each document in the given collection into a folder `./{COL_ID}

client.collection_to_mets(COL_ID, file_path='./foo')
# downloads a METS for each document in the given collection into a folder `./foo/{COL_ID}

client.collection_to_mets(COL_ID, filter_by_doc_ids=[230161, 230155])
# downloads only METS for document with ID 230161 and 230155 into a folder `./{COL_ID}
```