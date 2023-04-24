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
    has_library = RelationshipFrom(Library, "CONTAINS_DATA_MODEL_IG")
    has_version = RelationshipTo(
        DataModelIGValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(DataModelIGValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(DataModelIGValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(DataModelIGValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(DataModelIGValue, "LATEST_RETIRED")

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
    has_library = RelationshipFrom(Library, "CONTAINS_DATA_MODEL")
    has_version = RelationshipTo(
        DataModelValue, "HAS_VERSION", model=VersionRelationship
    )
    has_latest_value = RelationshipTo(DataModelValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(DataModelValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(DataModelValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(DataModelValue, "LATEST_RETIRED")
    has_data_model = RelationshipFrom(
        DataModelCatalogue, "HAS_DATA_MODEL", model=ClinicalMdrRel
    )


# pylint: disable=abstract-method
class CatalogueVerRel(ClinicalMdrRel):
    version_number = StringProperty()
    catalogue = StringProperty()


class DatasetClassValue(VersionValue):
    description = StringProperty()
    label = StringProperty()
    title = StringProperty()
    version_of = RelationshipFrom(
        "DatasetClassRoot", "HAS_VERSION", model=VersionRelationship
    )
    has_dataset_class = RelationshipFrom(
        DataModelValue, "HAS_DATASET_CLASS", model=ClinicalMdrRel, cardinality=One
    )
    has_parent_class = RelationshipFrom(
        "DatasetClassValue",
        "HAS_PARENT_CLASS",
        model=CatalogueVerRel,
        cardinality=ZeroOrOne,
    )


class DatasetClassRoot(VersionRoot):
    has_latest_value = RelationshipTo(DatasetClassValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(DatasetClassValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(DatasetClassValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(DatasetClassValue, "LATEST_RETIRED")
    has_dataset_class = RelationshipFrom(
        DataModelCatalogue, "HAS_DATASET_CLASS", model=ClinicalMdrRel, cardinality=One
    )
    has_version = RelationshipTo(
        DatasetClassValue, "HAS_VERSION", model=VersionRelationship
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
        "DatasetVariableRoot",
        "HAS_KEY",
        model=HasKeyRel,
        cardinality=OneOrMore,
    )
    has_sort_key = RelationshipTo(
        "DatasetVariableRoot",
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
        "DatasetRoot", "HAS_VERSION", model=VersionRelationship
    )


class DatasetRoot(VersionRoot):
    has_latest_value = RelationshipTo(DatasetValue, "LATEST", model=ClinicalMdrRel)
    latest_draft = RelationshipTo(DatasetValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(DatasetValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(DatasetValue, "LATEST_RETIRED")
    has_dataset = RelationshipFrom(
        DataModelCatalogue, "HAS_DATASET", model=ClinicalMdrRel, cardinality=One
    )
    has_version = RelationshipTo(DatasetValue, "HAS_VERSION", model=VersionRelationship)

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
    ordinal = IntegerProperty()
    version_number = StringProperty()


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
        DatasetClassValue,
        "HAS_CLASS_VARIABLE",
        model=HasClassVariableRel,
        cardinality=One,
    )
    implements_variable = RelationshipFrom(
        "DatasetVariableValue",
        "IMPLEMENTS_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )


class ClassVariableRoot(VersionRoot):
    has_latest_value = RelationshipTo(
        ClassVariableValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(ClassVariableValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(ClassVariableValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(ClassVariableValue, "LATEST_RETIRED")
    has_class_variable = RelationshipFrom(
        DataModelCatalogue,
        "HAS_CLASS_VARIABLE",
        model=HasClassVariableRel,
        cardinality=One,
    )
    has_version = RelationshipTo(
        ClassVariableValue, "HAS_VERSION", model=VersionRelationship
    )

    has_master_model_version = RelationshipTo(
        "MasterModelVariableValue", "HAS_VERSION", model=VersionRelationship
    )
    has_latest_master_model_value = RelationshipTo(
        "MasterModelVariableValue", "LATEST", model=ClinicalMdrRel
    )
    latest_master_model_draft = RelationshipTo(
        "MasterModelVariableValue", "LATEST_DRAFT", model=VersionRelationship
    )
    latest_master_model_final = RelationshipTo(
        "MasterModelVariableValue", "LATEST_FINAL", model=VersionRelationship
    )
    latest_master_model_retired = RelationshipTo(
        "MasterModelVariableValue", "LATEST_RETIRED", model=VersionRelationship
    )


# pylint: disable=abstract-method
class HasDatasetVariableRel(HasClassVariableRel):
    pass


# pylint: disable=abstract-method
class HasMappingTargetRel(ClinicalMdrRel):
    version_number = StringProperty()


class DatasetVariableValue(VersionValue):
    description = StringProperty()
    title = StringProperty()
    label = StringProperty()
    simple_datatype = StringProperty()
    role = StringProperty()
    core = StringProperty()
    has_dataset_variable = RelationshipFrom(
        DatasetValue,
        "HAS_DATASET_VARIABLE",
        model=HasDatasetVariableRel,
        cardinality=One,
    )
    implements_variable = RelationshipTo(
        ClassVariableValue,
        "IMPLEMENTS_VARIABLE",
        model=CatalogueVerRel,
        cardinality=One,
    )
    has_mapping_target = RelationshipTo(
        "DatasetVariableValue",
        "HAS_MAPPING_TARGET",
        model=HasMappingTargetRel,
        cardinality=ZeroOrOne,
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
        DatasetClassValue,
        "HAS_MASTER_MODEL_VARIABLE",
        model=ClinicalMdrRel,
        cardinality=One,
    )

    # has_variable = RelationshipFrom(
    #     MasterModelDatasetValue,
    #     "HAS_DATASET_VARIABLE",
    #     model=ClinicalMdrRel,
    #     cardinality=One,
    # )

    has_activity_item_class = RelationshipFrom(
        ActivityItemClassRoot,
        "AS_VARIABLE",
        model=ClinicalMdrRel,
    )


class DatasetVariableRoot(VersionRoot):
    has_latest_value = RelationshipTo(
        DatasetVariableValue, "LATEST", model=ClinicalMdrRel
    )
    latest_draft = RelationshipTo(DatasetVariableValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(DatasetVariableValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(DatasetVariableValue, "LATEST_RETIRED")
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
    has_version = RelationshipTo(
        DatasetVariableValue, "HAS_VERSION", model=VersionRelationship
    )
