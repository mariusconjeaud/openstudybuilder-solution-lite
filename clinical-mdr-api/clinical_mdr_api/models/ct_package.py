from datetime import date, datetime
from typing import Optional, Sequence

from pydantic import Field

from clinical_mdr_api.domain.controlled_terminology.ct_package import CTPackageAR
from clinical_mdr_api.domain_repositories.models._utils import convert_to_datetime
from clinical_mdr_api.models.utils import BaseModel, snake_case_data


class CTPackage(BaseModel):
    @classmethod
    def from_ct_package_ar(cls, ct_package_ar: CTPackageAR) -> "CTPackage":
        return cls(
            uid=ct_package_ar.uid,
            catalogue_name=ct_package_ar.catalogue_name,
            name=ct_package_ar.name,
            label=ct_package_ar.label,
            description=ct_package_ar.description,
            href=ct_package_ar.href,
            registration_status=ct_package_ar.registration_status,
            source=ct_package_ar.source,
            import_date=ct_package_ar.import_date,
            effective_date=ct_package_ar.effective_date,
            user_initials=ct_package_ar.user_initials,
        )

    uid: str = Field(
        ...,
        title="uid",
        description="",
    )

    catalogue_name: str = Field(
        ...,
        title="catalogue_name",
        description="",
    )
    name: str = Field(
        ...,
        title="name",
        description="",
    )
    label: Optional[str] = Field(
        None,
        title="label",
        description="",
    )
    description: Optional[str] = Field(
        None,
        title="description",
        description="",
    )
    href: Optional[str] = Field(
        None,
        title="href",
        description="",
    )
    registration_status: Optional[str] = Field(
        None,
        title="registration_status",
        description="",
    )
    source: Optional[str] = Field(
        None,
        title="source",
        description="",
    )
    import_date: datetime = Field(
        ...,
        title="import_date",
        description="",
    )
    effective_date: date = Field(
        ...,
        title="effective_date",
        description="",
    )
    user_initials: str = Field(
        ...,
        title="user_initials",
        description="",
    )


class CodelistChangeItem(BaseModel):
    uid: str
    value_node: dict
    change_date: datetime
    is_change_of_codelist: bool

    @classmethod
    def from_repository_output(cls, query_output) -> "CodelistChangeItem":
        return cls(
            uid=query_output["uid"],
            value_node=snake_case_data(query_output["value_node"]),
            change_date=convert_to_datetime(value=query_output["change_date"]),
            is_change_of_codelist=query_output.get("is_change_of_codelist", True),
        )


class TermChangeItem(BaseModel):
    uid: str
    value_node: dict
    change_date: datetime
    codelists: Sequence

    @classmethod
    def from_repository_output(cls, query_output) -> "TermChangeItem":
        return cls(
            uid=query_output["uid"],
            value_node=snake_case_data(query_output["value_node"]),
            change_date=convert_to_datetime(value=query_output["change_date"]),
            codelists=query_output["codelists"],
        )


class CTPackageChanges(BaseModel):
    from_package: str
    to_package: str
    new_codelists: Sequence[CodelistChangeItem]
    deleted_codelists: Sequence[CodelistChangeItem]
    updated_codelists: Sequence[CodelistChangeItem]

    new_terms: Sequence[TermChangeItem]
    deleted_terms: Sequence[TermChangeItem]
    updated_terms: Sequence[TermChangeItem]

    @classmethod
    def from_repository_output(
        cls, old_package_name: str, new_package_name: str, query_output
    ) -> "CTPackageChanges":
        return cls(
            from_package=old_package_name,
            to_package=new_package_name,
            new_codelists=[
                CodelistChangeItem.from_repository_output(item)
                for item in query_output["new_codelists"]
            ],
            updated_codelists=[
                CodelistChangeItem.from_repository_output(item)
                for item in query_output["updated_codelists"]
            ],
            deleted_codelists=[
                CodelistChangeItem.from_repository_output(item)
                for item in query_output["deleted_codelists"]
            ],
            new_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["new_terms"]
            ],
            updated_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["updated_terms"]
            ],
            deleted_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["deleted_terms"]
            ],
        )


class CTPackageChangesSpecificCodelist(CTPackageChanges):
    not_modified_terms: Sequence[TermChangeItem]

    @classmethod
    def from_repository_output(
        cls, old_package_name: str, new_package_name: str, query_output
    ) -> "CTPackageChangesSpecificCodelist":
        return cls(
            from_package=old_package_name,
            to_package=new_package_name,
            new_codelists=[
                CodelistChangeItem.from_repository_output(item)
                for item in query_output["new_codelists"]
            ],
            updated_codelists=[
                CodelistChangeItem.from_repository_output(item)
                for item in query_output["updated_codelists"]
            ],
            deleted_codelists=[
                CodelistChangeItem.from_repository_output(item)
                for item in query_output["deleted_codelists"]
            ],
            new_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["new_terms"]
            ],
            updated_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["updated_terms"]
            ],
            deleted_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["deleted_terms"]
            ],
            not_modified_terms=[
                TermChangeItem.from_repository_output(item)
                for item in query_output["not_modified_terms"]
            ],
        )


class CTPackageDates(BaseModel):
    @classmethod
    def from_repository_output(
        cls, catalogue_name: str, effective_dates: Sequence[date]
    ) -> "CTPackageDates":

        return cls(catalogue_name=catalogue_name, effective_dates=effective_dates)

    catalogue_name: str = Field(
        ...,
        title="catalogue_name",
        description="",
    )
    effective_dates: Sequence[date] = Field(
        ..., title="effective_dates", description=""
    )
