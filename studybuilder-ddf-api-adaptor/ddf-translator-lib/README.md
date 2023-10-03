# DDF-translator-lib

## Project description
The DDF-translator-lib is a Java library
for translating clinical study definitions
obtained from [OpenStudyBuilder (OSB)](https://novo-nordisk.gitlab.io/nn-public/openstudybuilder/project-description/) Clinical MDR solution APIs
to a data format which is compliant with the [Digital Data Flow (DDF)](https://www.transceleratebiopharmainc.com/initiatives/digital-data-flow/) Unified Study Definition Model (USDM) standard data model.
The USDM Java model classes are provided by the DDF-conformance library.

## Installation
Use [Gradle](https://gradle.org/) to compile the JAR file from sources and make it available to your Java project.
#### Note
Before compiling the JAR, place the DDF-conformance library JAR under the ```lib``` folder and match the file name according to the ```gradle.build``` file.

## Usage
The main flow for using the DDF-translator-lib library works as follows:
* Get a valid API token for accessing the OSB Clinical MDR API layer
* Create a ```OpenStudyObjectFactory``` instance by providing the API token to its constructor
* Get a ```OpenStudy``` OSB study definition instance using the ```getStudy``` method
* Create a ```StudyObjectMapper``` instance by providing the object factory and the OSB study definition
* Get a USDM-compliant study definition using the ```map``` method
