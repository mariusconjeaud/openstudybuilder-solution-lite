from datetime import datetime, timezone
from types import MappingProxyType
from typing import List, Sequence

from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDateTime

try:
    # New in Python version 3.8.
    from functools import cached_property
except ImportError:
    # Remove if upgraded to Python 3.8 also remove dependency from Pipfile
    from cached_property import cached_property

import ctrxml

from clinical_mdr_api.domain._utils import get_iso_lang_data
from clinical_mdr_api.exceptions import BusinessLogicException
from clinical_mdr_api.models import (
    CTCodelistAttributes,
    OdmForm,
    OdmItem,
    OdmItemGroup,
    Project,
    StudyVisit,
)
from clinical_mdr_api.models.study import (
    HighLevelStudyDesignJsonModel,
    StudyDescriptionJsonModel,
    StudyIdentificationMetadataJsonModel,
    StudyInterventionJsonModel,
    StudyMetadataJsonModel,
    StudyPopulationJsonModel,
    StudyVersionMetadataJsonModel,
)
from clinical_mdr_api.oauth import get_current_user_id
from clinical_mdr_api.services.ct_codelist_attributes import CTCodelistAttributesService
from clinical_mdr_api.services.odm_forms import OdmFormService
from clinical_mdr_api.services.odm_item_groups import OdmItemGroupService
from clinical_mdr_api.services.odm_items import OdmItemService
from clinical_mdr_api.services.project import ProjectService
from clinical_mdr_api.services.study import StudyService
from clinical_mdr_api.services.study_visit import StudyVisitService


def iso639_shortest(code: str) -> str:
    """Convert a language code to the shortest ISO 639 code, suitable value for xml:lang attribute"""
    return get_iso_lang_data(q=code, return_key="639-1")


class CTRXMLService:
    """Assemble and visualize Study Protocol Flowchart data"""

    serializer = XmlSerializer(config=SerializerConfig(pretty_print=True))

    namespaces = MappingProxyType(
        {
            None: "http://www.cdisc.org/ns/odm/v1.3",
            "ctr": "http://www.cdisc.org/ns/ctr/v1.0",
            "ct": "http://eudract.emea.europa.eu/schema/clinical_trial",
            "sdm": "http://www.cdisc.org/ns/studydesign/v1.0",
        }
    )

    def get_ctr_odm(self, study_uid: str):
        odm_builder = ODMBuilder(study_uid)
        odm = odm_builder.get_odm()
        # noinspection PyTypeChecker
        return self.serializer.render(odm, ns_map=self.namespaces)


class ODMBuilder:
    study_uid: str

    def __init__(self, study_uid: str):
        self.study_uid = study_uid

    @cached_property
    def project(self) -> Project:
        project = ProjectService(user=get_current_user_id()).get_by_study_uid(
            self.study_uid
        )
        if not project:
            raise BusinessLogicException("Missing study project")
        return project

    @cached_property
    def study_metadata(self) -> StudyMetadataJsonModel:
        fields = (
            f"+current_metadata.{m}"
            for m in (
                "identification_metadata",
                "version_metadata",
                "high_level_study_design",
                "study_description",
                "study_population",
                "study_intervention",
            )
        )
        study = StudyService(user=get_current_user_id()).get_by_uid(
            uid=self.study_uid, fields=",".join(fields)
        )
        if study.current_metadata is None:
            raise BusinessLogicException("Missing study metadata")
        return study.current_metadata

    @cached_property
    def study_visits(self) -> Sequence[StudyVisit]:
        result = StudyVisitService(author=get_current_user_id()).get_all_visits(
            self.study_uid
        )
        return result.items

    @property
    def study_identification_metadata(self) -> StudyIdentificationMetadataJsonModel:
        if self.study_metadata.identification_metadata is None:
            raise BusinessLogicException("Missing study identification metadata")
        return self.study_metadata.identification_metadata

    @property
    def study_version_metadata(self) -> StudyVersionMetadataJsonModel:
        if self.study_metadata.version_metadata is None:
            raise BusinessLogicException("Missing study version metadata")
        return self.study_metadata.version_metadata

    @property
    def study_design_high(self) -> HighLevelStudyDesignJsonModel:
        if self.study_metadata.high_level_study_design is None:
            raise BusinessLogicException("Missing study design (high level)")
        return self.study_metadata.high_level_study_design

    @property
    def study_description(self) -> StudyDescriptionJsonModel:
        if self.study_metadata.study_description is None:
            raise BusinessLogicException("Missing study description")
        return self.study_metadata.study_description

    @property
    def study_population(self) -> StudyPopulationJsonModel:
        if self.study_metadata.study_population is None:
            raise BusinessLogicException("Missing study population")
        return self.study_metadata.study_population

    @property
    def study_intervention(self) -> StudyInterventionJsonModel:
        if self.study_metadata.study_intervention is None:
            raise BusinessLogicException("Missing study intervention")
        return self.study_metadata.study_intervention

    def get_odm(self) -> ctrxml.Odm:
        return ctrxml.Odm(
            odmversion=ctrxml.Odmversion.VALUE_1_3_2,
            file_type=ctrxml.FileType.SNAPSHOT,
            # TODO: See the ODM specification for a discussion of FileOID recommendations.
            # file_oid=self.study_identification_metadata.studyId,
            granularity=ctrxml.Granularity.METADATA,
            # TODO: any information that will help the receiver interpret the document correctly
            # description=self.study_identification_metadata.studyId,
            creation_date_time=XmlDateTime.from_datetime(datetime.now(timezone.utc)),
            as_of_date_time=XmlDateTime.from_datetime(
                self.study_version_metadata.version_timestamp
            ),
            # originator="FIXME",  # TODO: Submission sponsor name "Company XYZ"
            source_system="OpenStudyBuilder",
            # source_system_version="FIXME",  # TODO
            study=[self.get_odm_study()],
        )

    def get_odm_study(self) -> ctrxml.Study:
        return ctrxml.Study(
            oid=self.study_identification_metadata.study_id,  # TODO: See the ODM specification section 2.11 for OID considera
            global_variables=self.get_odm_global_variables(),
            meta_data_version=[self.get_odm_meta_data_version()],
        )

    def get_odm_global_variables(self) -> ctrxml.GlobalVariables:
        odm_global = ctrxml.GlobalVariables()

        if self.study_description:

            if self.study_description.study_short_title:
                translated_title = [
                    ctrxml.TranslatedText(
                        value=self.study_description.study_short_title
                    )
                ]
                odm_global.study_name = ctrxml.StudyName(
                    study_name_localizations=[
                        ctrxml.StudyNameLocalizations(translated_text=translated_title)
                    ]
                )
                odm_global.public_title = [
                    ctrxml.PublicTitle(translated_text=translated_title)
                ]

            if self.study_description.study_title:
                odm_global.study_description = self.study_description.study_title
                odm_global.study_detailed_description = [
                    ctrxml.StudyDetailedDescription(
                        translated_text=[
                            ctrxml.TranslatedText(
                                value=self.study_description.study_title
                            )
                        ]
                    )
                ]

        return odm_global

    def get_odm_meta_data_version(self) -> ctrxml.MetaDataVersion:
        return ctrxml.MetaDataVersion(
            oid=(
                self.study_version_metadata.locked_version_number
                or self.study_version_metadata.version_timestamp.isoformat()
            ),
            name=self.study_version_metadata.study_status,
            description=self.study_version_metadata.locked_version_info,
            study_event_def=self.get_odm_study_event_defs(),
            form_def=self.get_odm_form_defs(),
            item_group_def=self.get_odm_item_group_defs(),
            item_def=self.get_odm_item_defs(),
            code_list=self.get_odm_codelists(),
        )

    def get_odm_study_event_defs(self) -> List[ctrxml.StudyEventDef]:
        return [
            ctrxml.StudyEventDef(
                oid=visit.uid,
                name=f"{visit.visit_type_name} {visit.visit_name}",
                repeating=ctrxml.YesOrNo.NO,
                type=ctrxml.EventType.SCHEDULED,
                category=visit.study_epoch_name,
            )
            for visit in self.study_visits
        ]

    @cached_property
    def odm_forms(self) -> Sequence[OdmForm]:
        # TODO: add filtering by StudyUID when it gets implemented in database schema
        result = OdmFormService(user=get_current_user_id()).get_all_concepts()
        # noinspection PyTypeChecker
        return result.items

    def get_odm_form_defs(self) -> List[ctrxml.FormDef]:
        return [
            ctrxml.FormDef(
                oid=form.oid,
                name=form.name,
                repeating=form.repeating.upper() if form.repeating else None,
                description=ctrxml.Description(
                    translated_text=[
                        ctrxml.TranslatedText(
                            value=description.description,
                            lang=iso639_shortest(description.language),
                        )
                        for description in form.descriptions
                    ]
                ),
                item_group_ref=[
                    ctrxml.ItemGroupRef(
                        item_group_oid=item_group.oid,
                        order_number=item_group.order_number,
                        mandatory=item_group.mandatory and item_group.mandatory.upper(),
                        collection_exception_condition_oid=item_group.collection_exception_condition_oid,
                    )
                    for item_group in form.item_groups
                ],
                alias=[
                    ctrxml.Alias(
                        name=alias.name,
                        context=alias.context,
                    )
                    for alias in form.aliases
                ],
            )
            for form in self.odm_forms
        ]

    @cached_property
    def odm_item_groups(self) -> Sequence[OdmItemGroup]:
        uids = [
            item_group.uid for form in self.odm_forms for item_group in form.item_groups
        ]
        result = OdmItemGroupService(user=get_current_user_id()).get_all_concepts(
            filter_by={"uid": {"v": uids, "op": "eq"}}
        )
        # noinspection PyTypeChecker
        return result.items

    def get_odm_item_group_defs(self) -> List[ctrxml.ItemGroupDef]:
        return [
            ctrxml.ItemGroupDef(
                oid=item_group.oid,
                name=item_group.name,
                repeating=(item_group.repeating and item_group.repeating.upper()),
                is_reference_data=(
                    item_group.is_reference_data
                    and item_group.is_reference_data.upper()
                ),
                domain=item_group.origin,  # FIXME! confirm whether 'domain' is 'origin' in SB model
                purpose=item_group.purpose,
                comment=item_group.comment,
                description=ctrxml.Description(
                    translated_text=[
                        ctrxml.TranslatedText(
                            value=description.description,
                            lang=iso639_shortest(description.language),
                        )
                        for description in item_group.descriptions
                    ]
                ),
                item_ref=[
                    ctrxml.ItemRef(
                        item_oid=item.oid,
                        order_number=item.order_number,
                        mandatory=(item.mandatory and item.mandatory.upper()),
                        role=item.role,
                        role_code_list_oid=item.role_codelist_oid,
                    )
                    for item in item_group.items
                ],
                alias=[
                    ctrxml.Alias(name=alias.name, context=alias.context)
                    for alias in item_group.aliases
                ],
            )
            for item_group in self.odm_item_groups
        ]

    @cached_property
    def odm_items(self) -> Sequence[OdmItem]:
        uids = [
            item.uid for item_group in self.odm_item_groups for item in item_group.items
        ]
        result = OdmItemService(user=get_current_user_id()).get_all_concepts(
            filter_by={"uid": {"v": uids, "op": "eq"}}
        )
        # noinspection PyTypeChecker
        return result.items

    def get_odm_item_defs(self) -> List[ctrxml.ItemDef]:
        return [
            ctrxml.ItemDef(
                oid=item.oid,
                name=item.name,
                data_type=item.datatype,
                length=item.length,
                significant_digits=item.significant_digits,
                origin=item.origin,
                comment=item.comment,
                code_list_ref=(
                    item.codelist
                    and ctrxml.CodeListRef(code_list_oid=item.codelist.uid)
                ),
                alias=[
                    ctrxml.Alias(name=alias.name, context=alias.context)
                    for alias in item.aliases
                ],
            )
            for item in self.odm_items
        ]

    @cached_property
    def ct_codelist_attributes(self) -> Sequence[CTCodelistAttributes]:
        uids = [item.codelist.uid for item in self.odm_items if item.codelist]
        result = CTCodelistAttributesService(
            user=get_current_user_id()
        ).get_all_ct_codelists(
            catalogue_name=None,
            library=None,
            package=None,
            filter_by={
                "codelist_uid": {
                    "v": uids,
                    "op": "eq",
                }
            },
        )
        # noinspection PyTypeChecker
        return result.items

    def get_odm_codelists(self) -> List[ctrxml.CodeList]:
        return [
            ctrxml.CodeList(
                oid=codelist.codelist_uid,
                name=codelist.name,
                # data_type=,  # TODO DataType is required attribute but not available in CTCodelistAttributes model
            )
            for codelist in self.ct_codelist_attributes
        ]
