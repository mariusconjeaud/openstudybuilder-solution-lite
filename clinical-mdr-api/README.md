# clinical-mdr-api

Clinical MDR repository to store the API linked with the neo4j database


## Technology stack
* Python with [FastAPI](https://fastapi.tiangolo.com/)
* [Neo4j](https://neo4j.com/)

---

## Setup Development Environment

### Setup python virtual environment

* Make sure Python 3.7 or newer is installed on your machine.
* Install pipenv version 2020.8.13 or later.
Note: the pipenv config file Pipefile specifies Python 3.7. It is also possible to use a newer version. To do that, update the Python version in Pipfile (python_version under [requires]) to the version you have before proceeding.
* Run `pipenv install --dev`

### Setup environment variables

Create `.env` file (in the root of the repository) with the following content:
```shell
NEO4J_DSN=bolt://neo4j:test1234@localhost:7687
OAUTH_ENABLED=false
ALLOW_ORIGIN_REGEX='.*'
```

Note that the value of `NEO4J_DSN` variable needs to be in alignment with the actual environemt variables used when starting the target neo4j database, e.g.

```
NEO4J_MDR_BOLT_PORT=7687
NEO4J_MDR_HOST=localhost
NEO4J_MDR_AUTH_USER=neo4j
NEO4J_MDR_AUTH_PASSWORD=test1234
```

To enable Authentication, add and set the following variables too.
Update them according to your auth configuration (the values below are random-generated examples).
```shell
OAUTH_ENABLED=True
OIDC_METADATA_DOCUMENT='https://login.microsoftonline.com/bd70d9d2-5ba8-4bb8-8ca5-55fdaf0c76d1/v2.0/.well-known/openid-configuration'
OAUTH_AUTHORIZATION_URL='https://login.microsoftonline.com/bd70d9d2-5ba8-4bb8-8ca5-55fdaf0c76d1/oauth2/v2.0/authorize'
OAUTH_TOKEN_URL='https://login.microsoftonline.com/bd70d9d2-5ba8-4bb8-8ca5-55fdaf0c76d1/oauth2/v2.0/token'
OAUTH_APP_ID='0b4bb293-433f-44d3-b992-8c95ad1665b9'
OAUTH_APP_ID_URI='api://0b4bb293-433f-44d3-b992-8c95ad1665b9'
OAUTH_CLIENT_ID='db8a95f6-a638-4535-bb1d-4a131748165a'
```

For integration with Azure Monitoring / Application Insights (logs, tracing, correlation)
add these variables as well (replacing the key):
```shell
APPLICATIONINSIGHTS_CONNECTION_STRING='InstrumentationKey=00000000-0000-0000-0000-000000000000'
UVICORN_LOG_CONFIG='logging-azure.yaml'
```

### Launch API locally

Start the API locally by running:

```bash
$ pipenv run dev
```


### Verify the API is running
If the setup is correctly done, the API should be available at:

- http://localhost:8000/

and the API specification in the form of SwaggerUI at:

- http://localhost:8000/docs/

### Additional information

You might want to use a start script like this:

```sh
#!/usr/bin/env bash
pipenv sync
pipenv run dev
```

All in all, you should be able to start the API by performing these steps:
* Start docker service by running `sudo service start docker`
* Start database container by running `docker start neo4j_local`
* Install Python virtual environment by running `pipenv install`
* Start the API by running `pipenv run dev`

---

## Usefull shortcuts (i.e. scripts defined in Pipfile)
- `pipenv run format` - Formats all Python code using [Black](https://black.readthedocs.io/en/stable/) and [isort](https://pycqa.github.io/isort/)
- `pipenv run testunit` - Runs all tests defined in the `clinical_mdr_api/tests/unit` folder and generates test and coverage reports
- `pipenv run testint` - Runs all tests defined in the `clinical_mdr_api/tests/integration` folder and generates test and coverage reports
- `pipenv run testauth` - Runs all tests defined in the `clinical_mdr_api/tests/oauth` folder and generates test and coverage reports
- `pipenv run test-telemetry` - Runs all tests defined in the `clinical_mdr_api/tests/telemetry` folder and generates test and coverage reports
- `pipenv run test` - Runs all tests defined in the `clinical_mdr_api/tests` folder
- `pipenv run lint` - Performs static code analysis using [Pylint](https://pylint.pycqa.org/en/latest/)
- `pipenv run openapi` - Generates API specification in the [OpenAPI](https://swagger.io/specification/) format and stores it in `openapi.json` file
- `pipenv run schemathesis` - Checks API implementation against the specification defined in `openapi.json` file, by using [schemathesis](https://schemathesis.readthedocs.io/en/stable/) tool

### Running tests
- Running unit/integration tests requires a neo4j database. We recommend using the docker image provided by the `neo4j-mdr-db` repository to start the database locally.

- If you want to execute only a subset of tests instead of using shortcuts defined above, you can run:
  ```bash
  $ pipenv run pytest {test file path}::{test class}::{test method}
  ```
  Below is an example:
  ```bash
  $ pipenv run pytest clinical_mdr_api/tests/integration/services/test_listing_study_design.py::TestStudyListing::test_registry_identifiers_listing
  ```

### Running Schemathesis checks
- In order to run schemathesis checks on a subset of endpoints and/or http methods, 
you can specify parameters for the desired http methods (`-M`) and endpoint names (`-E`) inside the `Pipfile`.

  For example, this will only test `GET` and `POST` endpoints whose name starts with `/concepts/numeric-values-with-unit`:

  ```
  schemathesis = """sh -c "
      st run \
          --checks=all \
          --base-url=http://localhost:8000 \
          -M GET \
          -M POST \
          -E ^/concepts/numeric-values-with-unit \
          --hypothesis-max-examples=10 \
          --junit-xml=schemathesis_report.xml \
          --report=schemathesis_report.tgz \
          --show-errors-tracebacks \
          openapi.json
  "
  """
  ```

---

## Authentication setup

See [OAuth README file](OAUTH-README.md)

---


## REST API Guidelines

### HTTP Methods

#### Requests

This is the default usage of the HTTP Methods:

| Method | Usage  | Success Response Code |
| :----- | :----- | :----- | 
| **GET** | **Get existing** - Returns a single entity or a list of entities. This is read only. |  200 - OK |
| **POST** | **Create new** - Creates a new entity or multiple new entities. This is non-idempotent. Responses can be cached. |  201 - Created |
| **PUT** | **Overwrite entirely** - Overwrites an existing or multiple existing entities entirely. Does not create a new entity (use POST in this case). This is idempotent. Responses cannot be cached. |  200 - OK |
| **PATCH** | **Update partially** - Updates some part of an existing entity or multiple existing entities. |  200 - OK |
| **DELETE** | **Delete existing** - Deletes an existing or multiple existing entities. |  204 - No Content |

E.g.:

| Resource       | GET - read    | POST - create  | PUT - overwrite | PATCH - Update partially | DELETE - delete |
| :------------- | :------------ | :------------- | :----------- | :-------------- |:-------------- |
| /studies | Returns a list of study objects.  | Creates a new study. | Bulk update of studies where each study will be completely overwritten. | Bulk update of studies where each study will only modified with the provided parameters. | Deletes all studies.|
| /studies/xyz | Returns the specific study identified by 'xyz'.  | Method not allowed (405). | Overwrites the entire study identified by 'xyz'. | Updates only the specified parts of the study identified by 'xyz' | Deletes the study identified by 'xyz'.|

### Error Codes
When making API requests, errors may occur. 
Errors in the API are formatted in a standardized JSON dictionary with the following keys:

| Key       | Mandatory | Content                                                                                                          |
| :-----    | :-----    | :-----                                                                                                           | 
| "message" | Yes       | A message describing the error that occurred. Ideally this should contain a suggestion for how to fix the error. |
| "detail"  | No        | An optional value with detailed information about the error.                                                     |
| "time"    | Yes       | Timestamp of when the error occurred.                                                                            |
| "path"    | Yes       | The complete request URL specified by the user.                                                                  |
| "method"  | Yes       | HTTP method - one of GET, POST, PATCH, DELETE.                                                                   |

For simplicity's sake, we limit the API to use only three error codes.

#### 400 - Bad Request
The request payload is invalid. 
This also covers errors that were previously classified as 422.

Example error message:

```
{
  "message": "Invalid query payload",
  "detail": [
    {
      "loc": [
	"query",
	"sortBy"
      ],
      "msg": "Invalid JSON",
      "type": "value_error.json"
    }
  ]
  "time": "2021-11-24T08:45:08.057908",
  "path": "http://localhost:8000/activity-description-templates/123?return_instantiation_counts=false",
  "method": "POST"
}
```
The template was not found. Make sure that there is a latest 'Final' version.

#### 403 - Forbidden
Some of the preconditions required to perform the operation were not met.
Likely one of the objects specified in the payload doesn't exist, or the object is not in the right state.

Example error message:

```
{
  "message": "The objective template identified by uid 'ObjectiveTemplate_000001' does not exist.",
  "time": "2021-11-24T08:46:16.728287",
  "path": "http://localhost:8000/objectives/",
  "method": "POST"
}
```

#### 404 - Not Found
The resource identified by the path cannot be found.
Either the path is invalid, or the resource you are trying to access hasn't been created. 

Example error message:

```
{
  "message": "ActivityDescriptionTemplateAR with uid 123 does not exist or there's no version with requested status or version number.",
  "time": "2021-11-24T08:45:08.057908",
  "path": "http://localhost:8000/activity-description-templates/123?return_instantiation_counts=false",
  "method": "GET"
}
```

#### 500 - Internal Server Error
Something unexpected went wrong inside the API. This is likely an error that needs investigating by the development team.

Example error message:

```
{
  "message": "Internal Server Error. Unable to connect to database.",
  "time": "2021-11-24T08:46:16.728287",
  "path": "http://localhost:8000/objectives/",
  "method": "POST"
}
```

### Naming Conventions
The follow general principles apply to naming the API endpoints: 
- We avoid deep nesting of the endpoints if possible.
- We minimize the number of root endpoints.
- Every endpoint must contain a description string describing its functionality.
- Endpoint parameters should be explicitly typed in the API code.
- We avoid PUT requests if possible.
- We have a unified method of pagination for query results. 


#### Endpoint Paths
Endpoints names should be specified in *kebab-case* (lowercase). 
This means we use **hyphens** to separate multiple words. 

E.g.
- /**event-registrations**
- /**disease-areas**

Endpoints can be either specified with or without a trailing ‘/’.

Verbs in endpoint names refer to actions, and are written in present simple. (imperative form)

Nouns in endpoint names refer to resources, always written in plural form.

E.g.
- /stud**ies**
- /event-registration**s**

#### Query Parameters
Parameter names and variables should be specified in **snake_case**. 
In general, we stick to the convention that query parameters are single words.

E.g.
- [GET] /studies?**page_number**=0&**page_size**=100

Parameter abbreviations, like “ID” or “UID” are written in snake_case format, e.g.: “study_uid”.
Each parameter field must also have a short, one sentence description.

#### Query Body
Query body parameters should be specified in  **snake_case**. 

### Future Unified Endpoint Names
In a future iteration of the project, endpoints will be naming uniformly by category. These categories are (for now), documented [here](https://docs.google.com/document/d/1DdFhcBRa-YtKy-SUjlEuvXU3m1zeVdrs1OlqmFs0Zwk/edit?usp=sharing).

---

## Code Style

Please stick to the rules mentioned here: https://pep8.org

---

## Source Code Management

We are using the 'Git-flow-Workflow' approach described here:
https://www.atlassian.com/de/git/tutorials/comparing-workflows/gitflow-workflow

---

## Domain Driven Design approach guide

(see [Domain Driven Design developer's guide](./doc/ddd_developers_guide/ddd-developers-guide.md) for clinical_mdr_api)

---

## Packaging the application for distribution
In order to ready the application for distribution, a series of steps is needed. The Pipfile.lock must be converted into requirements.txt, then a platform-specific python wheel must be built of the clinical-mdr-api application must be built (generating a .whl file of the app).
Finally, all the packages included in requirements.txt must be downloaded as .whl files.

```bash
pipenv lock -r > requirements.txt
pipenv run dist
pipenv run package
```
After these three commands have been run, the directory ./dist will contain all the .whl files necessary to install the application and these can be distributed for deployment.

To install the wheel files in a clean virtual environment and run the app, copy the wheel files to a clean directory and then execute the following commands (make sure to have `NEO4J_DSN` as an environment variable):
```bash
pipenv --python 3.7
pipenv shell
python -m pip install *.whl
python -m uvicorn --host=0.0.0.0 --port=8000 clinical_mdr_api.main:app
```
