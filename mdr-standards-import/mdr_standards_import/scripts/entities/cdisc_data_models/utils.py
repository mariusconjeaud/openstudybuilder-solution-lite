from typing import Sequence, Optional

from os import path

from mdr_standards_import.scripts.entities.cdisc_data_models.data_model_type import (
    DataModelType,
)
from mdr_standards_import.scripts.entities.cdisc_data_models.data_model_variable import (
    DataModelVariable,
)

from mdr_standards_import.scripts.utils import (
    flatten_list_of_lists_recursive,
    extract_list_from_json_recursive,
)


def extract_variables_from_json_data(
    json_data,
    catalogue,
    data_model_import,
    data_model_type,
    is_class_dataset: bool = False,
) -> "list[DataModelVariable]":

    variables_output = []
    variables_key = _get_variables_json_key(catalogue, is_class_dataset)
    # The extract list method is recursive and can handle list property inside a list of objects
    # The list then needs to be flattened
    variables = flatten_list_of_lists_recursive(
        [l for l in extract_list_from_json_recursive(json_data, [variables_key])]
    )
    for variable in variables:
        _variable: DataModelVariable = data_model_import.merge_variable(
            href=variable.get("_links", {}).get("self", {}).get("href", None),
        )
        codelists = [
            path.basename(codelist.get("href", None))
            for codelist in variable.get("_links", {}).get("codelist", [])
        ]

        implemented_variables = []
        mapping_targets = []
        if data_model_type == DataModelType.IMPLEMENTATION.value:
            implemented_variables_keys = _get_implemented_variables_json_key(
                catalogue,
            )
            implemented_variables = flatten_list_of_lists_recursive(
                [
                    l
                    for l in extract_list_from_json_recursive(
                        variable.get("_links", {}), implemented_variables_keys
                    )
                ]
            )

            if catalogue == "CDASHIG":
                mapping_targets = flatten_list_of_lists_recursive(
                    [
                        l
                        for l in extract_list_from_json_recursive(
                            variable.get("_links", {}),
                            ["sdtmigDatasetMappingTargets"],
                        )
                    ]
                )

        _variable.set_attributes(
            name=variable.get("name", None),
            title=variable.get("_links", {}).get("self", {}).get("title", None),
            label=variable.get("label", None),
            description=variable.get("description", None),
            definition=variable.get("definition", None),
            ordinal=variable.get("ordinal", None),
            role=variable.get("role", None),
            role_description=variable.get("roleDescription", None),
            simple_datatype=variable.get("simpleDatatype", None),
            implementation_notes=variable.get("implementationNotes", None),
            mapping_instructions=variable.get("mappingInstructions", None),
            prompt=variable.get("prompt", None),
            question_text=variable.get("questionText", None),
            completion_instructions=variable.get("completionInstructions", None),
            core=variable.get("core", None),
            codelists=codelists,
            implements_variables=[v.get("href", None) for v in implemented_variables],
            mapping_targets=[v.get("href", None) for v in mapping_targets],
            prior_version=variable.get("_links", {})
            .get("priorVersion", {})
            .get("href", None),
        )
        variables_output.append(_variable)
    return variables_output


def _get_variables_json_key(
    catalogue: str,
    is_class_dataset: bool = False,
) -> Optional[str]:
    """
    Returns the json key where the list of variables is stored

    Args:
        catalogue (str): Name of the catalogue

    Returns:
        Optional(str): json key. Most are a single level, but some (like ADAM) can be nested.
    """
    if catalogue == "ADAM":
        return "analysisVariables"
    elif catalogue == "CDASH":
        return "cdashModelFields"
    elif catalogue == "CDASHIG":
        return "fields"
    elif catalogue == "SDTM":
        return "datasetVariables" if is_class_dataset else "classVariables"
    elif catalogue in ["SDTMIG", "SENDIG"]:
        return "datasetVariables"
    else:
        return None


def _get_implemented_variables_json_key(catalogue: str) -> Sequence[str]:
    """
    Returns the json key where the link to the implemented variable is stored.
    This is a list, because multiple options are sometimes available.

    Args:
        catalogue (str): Name of the catalogue

    Returns:
        list(str): json keys. Empty means that the provided catalogue doesn't have variables
        that implement variables from other catalogues.
        Multiple entries means it is either one of these options.
    """
    if catalogue in ["SDTMIG", "SENDIG"]:
        return ["modelClassVariable", "modelDatasetVariable"]
    elif catalogue == "CDASHIG":
        return ["implements"]
    else:
        return []
