# StudyBuilder DDF adapter Azure cloud functions

## Project description
This is an Azure cloud function written in Java that uses the StudyBuilder DDF translation library (DDF-translator-lib) for translating clinical study definitions
obtained from [OpenStudyBuilder (OSB)](https://novo-nordisk.gitlab.io/nn-public/openstudybuilder/project-description/) Clinical MDR solution APIs
to a data format which is compliant with the [Digital Data Flow (DDF)](https://www.transceleratebiopharmainc.com/initiatives/digital-data-flow/) Unified Study Definition Model (USDM) standard data model.

The cloud function is used to provide a single endpoint that responds with a DDF compliant study given a study id.

## Usage
Run the following command to build then run the function project:
```
gradle jar --info
gradle azureFunctionsRun
```

## Future works
This project will be extended with more functions to create a set of endpoints which are compatible with the [DDF API Reference](https://github.com/cdisc-org/DDF-RA).