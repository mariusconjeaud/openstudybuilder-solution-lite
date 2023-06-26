from .utils.importer import BaseImporter, open_file, open_file_async
from .utils.path_join import path_join
from .utils.metrics import Metrics
from .functions.parsers import map_boolean
import asyncio
import aiohttp
import csv
from typing import Optional, Sequence, Any

from .functions.utils import load_env
from .functions.caselessdict import CaselessDict

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
SAMPLE = load_env("MDR_MIGRATION_SAMPLE", default="False") == "True"
API_BASE_URL = load_env("API_BASE_URL")


# ---------------------------------------------------------------
# Utilities for parsing and converting data
# ---------------------------------------------------------------
#


def sample_from_dict(d, sample=10):
    if SAMPLE:
        keys = list(d)[0:sample]
        values = [d[k] for k in keys]
        return dict(zip(keys, values))
    else:
        return d


def sample_from_list(d, sample=10):
    if SAMPLE:
        return d[0:sample]
    else:
        return d


ACTIVITIES_PATH = "/concepts/activities/activities"
ACTIVITY_GROUPS_PATH = "/concepts/activities/activity-groups"
ACTIVITY_SUBGROUPS_PATH = "/concepts/activities/activity-sub-groups"
ACTIVITY_INSTANCE_CLASSES_PATH = "/activity-instance-classes"
ACTIVITY_ITEM_CLASSES_PATH = "/activity-item-classes"
ACTIVITY_ITEMS_PATH = "/activity-items"
ACTIVITY_INSTANCES_PATH = "/concepts/activities/activity-instances"


# Activities with instances, groups and subgroups in sponsor library
class Activities(BaseImporter):
    logging_name = "activities"

    def __init__(self, api=None, metrics_inst=None, cache=None):
        super().__init__(api=api, metrics_inst=metrics_inst, cache=cache)

    # Get all terms belonging to any of the category and subcategory codelists
    def _get_all_cats_and_subcats(self):
        self.ensure_cache()
        sdtm_cat_lists = ["QSCAT", "ACSPCAT", "DECAT", "FTCAT", "CCCAT", "ONCRSCAT", "FXRESCAT", "ICRESCAT", "PYRESCAT", "BACAT", "CAGTCAT", "SAERCAT", "CPCAT", "IECAT", "DSCAT", "MSRESCAT", "CLCAT", "STCAT", "EGCATSND", "MIRESCAT"]
        sdtm_subcat_lists = ["DSSCAT"]

        all_codelist_uids = self._get_codelists_uid_and_submval()
        sdtm_cat_uids = []
        sdtm_subcat_uids = []
        for submval in sdtm_cat_lists:
            cl_uid = all_codelist_uids.get(submval)
            if cl_uid is not None:
                sdtm_cat_uids.extend(term for term in self.cache.all_terms_attributes if term["codelist_uid"] == cl_uid)
        for submval in sdtm_subcat_lists:
            cl_uid = all_codelist_uids.get(submval)
            if cl_uid is not None:
                sdtm_subcat_uids.extend(term for term in self.cache.all_terms_attributes if term["codelist_uid"] == cl_uid)
        return sdtm_cat_uids, sdtm_subcat_uids

    # Get a dictionary with key = submission value and value = uid
    def _get_codelists_uid_and_submval(self):
        all_codelist_attributes = self.api.get_all_from_api("/ct/codelists/attributes")

        all_codelist_uids = CaselessDict(
            self.api.get_all_identifiers(
                all_codelist_attributes,
                identifier="submission_value",
                value="codelist_uid",
            )
        )
        return all_codelist_uids

    # Get all terms from a codelist identified by its submission value
    def _get_codelist_terms(self, codelist_submval):
        self.ensure_cache()
        all_codelist_uids = self._get_codelists_uid_and_submval()
        cl_uid = all_codelist_uids.get(codelist_submval)
        if cl_uid is not None:
            terms = [term for term in self.cache.all_terms_attributes if term["codelist_uid"] == cl_uid]
            return terms

    # Get a dictionary mapping submission values to term uids for a codelist identified by its uid
    def _get_submissionvalues_for_codelist(self, cl):
        terms = self._get_codelist_terms(cl)
        name_submvals = CaselessDict(
            self.api.get_all_identifiers(
                terms,
                identifier="name_submission_value",
                value="term_uid",
            )
        )
        code_submvals = CaselessDict(
            self.api.get_all_identifiers(
                terms,
                identifier="code_submission_value",
                value="term_uid",
            )
        )
        name_submvals.update(code_submvals)
        return name_submvals

    # Get a dictionary with valid ct terms that may map to values in a given column of the activity instances file
    def _get_terms_for_columns(self):
        ct_codelists = {
            "specimen": "SPECTYPE",
            "SDTM_DOMAIN": "DOMAIN",
            "unit_dimension": "UNITDIM",
            "laterality": "LAT",
            "location": "LOC",
        }
        result = {}
        for key, val in ct_codelists.items():
            result[key] = self._get_submissionvalues_for_codelist(val)
        return result

    # Sort a list of activity items by class, returns a dict with class as key
    def _sort_activity_items_by_class(self, items):
        result = {}
        for item in items:
            class_name = item["activity_item_class"]["name"]
            if class_name not in result:
                result[class_name] = {}
            result[class_name][item["name"]] = item
        return result


    @open_file_async()
    async def handle_activity_groups(self, csvfile, session):
        # Populate then activity groups in sponsor library
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        api_tasks = []

        existing_rows = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_GROUPS_PATH),
            identifier="name",
            value="uid",
        )

        for row in readCSV:
            data = {
                "path": ACTIVITY_GROUPS_PATH,
                "approve_path": ACTIVITY_GROUPS_PATH,
                "body": {
                    "name": row[headers.index("std_assm_grp")],
                    "name_sentence_case": row[headers.index("std_assm_grp")].lower(),
                    "definition": "Definition not provided",
                    "library_name": "Sponsor",
                },
            }
            if not existing_rows.get(data["body"]["name"]):
                self.log.info(
                    f"Add activity group '{data['body']['name']}' to library '{data['body']['library_name']}'"
                )
                api_tasks.append(
                    self.api.post_then_approve(data=data, session=session, approve=True)
                )  # TODO Verify if activity groups can be approved?
            else:
                # Already exists, skip.
                # Do we need patch functionality here?
                self.log.info(
                    f"Item '{data['body']['name']}' already exists in library '{data['body']['library_name']}'"
                )
        await asyncio.gather(*api_tasks)

    @open_file_async()
    async def handle_activity_subgroups(self, csvfile, session):
        # Populate then activity subgroups in sponsor library
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)

        existing_groups = sample_from_dict(
            self.api.get_all_identifiers(
                self.api.get_all_from_api(ACTIVITY_GROUPS_PATH),
                identifier="name",
                value="uid",
            ),
            sample=10,
        )

        existing_sub_groups = {}

        for item in self.api.get_all_from_api(ACTIVITY_SUBGROUPS_PATH):
            existing_sub_groups[item["name"]] = {
                "uid": item["uid"],
                "activity_group": item["activity_group"],
            }

        api_tasks = []
        file_data = {}

        for row in readCSV:
            sub_group_name = row[headers.index("std_assm_sub_grp")]
            group_name = row[headers.index("std_assm_grp")]
            if group_name != "" and sub_group_name != "":
                # print(group_name, " - ", sub_group_name)
                if sub_group_name in file_data:
                    self.log.warning(
                        f"Subgroup '{sub_group_name}' is already belonging to group '{file_data[sub_group_name]}', ignoring group '{group_name}'"
                    )
                file_data[sub_group_name] = group_name
        # print(file_data)

        for sub_group_name, group_name in file_data.items():
            # Check if all group names are defined
            if group_name not in existing_groups:
                self.log.warning(
                    f"Group name not found: '{group_name}' will not create subgroup: '{sub_group_name}'"
                )
                continue
            # Check if subgroup exists
            if sub_group_name in existing_sub_groups:
                # If the subgroup has the wrong group, patch it
                if (
                    existing_sub_groups[sub_group_name]["activity_group"]["name"]
                    == group_name
                ):
                    self.log.info(
                        f"Subgroup '{sub_group_name}' already exists for group '{group_name}'"
                    )
                    continue
                data = {
                    "path": ACTIVITY_SUBGROUPS_PATH,
                    "patch_path": path_join(
                        ACTIVITY_SUBGROUPS_PATH,
                        existing_sub_groups[sub_group_name]["uid"],
                    ),
                    "new_path": path_join(
                        ACTIVITY_SUBGROUPS_PATH,
                        existing_sub_groups[sub_group_name]["uid"],
                        "versions",
                    ),
                    "approve_path": ACTIVITY_SUBGROUPS_PATH,
                    "body": {
                        "name": sub_group_name,
                        "name_sentence_case": sub_group_name.lower(),
                        "library_name": "Sponsor",
                        "activity_group": existing_groups[group_name],
                        "change_description": "Migration modification",
                    },
                }
                self.log.info(
                    f"Patching subgroup '{sub_group_name}' to group '{group_name}'"
                )
                api_tasks.append(
                    self.api.new_version_patch_then_approve(
                        data=data, session=session, approve=True
                    )
                )
            else:
                # Create the new subgroup
                data = {
                    "path": ACTIVITY_SUBGROUPS_PATH,
                    "approve_path": ACTIVITY_SUBGROUPS_PATH,
                    "body": {
                        "name": sub_group_name,
                        "name_sentence_case": sub_group_name.lower(),
                        "library_name": "Sponsor",
                        "activity_group": existing_groups[group_name],
                    },
                }
                self.log.info(
                    f"Adding subgroup '{sub_group_name}' to groups '{group_name}'"
                )
                api_tasks.append(
                    self.api.post_then_approve(data=data, session=session, approve=True)
                )
        await asyncio.gather(*api_tasks)

    @open_file_async()
    async def handle_activities(self, csvfile, session):
        # Populate the activities in sponsor library
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        self.log.info("Fetching all existing activity subgroups")
        existing_sub_groups = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_SUBGROUPS_PATH),
            identifier="name",
            value="uid",
        )

        self.log.info("Fetching all existing activities")
        existing_activities = {}
        for item in self.api.get_all_activity_objects("activities"):
            existing_activities[item["name"]] = {
                "uid": item["uid"],
                "activity_subgroup": item["activity_subgroup"],
            }

        api_tasks = []
        file_data = {}

        for row in readCSV:
            activity_name = row[headers.index("activity")]
            sub_group_name = row[headers.index("std_assm_sub_grp")]
            if activity_name != "" and sub_group_name != "":
                if sub_group_name in file_data:
                    self.log.warning(
                        f"Activity '{activity_name}' is already belonging to subgroup '{file_data[sub_group_name]}', ignoring subgroup '{sub_group_name}'"
                    )
                file_data[activity_name] = sub_group_name

        file_data = sample_from_dict(file_data, sample=100)

        for activity_name, sub_group_name in file_data.items():
            # Check if all sub group names are defined
            if sub_group_name not in existing_sub_groups:
                self.log.warning(
                    f"Sub group name not found: {sub_group_name} will not create activity: {activity_name}"
                )
                continue
            # Check if activity exists
            if activity_name in existing_activities:
                # If the activity does not already have all groups -> patch it
                subgrp = existing_activities[activity_name]["activity_subgroup"]
                if subgrp is not None and subgrp["name"] == sub_group_name:
                    self.log.info(f"Activity '{activity_name}' already exists for subgroup '{sub_group_name}'")
                    continue
                data = {
                    "path": ACTIVITIES_PATH,
                    "patch_path": path_join(
                        ACTIVITIES_PATH,
                        existing_activities[activity_name]["uid"]
                    ),
                    "new_path": path_join(
                        ACTIVITIES_PATH,
                        existing_activities[activity_name]["uid"],
                        "versions",
                    ),
                    "approve_path": ACTIVITIES_PATH,
                    "body": {
                        "name": activity_name,
                        "name_sentence_case": activity_name.lower(),
                        "library_name": "Sponsor",
                        "activity_subgroup": existing_sub_groups[sub_group_name],
                        "change_description": "Migration modification",
                    },
                }
                self.log.info(
                    f"Adding activity '{activity_name}' to subgroup '{sub_group_name}'"
                )
                api_tasks.append(
                    self.api.new_version_patch_then_approve(
                        data=data, session=session, approve=True
                    )
                )
            else:  # Create the activity
                data = {
                    "path": ACTIVITIES_PATH,
                    "approve_path": ACTIVITIES_PATH,
                    "body": {
                        "name": activity_name,
                        "name_sentence_case": activity_name.lower(),
                        "library_name": "Sponsor",
                        "activity_subgroup": existing_sub_groups[sub_group_name],
                    },
                }
                self.log.info(
                    f"Adding activity '{activity_name}' to subgroup '{sub_group_name}'"
                )
                api_tasks.append(
                    self.api.post_then_approve(data=data, session=session, approve=True)
                )

        await asyncio.gather(*api_tasks)
        # await session.close()

    @open_file_async()
    async def handle_activity_instance_classes(self, csvfile, session):
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        api_tasks_for_0_level_ac = []
        api_tasks_for_1_level_ac = []
        api_tasks_for_2_level_ac = []
        api_tasks_for_3_level_ac = []
        api_tasks_for_4_level_ac = []

        migrated_ac_level_0 = []
        migrated_ac_level_1 = []
        migrated_ac_level_2 = []
        migrated_ac_level_3 = []
        migrated_ac_level_4 = []
        existing_rows = self.api.response_to_dict(
            self.api.get_all_from_api(ACTIVITY_INSTANCE_CLASSES_PATH),
            identifier="name",
        )

        def are_instance_classes_equal(new, existing):
            existing_parent_name = existing.get("parent_class").get("name") if existing.get("parent_class") else None
            new_parent_name = new.get("parent_name") if new.get("parent_name") != "" else None
            new_order = int(new.get("order")) if new.get("order") else None
            try:
                new_is_specific = map_boolean(new.get("is_domain_specific"), raise_exception=True)
            except ValueError:
                new_is_specific = None
            result = (existing_parent_name == new_parent_name
                    and existing.get("name") == new.get("name")
                    and existing.get("library_name") == new.get("library_name")
                    and existing.get("is_domain_specific") == new_is_specific
                    and existing.get("definition") == new.get("definition")
                    and existing.get("order") == new_order)
            return result

        async def _migrate_aic(data):
            # lookup the parent_uid
            parent_name = data["body"].get("parent_name")
            if parent_name:
                parent_uid = existing_rows.get(parent_name).get("uid")
                if not parent_uid:
                    self.log.info(
                        f"Item '{data['body']['name']}' didn't found a corresponding parent Activity Instance Class"
                    )
                    return
                data["body"]["parent_uid"] = parent_uid
            if existing_rows.get(data["body"]["name"]) is None:
                self.log.info(
                    f"Add activity instance class '{data['body']['name']}' to library '{data['body']['library_name']}'"
                )
                if "parent_name" in data["body"]:
                    data["body"].pop("parent_name")
                response = await self.api.post_then_approve(
                    data=data, session=session, approve=True
                )
                if response:
                    existing_rows[data["body"]["name"]] = response
            elif not are_instance_classes_equal(data["body"], existing_rows.get(data["body"]["name"])):
                self.log.info(
                    f"Patch activity instance class '{data['body']['name']}' in library '{data['body']['library_name']}'"
                )
                if "parent_name" in data["body"]:
                    data["body"].pop("parent_name")
                data["patch_path"] = path_join(
                    ACTIVITY_INSTANCE_CLASSES_PATH,
                    existing_rows[data["body"]["name"]].get("uid"),
                )
                data["new_path"] = path_join(
                    ACTIVITY_INSTANCE_CLASSES_PATH,
                    existing_rows[data["body"]["name"]].get("uid"),
                    "versions",
                )
                data["body"]["change_description"] = "Migration modification"
                response = await self.api.new_version_patch_then_approve(
                    data=data, session=session, approve=True
                )
                if response:
                    existing_rows[data["body"]["name"]] = response
            else:
                self.log.info(
                    f"Identical item '{data['body']['name']}' already exists in library '{data['body']['library_name']}'"
                )

        for row in readCSV:
            # migrating Level 0 ActivityInstanceClass
            ac_0_level_name = row[headers.index("LEVEL_0_CLASS")]
            ac_0_level_data = {
                "path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "approve_path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "body": {
                    "name": ac_0_level_name,
                    "library_name": "Sponsor",
                },
            }
            if ac_0_level_name not in migrated_ac_level_0:
                migrated_ac_level_0.append(ac_0_level_name)
                api_tasks_for_0_level_ac.append(_migrate_aic(ac_0_level_data))

            # migrating Level 1 ActivityInstanceClass
            ac_1_level_name = row[headers.index("LEVEL_1_CLASS")]
            ac_1_level_data = {
                "path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "approve_path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "body": {
                    "name": ac_1_level_name,
                    "parent_name": ac_0_level_name,
                    "library_name": "Sponsor",
                },
            }
            if ac_1_level_name not in migrated_ac_level_1:
                migrated_ac_level_1.append(ac_1_level_name)
                api_tasks_for_1_level_ac.append(_migrate_aic(ac_1_level_data))

            # migrating Level 2 ActivityInstanceClass
            ac_2_level_name = row[headers.index("LEVEL_2_CLASS")]
            ac_2_level_data = {
                "path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "approve_path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "body": {
                    "name": ac_2_level_name,
                    "parent_name": ac_1_level_name,
                    "library_name": "Sponsor",
                },
            }
            if ac_2_level_name not in migrated_ac_level_2:
                migrated_ac_level_2.append(ac_2_level_name)
                api_tasks_for_2_level_ac.append(_migrate_aic(ac_2_level_data))

            # migrating Level 3 ActivityInstanceClass
            ac_3_level_name = row[headers.index("LEVEL_3_CLASS")]
            ac_3_level_data = {
                "path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "approve_path": ACTIVITY_INSTANCE_CLASSES_PATH,
                "body": {
                    "name": row[headers.index("LEVEL_3_CLASS")],
                    "parent_name": ac_2_level_name,
                    "is_domain_specific": row[headers.index("DOMAIN_SPECIFIC")],
                    "definition": row[headers.index("DEFINITION")],
                    "order": row[headers.index("ORDER")],
                    "library_name": "Sponsor",
                },
            }
            if ac_3_level_name not in migrated_ac_level_3:
                migrated_ac_level_3.append(ac_3_level_name)
                api_tasks_for_3_level_ac.append(_migrate_aic(ac_3_level_data))

            # migrating Level 4 ActivityInstanceClass
            ac_4_level_name = row[headers.index("LEVEL_4_CLASS")]
            if row[headers.index("LEVEL_4_CLASS")]:
                ac_4_level_data = {
                    "path": ACTIVITY_INSTANCE_CLASSES_PATH,
                    "approve_path": ACTIVITY_INSTANCE_CLASSES_PATH,
                    "body": {
                        "name": row[headers.index("LEVEL_4_CLASS")],
                        "parent_name": ac_3_level_name,
                        "is_domain_specific": row[headers.index("DOMAIN_SPECIFIC")],
                        "definition": row[headers.index("DEFINITION")],
                        "order": row[headers.index("ORDER")],
                        "library_name": "Sponsor",
                    },
                }
                if ac_4_level_name not in migrated_ac_level_4:
                    migrated_ac_level_4.append(ac_4_level_name)
                    api_tasks_for_4_level_ac.append(_migrate_aic(ac_4_level_data))

        await asyncio.gather(*api_tasks_for_0_level_ac)
        await asyncio.gather(*api_tasks_for_1_level_ac)
        await asyncio.gather(*api_tasks_for_2_level_ac)
        await asyncio.gather(*api_tasks_for_3_level_ac)
        await asyncio.gather(*api_tasks_for_4_level_ac)

    @open_file_async()
    async def handle_activity_item_classes(self, csvfile, session):
        self.ensure_cache()
        # Populate then activity item classes in sponsor library
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        api_tasks = []

        existing_rows = self.api.response_to_dict(
            self.api.get_all_from_api(ACTIVITY_ITEM_CLASSES_PATH),
            identifier="name",
        )
        print(f"existing_rows {existing_rows}")
        available_instance_classes = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_INSTANCE_CLASSES_PATH),
            identifier="name",
            value="uid",
        )

        def are_item_classes_equal(new, existing):
            new_order = int(new.get("order")) if new.get("order") else None
            new_instance_class_names = set(new.get("activity_instance_class_names")) if new.get("activity_instance_class_names") else set()
            existing_instance_class_names = set(inst_cls["name"] for inst_cls in existing.get("activity_instance_classes"))
            result = (existing.get("name") == new.get("name")
                    and existing.get("library_name") == new.get("library_name")
                    and existing.get("mandatory") == new.get("mandatory")
                    and existing.get("order") == new_order
                    and existing.get("role").get("uid") == new.get("role_uid")
                    and existing.get("data_type").get("uid") == new.get("data_type_uid")
                    and existing_instance_class_names == new_instance_class_names)
            return result

        activity_item_data = {}
        for row in readCSV:
            activity_instance_class_name = row[headers.index("ACTIVITY_INSTANCE_CLASS")]
            instance_class_uid = available_instance_classes.get(
                activity_instance_class_name
            )
            role = row[headers.index("SEMANTIC_ROLE")]
            if role in self.cache.all_terms_name_submission_values:
                role_uid = self.cache.all_terms_name_submission_values[role]
            else:
                self.log.warning(
                    f"The role ({role}) wasn't found for the following ActivityInstanceClass ({activity_instance_class_name})"
                )
                continue
            data_type = row[headers.index("SEMANTIC_DATA_TYPE")]
            if data_type in self.cache.all_terms_name_submission_values:
                data_type_uid = self.cache.all_terms_name_submission_values[data_type]
            else:
                self.log.warning(
                    f"The data_type ({data_type}) wasn't found for the following ActivityInstanceClass ({activity_instance_class_name})"
                )
                continue
            activity_item_class_name = row[headers.index("ACTIVITY_ITEM_CLASS")]
            if instance_class_uid is None:
                self.log.warning(
                    f"Activity instance class '{activity_instance_class_name}' "
                    f"wasn't found in available activity instance classes in the db"
                )
                continue
            data = {
                "path": ACTIVITY_ITEM_CLASSES_PATH,
                "approve_path": ACTIVITY_ITEM_CLASSES_PATH,
                "body": {
                    "name": activity_item_class_name,
                    "order": row[headers.index("ORDER")],
                    "mandatory": map_boolean(row[headers.index("MANDATORY")]),
                    "activity_instance_class_uids": [instance_class_uid],
                    "activity_instance_class_names": [activity_instance_class_name],
                    "role_uid": role_uid,
                    "data_type_uid": data_type_uid,
                    "library_name": "Sponsor",
                },
            }
            if activity_item_class_name not in activity_item_data:
                activity_item_data[activity_item_class_name] = data
            else:
                current_instance_classes = activity_item_data[activity_item_class_name][
                    "body"
                ]["activity_instance_class_uids"]
                if instance_class_uid not in current_instance_classes:
                    current_instance_classes.append(instance_class_uid)
                    activity_item_data[activity_item_class_name]["body"]["activity_instance_class_names"].append(activity_instance_class_name)

            if activity_item_class_name in activity_item_data:
                self.log.info(
                    f"Trying to link {activity_item_class_name} "
                    f"to additional instance class {activity_instance_class_name}"
                )

        for item_name, item_data in activity_item_data.items():
            if item_name not in existing_rows:
                self.log.info(
                    f"Add activity item class '{item_data['body']['name']}' to library '{item_data['body']['library_name']}'"
                )
                if "activity_instance_class_names" in item_data["body"]:
                    item_data["body"].pop("activity_instance_class_names")
                api_tasks.append(
                    self.api.post_then_approve(
                        data=item_data, session=session, approve=True
                    )
                )
            elif not are_item_classes_equal(item_data["body"], existing_rows[item_name]):
                self.log.info(
                    f"Patch activity item class '{item_data['body']['name']}' to library '{item_data['body']['library_name']}'"
                )
                if "activity_instance_class_names" in item_data["body"]:
                    item_data["body"].pop("activity_instance_class_names")
                item_data["patch_path"] = path_join(
                    ACTIVITY_ITEM_CLASSES_PATH,
                    existing_rows[item_name].get("uid"),
                )
                item_data["new_path"] = path_join(
                    ACTIVITY_ITEM_CLASSES_PATH,
                    existing_rows[item_name].get("uid"),
                    "versions",
                )
                item_data["body"]["change_description"] = "Migration modification"
                api_tasks.append(
                    self.api.new_version_patch_then_approve(
                        data=item_data, session=session, approve=True
                    )
                )
            else:
                self.log.info(
                    f"Identical item '{item_data['body']['name']}' already exists in library '{item_data['body']['library_name']}'"
                )

        await asyncio.gather(*api_tasks)
        # await session.close()

    @open_file_async()
    async def handle_activity_instances(self, csvfile, session):
        readCSV = csv.DictReader(csvfile, delimiter=',')
        api_tasks = []

        all_activity_hierarchies = self.api.get_all_identifiers(
            self.api.get_all_activity_objects("activities"),
            identifier="name",
            value="uid",
        )

        all_activity_instance_classes = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_INSTANCE_CLASSES_PATH),
            identifier="name",
            value="uid",
        )

        # Names may overlap between different item classes.
        # Store the different classes in separate dicts.
        all_activity_items = self.api.get_all_from_api(ACTIVITY_ITEMS_PATH)
        items_by_class = {}
        for item in all_activity_items:
            itemclass = item["activity_item_class"]["name"]
            if itemclass not in items_by_class:
                items_by_class[itemclass] = {}
            name = item["name"]
            uid= item["uid"]
            items_by_class[itemclass][name] = uid

        existing_instances = self.api.get_all_activity_objects("activity-instances")
        existing_rows_by_name = self.api.response_to_dict(
            existing_instances,
            identifier="name",
        )
        existing_rows_by_tc = self.api.response_to_dict(
            existing_instances,
            identifier="topic_code",
        )

        def are_instances_equal(new, existing):
            new_item_uids = set(new.get("activity_item_uids")) if new.get("activity_item_uids") else set()
            existing_item_uids = set(item["uid"] for item in existing.get("activity_items"))
            new_activity_uids = set(new.get("activities")) if new.get("activities") else set()
            existing_activity_uids = set(act["uid"] for act in existing.get("activities"))
            result = (existing.get("activity_instance_class").get("uid") == new.get("activity_instance_class_uid")
                    and existing.get("library_name") == new.get("library_name")
                    and existing.get("name_sentence_case") == new.get("name_sentence_case")
                    and existing.get("adam_param_code") == existing.get("adam_param_code")
                    and existing.get("legacy_description") == existing.get("legacy_description")
                    and existing.get("topic_code") == existing.get("topic_code")
                    and existing_item_uids == new_item_uids
                    and existing_activity_uids == new_activity_uids)
            return result

        file_data = []
        for row in readCSV:
            file_data.append(row)

        file_data = sample_from_list(file_data, sample=10)
        all_data = {}
        for row in file_data:
            activity_instance_name = row["activity_instance"]
            activity = row["activity"]

            # find related Activity hierarchy
            activity_uids = []
            if all_activity_hierarchies.get(activity):
                activity_uids.append(all_activity_hierarchies.get(activity))

            # find related Activity Items
            activity_item_uids = []

            def add_item_uid(in_key):
                if row[in_key] != "":
                    value = row[in_key]
                    if "|" in value:
                        items = value.split("|")
                    else:
                        items = [value]
                    for item in items:
                        # look up item of correct item class
                        domain = row["GENERAL_DOMAIN_CLASS"]
                        itemclass = self._get_item_class(in_key, domain)
                        item_uid = items_by_class.get(itemclass, {}).get(item)
                        if item_uid is not None:
                            activity_item_uids.append(item_uid)
                        else:
                            self.log.info(f"Term for '{in_key}' = '{item}' not found")
            add_item_uid("specimen")
            add_item_uid("SDTM_DOMAIN")
            add_item_uid("sdtm_cat")
            add_item_uid("sdtm_sub_cat")
            add_item_uid("sdtm_variable")
            add_item_uid("laterality")
            add_item_uid("location")
            add_item_uid("unit_dimension")
            add_item_uid("std_unit")

            # find related Activity Instance Class
            sub_domain_class = row["sub_domain_class"]
            if sub_domain_class.lower() == "adverse event":
                activity_instance_class_uid = all_activity_instance_classes.get(
                    "AdverseEvent"
                )
            elif sub_domain_class.lower() == "medical history":
                activity_instance_class_uid = all_activity_instance_classes.get(
                    "MedicalHistory"
                )
            elif sub_domain_class.lower() == "disposition":
                activity_instance_class_uid = all_activity_instance_classes.get(
                    "Disposition"
                )
            elif sub_domain_class.lower() == "categoric finding":
                activity_instance_class_uid = all_activity_instance_classes.get(
                    "CategoricFinding"
                )
            elif sub_domain_class.lower() == "numeric finding":
                activity_instance_class_uid = all_activity_instance_classes.get(
                    "NumericFinding"
                )
            elif sub_domain_class.lower() == "textual finding":
                activity_instance_class_uid = all_activity_instance_classes.get(
                    "TextualFinding"
                )
            else:
                # The activity instance type was not recognized
                self.log.warning(
                    f"Activity instance '{activity_instance_name}' has an unknown domain class '{sub_domain_class}'"
                )
                continue
            data = {
                "path": ACTIVITY_INSTANCES_PATH,
                "approve_path": ACTIVITY_INSTANCES_PATH,
                "body": {
                    "activity_instance_class_uid": activity_instance_class_uid,
                    "name": activity_instance_name,
                    "name_sentence_case": activity_instance_name.lower(),
                    "adam_param_code": row["adam_param_code"],
                    "activities": activity_uids,
                    "activity_item_uids": activity_item_uids,
                    "legacy_description": row["legacy_description"],
                    "topic_code": row["TOPIC_CD"],
                    "library_name": "Sponsor",
                },
            }
            if activity_instance_name not in all_data:
                all_data[activity_instance_name] = data
            else:
                current_activity_items = all_data[activity_instance_name]["body"][
                    "activity_item_uids"
                ]
                for activity_item_uid in activity_item_uids:
                    if activity_item_uid not in current_activity_items:
                        current_activity_items.append(activity_item_uid)

        for activity_instance_name, activity_instance_data in all_data.items():
            topic_code = activity_instance_data['body']["topic_code"]
            if activity_instance_name not in existing_rows_by_name and topic_code not in existing_rows_by_tc:
                self.log.info(
                    f"Adding activity instance '{activity_instance_name}' to activities"
                    f" '{activity_instance_data['body']['activities']}'"
                )
                api_tasks.append(
                    self.api.post_then_approve(data=activity_instance_data, session=session, approve=True)
                )
            elif activity_instance_name in existing_rows_by_name and existing_rows_by_name[activity_instance_name]["topic_code"] != topic_code:
                self.log.warning(f"Not adding activity instance for topic code {topic_code}"
                             f" since instance with name {activity_instance_name} already exists"
                             f" with different topic code {existing_rows_by_name[activity_instance_name]['topic_code']}")
            elif not are_instances_equal(activity_instance_data["body"], existing_rows_by_tc[topic_code]):
                self.log.info(
                    f"Patch activity instance '{activity_instance_name}' to activities"
                    f" '{activity_instance_data['body']['activities']}'"
                )
                activity_instance_data["patch_path"] = path_join(
                    ACTIVITY_INSTANCES_PATH,
                    existing_rows_by_tc[topic_code].get("uid"),
                )
                activity_instance_data["new_path"] = path_join(
                    ACTIVITY_INSTANCES_PATH,
                    existing_rows_by_tc[topic_code].get("uid"),
                    "versions",
                )
                activity_instance_data["body"]["change_description"] = "Migration modification"
                api_tasks.append(
                    self.api.new_version_patch_then_approve(data=activity_instance_data, session=session, approve=True)
                )
            else:
                self.log.info(
                    f"Identical activity instance '{activity_instance_name}' already exists"
                )
        await asyncio.gather(*api_tasks)

    # Get the item class for combination of column name and domain
    def _get_item_class(self, col, domain):
        if col == "specimen":
            return "specimen"
        if col == "SDTM_DOMAIN":
            return "domain"
        if col == "location":
            return "location"
        if col == "laterality":
            return "laterality"
        if col == "unit_dimension":
            return "unit_dimension"
        if col == "sdtm_cat":
            if domain == "FINDINGS":
                return "finding_category"
            if domain == "EVENTS":
                return "event_category"
            if domain == "INTERVENTIONS":
                return "intervention_category"
        if col == "sdtm_sub_cat":
            if domain == "FINDINGS":
                return "finding_subcategory"
            if domain == "EVENTS":
                return "event_subcategory"
            if domain == "INTERVENTIONS":
                return "intervention_subcategory"
        if col == "sdtm_variable" and domain == "FINDINGS":
            return "test_name_code"
        if col == "std_unit":
            return "standard_unit"

    # Helper to create a single activity item
    def _create_activity_item(self, item, column, domain, terms_for_columns):
        item_class = self._get_item_class(column, domain)
        if not item_class:
            return
        if item_class not in self.all_migrated_items:
            self.all_migrated_items[item_class] = []
        migrated_items = self.all_migrated_items[item_class]
        if item != "" and item not in migrated_items:
            unit_uid = None
            item_uid = None
            if item_class in ["standard_unit"]:
                unit_uid = self.all_units.get(item)
                if unit_uid:
                    self.log.info(
                        f"Activity item '{item}' found unit def '{item}'"
                    )
                else:
                    self.log.warning(
                        f"Activity item '{item}' could not find unit def '{item}'"
                    )
            else:
                if item_class == "finding_category":
                    submval = item + " FIND_CAT"
                elif item_class == "finding_subcategory":
                    submval = item + " FIND_SUB_CAT"
                elif item_class == "intervention_category":
                    submval = item + " INTRV_CAT"
                elif item_class == "intervention_subcategory":
                    submval = item + " INTRV_SUB_CAT"
                elif item_class == "event_category":
                    submval = item + " EVNT_CAT"
                elif item_class == "event_subcategory":
                    submval = item + " EVNT_SUB_CAT"
                else:
                    submval = item
                if column == "sdtm_cat" and item in self.sdtm_cats:
                    item_uid = self.sdtm_cats[item]
                    self.log.info(
                        f"Activity item '{item}' found underlying ct term with uid '{item_uid}' for item class '{item_class}'"
                    )
                elif column == "sdtm_sub_cat" and item in self.sdtm_subcats:
                    item_uid = self.sdtm_subcats[item]
                    self.log.info(
                        f"Activity item '{item}' found underlying ct term with uid '{item_uid}' for item class '{item_class}'"
                    )
                elif column in terms_for_columns:
                    terms = terms_for_columns[column]
                    if submval in terms:
                        item_uid = terms[submval]
                        self.log.info(
                            f"Activity item '{item}' found underlying ct term with uid '{item_uid}' for item class '{item_class}'"
                        )
                    else:
                        self.log.warning(
                            f"Activity item '{item}' from column '{column}' can't find underlying ct term for item class '{item_class}'"
                        )
                        migrated_items.append(item)
                        return

                elif submval in self.cache.all_terms_name_submission_values:
                    item_uid = self.cache.all_terms_name_submission_values[submval]
                    self.log.info(
                        f"Activity item '{item}' found underlying ct term with uid '{item_uid}' for item class '{item_class}'"
                    )
                elif submval in self.cache.all_terms_code_submission_values:
                    item_uid = self.cache.all_terms_code_submission_values[submval]
                    self.log.info(
                        f"Activity item '{item}' found underlying ct term with uid '{item_uid}' for item class '{item_class}'"
                    )
                else:
                    self.log.warning(
                        f"Activity item '{item}' can't find underlying ct term for item class '{item_class}'"
                    )
                    migrated_items.append(item)
                    return
            if item not in migrated_items:
                item_data = {
                    "path": ACTIVITY_ITEMS_PATH,
                    "approve_path": ACTIVITY_ITEMS_PATH,
                    "body": {
                        "name": item,
                        "activity_item_class_uid": self.all_activity_item_classes.get(item_class),
                        "library_name": "Sponsor",
                        "activity_item_class_name": item_class,
                    },
                }
                if unit_uid and item_uid:
                    self.log.warning(f"Activity Item '{item}' can't link both to CTTerm and UnitDefinition, ignoring the unit")
                if item_uid:
                    item_data["body"]["ct_term_uid"] = item_uid
                elif unit_uid:
                    item_data["body"]["unit_definition_uid"] = unit_uid
                else:
                    self.log.warning(f"Activity Item '{item}' is not linked with any related nodes like"
                                     f"CTTerm or UnitDefinition")
                    return
                if item_data["body"]["activity_item_class_uid"] is None:
                    self.log.warning(f"Activity Item '{item}' has unknown item class '{item_class}'")
                    return
                migrated_items.append(item)
                return item_data





    @open_file_async()
    async def handle_activity_items(self, csvfile, session):
        self.ensure_cache()
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        api_tasks = []


        self.all_activity_item_classes = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_ITEM_CLASSES_PATH),
            identifier="name",
            value="uid",
        )

        existing_items = self.api.get_all_from_api(ACTIVITY_ITEMS_PATH)
        existing_rows = self.api.get_all_identifiers(
            existing_items,
            identifier="name",
            value="uid",
        )
        existing_items_by_class = self._sort_activity_items_by_class(existing_items)

        self.all_units = self.api.get_all_identifiers(
            self.api.get_all_from_api("/concepts/unit-definitions"),
            identifier="name",
            value="uid",
        )

        sdtm_cats, sdtm_subcats = self._get_all_cats_and_subcats()
        self.sdtm_cats = sdtm_cats
        self.sdtm_subcats = sdtm_subcats

        terms_for_columns = self._get_terms_for_columns()

        def are_items_equal(new, existing):
            existing_unit_name = existing.get("unit_definition").get("name") if existing.get("unit_definition") else None
            existing_term_uid = existing.get("ct_term").get("uid") if existing.get("ct_term") else None
            new_unit_name = new["name"] if new.get("unit_definition_uid") else None
            result = (existing.get("activity_item_class").get("name") == new.get("activity_item_class_name")
                    and existing.get("library_name") == new.get("library_name")
                    and existing_unit_name == new_unit_name
                    and existing_term_uid == new.get("ct_term_uid"))
            return result

        self.all_migrated_items = {}
        for row in readCSV:
            item_data = []
            domain = row[headers.index("GENERAL_DOMAIN_CLASS")]
            cols = ["specimen", "SDTM_DOMAIN", "sdtm_cat", "sdtm_sub_cat", "unit_dimension", "laterality", "location", "std_unit", "sdtm_variable"]
            for col in cols:
                value = row[headers.index(col)]
                if "|" in value:
                    items = value.split("|")
                else:
                    items = [value]
                for item in items:
                    data = self._create_activity_item(item, col, domain, terms_for_columns)
                    if data:
                        item_data.append(data)

            for data in item_data:
                if data:
                    activity_item_name = data["body"]["name"]
                    activity_item_class = data["body"]["activity_item_class_uid"]
                    activity_item_class_name = data["body"]["activity_item_class_name"]
                    if not existing_items_by_class.get(activity_item_class_name, {}).get(activity_item_name):
                        self.log.info(
                            f"Adding activity item '{activity_item_name}' to activity item class '{activity_item_class}'"
                        )
                        if "activity_item_class" in data["body"]:
                            data["body"].pop("activity_item_class")
                        api_tasks.append(
                            self.api.post_then_approve(
                                data=data, session=session, approve=True
                            )
                        )
                    elif not are_items_equal(data["body"], existing_items_by_class.get(activity_item_class_name, {}).get(activity_item_name)):
                        self.log.info(
                            f"Patching activity item '{activity_item_name}' to activity item class '{activity_item_class}'"
                        )
                        data["patch_path"] = path_join(
                            ACTIVITY_ITEMS_PATH,
                            existing_items_by_class[activity_item_class_name][activity_item_name].get("uid"),
                        )
                        data["new_path"] = path_join(
                            ACTIVITY_ITEMS_PATH,
                            existing_items_by_class[activity_item_class_name][activity_item_name].get("uid"),
                            "versions",
                        )
                        data["body"]["change_description"] = "Migration modification"
                        if "activity_item_class" in data["body"]:
                            data["body"].pop("activity_item_class")
                        api_tasks.append(
                            self.api.new_version_patch_then_approve(
                                data=data, session=session, approve=True
                            )
                        )
                    else:
                        self.log.info(
                            f"Identical activity item '{activity_item_name}' in item class '{activity_item_class}' already exists"
                        )
        await asyncio.gather(*api_tasks)

    async def async_run(self):

        mdr_migration_activities = load_env("MDR_MIGRATION_ACTIVITIES")
        mdr_migration_activity_sub_groups = load_env("MDR_MIGRATION_ACTIVITY_SUB_GROUPS")
        mdr_migration_activity_group = load_env("MDR_MIGRATION_ACTIVITY_GROUPS")
        mdr_migration_activity_instances = load_env("MDR_MIGRATION_ACTIVITY_INSTANCES")
        mdr_migration_activity_instance_classes = load_env(
            "MDR_MIGRATION_ACTIVITY_INSTANCE_CLASSES"
        )
        mdr_migration_activity_item_classes = load_env("MDR_MIGRATION_ACTIVITY_ITEM_CLASSES")

        timeout = aiohttp.ClientTimeout(None)
        conn = aiohttp.TCPConnector(limit=4, force_close=True)
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            await self.handle_activity_groups(mdr_migration_activity_group, session)
            await self.handle_activity_subgroups(
                mdr_migration_activity_sub_groups, session
            )
            await self.handle_activities(mdr_migration_activities, session)
            await self.handle_activity_instance_classes(
                mdr_migration_activity_instance_classes, session
            )
            await self.handle_activity_item_classes(
                mdr_migration_activity_item_classes, session
            )
            await self.handle_activity_items(
                mdr_migration_activity_instances, session
            )
            await self.handle_activity_instances(
                mdr_migration_activity_instances, session
            )

    def run(self):
        self.log.info("Importing activities")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_run())
        self.log.info("Done importing activities")


def main():
    metr = Metrics()
    migrator = Activities(metrics_inst=metr)
    migrator.run()
    metr.print()


if __name__ == "__main__":
    main()
