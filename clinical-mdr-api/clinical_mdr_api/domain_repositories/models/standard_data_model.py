from neomodel import One, OneOrMore, RelationshipFrom, RelationshipTo, StringProperty

from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrNode,
    ClinicalMdrRel,
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)


class DataModelCatalogue(ClinicalMdrNode):
    has_library = RelationshipFrom(Library, "CONTAINS_CATALOGUE")
    name = StringProperty()
    data_model_type = StringProperty()


class DataModelIGValue(VersionValue):
    name = StringProperty()
    description = StringProperty()
    implements = RelationshipTo(
        "DataModelValue", "IMPLEMENTS", model=ClinicalMdrRel, cardinality=One
    )


class DataModelIGRoot(VersionRoot):
    has_library = RelationshipFrom(Library, "CONTAINS_DATA_MODEL_IG")
    has_version = RelationshipTo(
        DataModelIGValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(DataModelIGValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(
        DataModelIGValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        DataModelIGValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        DataModelIGValue, "LATEST_RETIRED", model=VersionRelationship
    )


class DataModelValue(VersionValue):
    name = StringProperty()
    description = StringProperty()
    implements = RelationshipFrom(
        DataModelIGValue, "IMPLEMENTS", model=ClinicalMdrRel, cardinality=OneOrMore
    )


class DataModelRoot(VersionRoot):
    has_library = RelationshipFrom(Library, "CONTAINS_DATA_MODEL")
    has_version = RelationshipTo(
        DataModelValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(DataModelValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(
        DataModelValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        DataModelValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        DataModelValue, "LATEST_RETIRED", model=VersionRelationship
    )
    has_data_model = RelationshipFrom(
        DataModelCatalogue, "HAS_DATA_MODEL", model=ClinicalMdrRel
    )


class DatasetClassValue(VersionValue):
    description = StringProperty()
    label = StringProperty()
    title = StringProperty()
    has_dataset_class = RelationshipFrom(
        DataModelValue, "HAS_DATASET_CLASS", model=ClinicalMdrRel, cardinality=One
    )


class DatasetClassRoot(VersionRoot):
    has_latest_value = RelationshipTo(DatasetClassValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(
        DatasetClassValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        DatasetClassValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        DatasetClassValue, "LATEST_RETIRED", model=VersionRelationship
    )
    has_dataset_class = RelationshipFrom(
        DataModelCatalogue, "HAS_DATASET_CLASS", model=ClinicalMdrRel, cardinality=One
    )


class DatasetValue(VersionValue):
    description = StringProperty()
    label = StringProperty()
    title = StringProperty()
    has_dataset = RelationshipFrom(
        DataModelIGValue, "HAS_DATASET", model=ClinicalMdrRel, cardinality=One
    )
    implements_dataset_class = RelationshipTo(
        DatasetClassValue,
        "IMPLEMENTS_DATASET_CLASS",
        model=ClinicalMdrRel,
        cardinality=One,
    )


class DatasetRoot(VersionRoot):
    has_latest_value = RelationshipTo(DatasetValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(
        DatasetValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        DatasetValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        DatasetValue, "LATEST_RETIRED", model=VersionRelationship
    )
    has_dataset = RelationshipFrom(
        DataModelCatalogue, "HAS_DATASET", model=ClinicalMdrRel, cardinality=One
    )


class ClassVariableValue(VersionValue):
    description = StringProperty()
    implementation_notes = StringProperty()
    title = StringProperty()
    label = StringProperty()
    mapping_instructions = StringProperty()
    prompt = StringProperty()
    question_text = StringProperty()
    simple_datatype = StringProperty()
    role = StringProperty()
    has_class_variable = RelationshipFrom(
        DatasetClassValue, "HAS_CLASS_VARIABLE", model=ClinicalMdrRel, cardinality=One
    )
    implements_class_variable = RelationshipFrom(
        "DatasetVariableValue",
        "IMPLEMENTS_CLASS_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )


class ClassVariableRoot(VersionRoot):
    has_latest_value = RelationshipTo(
        ClassVariableValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(
        ClassVariableValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        ClassVariableValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        ClassVariableValue, "LATEST_RETIRED", model=VersionRelationship
    )
    has_class_variable = RelationshipFrom(
        DataModelCatalogue, "HAS_CLASS_VARIABLE", model=ClinicalMdrRel, cardinality=One
    )


class DatasetVariableValue(VersionValue):
    description = StringProperty()
    title = StringProperty()
    label = StringProperty()
    simple_datatype = StringProperty()
    role = StringProperty()
    core = StringProperty()
    has_dataset_variable = RelationshipFrom(
        DatasetValue, "HAS_DATASET_VARIABLE", model=ClinicalMdrRel, cardinality=One
    )
    implements_class_variable = RelationshipTo(
        ClassVariableValue,
        "IMPLEMENTS_CLASS_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )


class DatasetVariableRoot(VersionRoot):
    has_latest_value = RelationshipTo(
        DatasetVariableValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(
        DatasetVariableValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_final = RelationshipTo(
        DatasetVariableValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_retired = RelationshipTo(
        DatasetVariableValue, "LATEST_RETIRED", model=VersionRelationship
    )
    has_dataset_variable = RelationshipFrom(
        DataModelCatalogue,
        "HAS_DATASET_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )
