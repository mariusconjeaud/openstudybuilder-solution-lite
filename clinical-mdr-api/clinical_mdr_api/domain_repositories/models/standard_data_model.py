from neomodel import (
    ArrayProperty,
    BooleanProperty,
    IntegerProperty,
    One,
    OneOrMore,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredRel,
    ZeroOrOne,
)

from clinical_mdr_api.domain_repositories.models.biomedical_concepts import (
    ActivityInstanceClassRoot,
    ActivityItemClassRoot,
)
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTCodelistRoot,
)
from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrNode,
    ClinicalMdrRel,
    Library,
    VersionRelationship,
    VersionRoot,
    VersionValue,
)


class DataModelCatalogue(ClinicalMdrNode):
    has_library = RelationshipFrom(Library, "CONTAINS_CATALOGUE", model=ClinicalMdrRel)
    name = StringProperty()
    data_model_type = StringProperty()


class DataModelIGValue(VersionValue):
    name = StringProperty()
    description = StringProperty()
    version_number = StringProperty()
    implements = RelationshipTo(
        "DataModelValue", "IMPLEMENTS", model=ClinicalMdrRel, cardinality=One
    )


class MasterModelValue(VersionValue):
    name = StringProperty()
    extends_version = RelationshipTo(
        DataModelIGValue, "EXTENDS_VERSION", model=ClinicalMdrRel, cardinality=One
    )
    has_master_model_version = RelationshipFrom(
        "DataModelIGRoot", "HAS_VERSION", model=VersionRelationship
    )


class DataModelIGRoot(VersionRoot):
    has_library = RelationshipFrom(
        Library, "CONTAINS_DATA_MODEL_IG", model=ClinicalMdrRel
    )
    has_version = RelationshipTo(
        DataModelIGValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(DataModelIGValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(
        DataModelIGValue, "LATEST_DRAFT", model=ClinicalMdrRel
    )
    latest_final = RelationshipTo(
        DataModelIGValue, "LATEST_FINAL", model=ClinicalMdrRel
    )
    latest_retired = RelationshipTo(
        DataModelIGValue, "LATEST_RETIRED", model=ClinicalMdrRel
    )

    has_master_model_version = RelationshipTo(
        MasterModelValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_master_model_value = RelationshipTo(
        MasterModelValue, "LATEST", model=ClinicalMdrRel
    )
    latest_master_model_draft = RelationshipTo(
        MasterModelValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_master_model_final = RelationshipTo(
        MasterModelValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_master_model_retired = RelationshipTo(
        MasterModelValue, "LATEST_RETIRED", model=VersionRelationship
    )


class DataModelValue(VersionValue):
    name = StringProperty()
    description = StringProperty()
    implements = RelationshipFrom(
        DataModelIGValue, "IMPLEMENTS", model=ClinicalMdrRel, cardinality=OneOrMore
    )


class DataModelRoot(VersionRoot):
    has_library = RelationshipFrom(Library, "CONTAINS_DATA_MODEL", model=ClinicalMdrRel)
    has_version = RelationshipTo(
        DataModelValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(DataModelValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(DataModelValue, "LATEST_DRAFT", model=ClinicalMdrRel)
    latest_final = RelationshipTo(DataModelValue, "LATEST_FINAL", model=ClinicalMdrRel)
    latest_retired = RelationshipTo(
        DataModelValue, "LATEST_RETIRED", model=ClinicalMdrRel
    )
    has_data_model = RelationshipFrom(
        DataModelCatalogue, "HAS_DATA_MODEL", model=ClinicalMdrRel
    )


# pylint: disable=abstract-method
class CatalogueVerRel(ClinicalMdrRel):
    version_number = StringProperty()
    catalogue = StringProperty()


class HasDatasetClassRel(ClinicalMdrRel):
    ordinal = StringProperty()


class DatasetClassInstance(VersionValue):
    description = StringProperty()
    label = StringProperty()
    title = StringProperty()
    has_dataset_class = RelationshipFrom(
        DataModelValue, "HAS_DATASET_CLASS", model=HasDatasetClassRel, cardinality=One
    )
    has_parent_class = RelationshipTo(
        "DatasetClassInstance",
        "HAS_PARENT_CLASS",
        model=CatalogueVerRel,
        cardinality=ZeroOrOne,
    )


class DatasetClass(VersionRoot):
    has_instance = RelationshipTo(
        DatasetClassInstance, "HAS_INSTANCE", model=ClinicalMdrRel
    )
    has_dataset_class = RelationshipFrom(
        DataModelCatalogue, "HAS_DATASET_CLASS", model=ClinicalMdrRel, cardinality=One
    )


class DatasetInstance(VersionValue):
    description = StringProperty()
    label = StringProperty()
    title = StringProperty()
    has_dataset = RelationshipFrom(
        DataModelIGValue, "HAS_DATASET", model=ClinicalMdrRel, cardinality=One
    )
    implements_dataset_class = RelationshipTo(
        DatasetClassInstance,
        "IMPLEMENTS_DATASET_CLASS",
        model=ClinicalMdrRel,
        cardinality=One,
    )


class HasKeyRel(StructuredRel):
    order = IntegerProperty()


class MasterModelDatasetValue(VersionValue):
    description = StringProperty()
    is_basic_std = BooleanProperty()
    xml_path = StringProperty()
    xml_title = StringProperty()
    structure = StringProperty()
    purpose = StringProperty()
    comment = StringProperty()
    ig_comment = StringProperty()
    map_domain_flag = BooleanProperty()
    suppl_qual_flag = BooleanProperty()
    include_in_raw = BooleanProperty()
    gen_raw_seqno_flag = BooleanProperty()
    enrich_build_order = IntegerProperty()

    has_dataset = RelationshipFrom(
        MasterModelValue, "HAS_DATASET", model=ClinicalMdrRel, cardinality=One
    )
    has_key = RelationshipTo(
        "DatasetVariable",
        "HAS_KEY",
        model=HasKeyRel,
        cardinality=OneOrMore,
    )
    has_sort_key = RelationshipTo(
        "DatasetVariable",
        "HAS_SORT_KEY",
        model=HasKeyRel,
        cardinality=OneOrMore,
    )
    has_activity_instance_class = RelationshipFrom(
        ActivityInstanceClassRoot,
        "IN_DATASET",
        model=ClinicalMdrRel,
    )

    has_master_model_version = RelationshipFrom(
        "Dataset", "HAS_VERSION", model=VersionRelationship
    )


class Dataset(VersionRoot):
    has_instance = RelationshipTo(DatasetInstance, "HAS_INSTANCE", model=ClinicalMdrRel)
    has_dataset = RelationshipFrom(
        DataModelCatalogue, "HAS_DATASET", model=ClinicalMdrRel, cardinality=One
    )

    has_master_model_version = RelationshipTo(
        MasterModelDatasetValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_master_model_value = RelationshipTo(
        MasterModelDatasetValue, "LATEST", model=ClinicalMdrRel
    )
    latest_master_model_draft = RelationshipTo(
        MasterModelDatasetValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_master_model_final = RelationshipTo(
        MasterModelDatasetValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_master_model_retired = RelationshipTo(
        MasterModelDatasetValue, "LATEST_RETIRED", model=VersionRelationship
    )


# pylint: disable=abstract-method
class HasClassVariableRel(ClinicalMdrRel):
    ordinal = StringProperty()
    version_number = StringProperty()


# pylint: disable=abstract-method
class HasMappingTargetRel(ClinicalMdrRel):
    version_number = StringProperty()


class VariableClassInstance(VersionValue):
    description = StringProperty()
    implementation_notes = StringProperty()
    title = StringProperty()
    label = StringProperty()
    core = StringProperty()
    completion_instructions = StringProperty()
    mapping_instructions = StringProperty()
    prompt = StringProperty()
    question_text = StringProperty()
    simple_datatype = StringProperty()
    role = StringProperty()
    has_class_variable = RelationshipFrom(
        DatasetClassInstance,
        "HAS_VARIABLE_CLASS",
        model=HasClassVariableRel,
        cardinality=One,
    )
    implements_variable = RelationshipFrom(
        "DatasetVariableInstance",
        "IMPLEMENTS_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )
    has_version = RelationshipFrom(
        "VariableClass", "HAS_VERSION", model=VersionRelationship
    )
    references_codelist = RelationshipTo(
        CTCodelistRoot, "REFERENCES_CODELIST", model=ClinicalMdrRel
    )
    has_mapping_target = RelationshipTo(
        "VariableClassInstance",
        "HAS_MAPPING_TARGET",
        model=HasMappingTargetRel,
        cardinality=ZeroOrOne,
    )


class VariableClass(VersionRoot):
    has_instance = RelationshipTo(
        VariableClassInstance, "HAS_INSTANCE", model=ClinicalMdrRel
    )
    has_class_variable = RelationshipFrom(
        DataModelCatalogue,
        "HAS_VARIABLE_CLASS",
        model=HasClassVariableRel,
        cardinality=One,
    )


# pylint: disable=abstract-method
class HasDatasetVariableRel(HasClassVariableRel):
    pass


class DatasetVariableInstance(VersionValue):
    description = StringProperty()
    title = StringProperty()
    label = StringProperty()
    simple_datatype = StringProperty()
    role = StringProperty()
    core = StringProperty()
    question_text = StringProperty()
    prompt = StringProperty()
    completion_instructions = StringProperty()
    implementation_notes = StringProperty()
    mapping_instructions = StringProperty()
    has_dataset_variable = RelationshipFrom(
        DatasetInstance,
        "HAS_DATASET_VARIABLE",
        model=HasDatasetVariableRel,
        cardinality=One,
    )
    implements_variable = RelationshipTo(
        VariableClassInstance,
        "IMPLEMENTS_VARIABLE",
        model=CatalogueVerRel,
        cardinality=One,
    )
    has_mapping_target = RelationshipTo(
        "DatasetVariableInstance",
        "HAS_MAPPING_TARGET",
        model=HasMappingTargetRel,
        cardinality=ZeroOrOne,
    )
    has_version = RelationshipFrom(
        "DatasetVariable", "HAS_VERSION", model=VersionRelationship
    )
    references_codelist = RelationshipTo(
        CTCodelistRoot, "REFERENCES_CODELIST", model=ClinicalMdrRel
    )


class MasterModelVariableValue(VersionValue):
    description = StringProperty()
    is_basic_std = BooleanProperty()
    # TODO : Move order into relationship from MMDataset to MMVariable ?
    order = IntegerProperty()
    variable_type = StringProperty()
    length = IntegerProperty()
    display_format = StringProperty()
    xml_datatype = StringProperty()
    xml_codelist = StringProperty()
    xml_codelist_multi = StringProperty()
    core = StringProperty()
    role = StringProperty()
    term = StringProperty()
    algorithm = StringProperty()
    qualifiers = ArrayProperty()
    comment = StringProperty()
    ig_comment = StringProperty()
    map_var_flag = BooleanProperty()
    fixed_mapping = StringProperty()
    include_in_raw = StringProperty()
    nn_internal = StringProperty()
    value_lvl_where_cols = StringProperty()
    value_lvl_label_col = StringProperty()
    value_lvl_collect_ct_val = StringProperty()
    value_lvl_ct_codelist_id_col = StringProperty()
    enrich_build_order = IntegerProperty()
    enrich_rule = StringProperty()
    xml_codelist_values = ArrayProperty()

    has_variable = RelationshipFrom(
        MasterModelDatasetValue,
        "HAS_DATASET_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )
    has_activity_item_class = RelationshipFrom(
        ActivityItemClassRoot,
        "AS_VARIABLE",
        model=ClinicalMdrRel,
    )


class DatasetVariable(VersionRoot):
    has_instance = RelationshipTo(
        DatasetVariableInstance, "HAS_INSTANCE", model=ClinicalMdrRel
    )
    has_dataset_variable = RelationshipFrom(
        DataModelCatalogue,
        "HAS_DATASET_VARIABLE",
        model=HasDatasetVariableRel,
        cardinality=One,
    )

    has_master_model_version = RelationshipTo(
        MasterModelVariableValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_master_model_value = RelationshipTo(
        MasterModelVariableValue, "LATEST", model=ClinicalMdrRel
    )
    latest_master_model_draft = RelationshipTo(
        MasterModelVariableValue, "LATEST_DRAFT", model=VersionRelationship
    )
    latest_master_model_final = RelationshipTo(
        MasterModelVariableValue, "LATEST_FINAL", model=VersionRelationship
    )
    latest_master_model_retired = RelationshipTo(
        MasterModelVariableValue, "LATEST_RETIRED", model=VersionRelationship
    )
