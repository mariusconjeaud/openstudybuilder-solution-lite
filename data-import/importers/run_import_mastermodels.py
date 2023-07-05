from .utils.importer import BaseImporter, open_file, open_file_async
from .utils.path_join import path_join
from .utils.metrics import Metrics
from .functions.parsers import map_boolean
import asyncio
import aiohttp
import csv
from typing import Optional, Sequence, Any

from .functions.utils import load_env

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
SAMPLE = load_env("MDR_MIGRATION_SAMPLE", default="False") == "True"
API_BASE_URL = load_env("API_BASE_URL")
MDR_MIGRATION_MASTER_MODEL_DATASETS = load_env("MDR_MIGRATION_MASTER_MODEL_DATASETS")
MDR_MIGRATION_MASTER_MODEL_VARIABLES = load_env("MDR_MIGRATION_MASTER_MODEL_VARIABLES")

MASTER_MODELS_PATH_PREFIX = "/standards/master-models/"
MASTER_MODELS_PATH = MASTER_MODELS_PATH_PREFIX + "models"
MASTER_MODELS_DATASETS_PATH = MASTER_MODELS_PATH_PREFIX + "datasets"
MASTER_MODELS_VARIABLES_PATH = MASTER_MODELS_PATH_PREFIX + "variables"
ACTIVITY_INSTANCE_CLASSES_PATH = "/activity-instance-classes"
ACTIVITY_ITEM_CLASSES_PATH = "/activity-item-classes"


# MasterModels with datasets and variables
class MasterModels(BaseImporter):
    logging_name = "master_models"

    def __init__(self, api=None, metrics_inst=None, cache=None):
        super().__init__(api=api, metrics_inst=metrics_inst, cache=cache)

    def parse_bool(self, cell):
        if cell is None:
            return None
        else:
            return cell == "Y"

    def parse_instance_class_name(self, name):
        parsed = name.replace("AP ", "AssociatedPersons")
        parsed = parsed.replace(" ", "").lower()
        if parsed.endswith("s"):
            parsed = parsed[:-1]
        return parsed

    def parse_item_class_name(self, name):
        return name.replace(" ", "").lower()

    async def handle_master_model(self, session):
        api_tasks = []

        data = {
            "body": {
                "ig_uid": "SDTMIG",
                "ig_version_number": "3.2",
                "version_number": "15",
            },
        }
        self.log.info(
            f"Add master model for Implemention Guide '{data['body']['ig_uid']}' version '{data['body']['ig_version_number']}'"
        )

        api_tasks.append(
            self.api.post_to_api_async(
                url=MASTER_MODELS_PATH, body=data["body"], session=session
            )
        )
        await asyncio.gather(*api_tasks)

    @open_file_async()
    async def handle_datasets(self, csvfile, session):
        # Populate master model datasets
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        api_tasks = []

        existing_instance_classes = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_INSTANCE_CLASSES_PATH),
            identifier="name",
            value="uid",
        )

        existing_instance_classes = {
            self.parse_instance_class_name(i): v
            for i, v in existing_instance_classes.items()
        }

        for row in readCSV:
            data = {
                "body": {
                    "dataset_uid": row[headers.index("Table")],
                    "master_model_name": "sdtmig_mastermodel_3.2_NN15",
                    "master_model_version_number": "15",
                    "description": None,
                    "is_basic_std": self.parse_bool(row[headers.index("basic_std")]),
                    "xml_path": row[headers.index("XmlPath")],
                    "xml_title": row[headers.index("XmlTitle")],
                    "structure": row[headers.index("Structure")],
                    "purpose": row[headers.index("Purpose")],
                    "keys": row[headers.index("Keys")].split(" ")
                    if row[headers.index("Keys")]
                    else None,
                    "sort_keys": row[headers.index("SortKeys")]
                    if row[headers.index("SortKeys")]
                    else None,
                    "comment": row[headers.index("comment")],
                    "ig_comment": row[headers.index("IGcomment")],
                    "map_domain_flag": self.parse_bool(
                        row[headers.index("map_domain_flag")]
                    ),
                    "suppl_qual_flag": self.parse_bool(
                        row[headers.index("suppl_qual_flag")]
                    ),
                    "include_in_raw": self.parse_bool(
                        row[headers.index("include_in_raw")]
                    ),
                    "gen_raw_seqno_flag": self.parse_bool(
                        row[headers.index("gen_raw_seqno_flag")]
                    ),
                    "enrich_build_order": row[headers.index("enrich_build_order")],
                    "activity_instance_class_uid": existing_instance_classes.get(
                        self.parse_instance_class_name(row[headers.index("Class")]),
                        None,
                    )
                    if row[headers.index("Class")]
                    else None,
                },
            }
            self.log.info(
                f"Add master model dataset '{data['body']['dataset_uid']}' to master model '{data['body']['master_model_name']}'"
            )
            api_tasks.append(
                self.api.post_to_api_async(
                    url=MASTER_MODELS_DATASETS_PATH, body=data["body"], session=session
                )
            )
        await asyncio.gather(*api_tasks)

    @open_file_async()
    async def handle_variables(self, csvfile, session):
        # Populate master model variables
        readCSV = csv.reader(csvfile, delimiter=",")
        headers = next(readCSV)
        api_tasks = []

        existing_item_classes = self.api.get_all_identifiers(
            self.api.get_all_from_api(ACTIVITY_ITEM_CLASSES_PATH),
            identifier="name",
            value="uid",
        )

        existing_item_classes = {
            self.parse_item_class_name(i): v for i, v in existing_item_classes.items()
        }

        for row in readCSV:
            data = {
                "body": {
                    "class_uid": row[headers.index("table")],
                    "variable_uid": row[headers.index("column")].replace("__", "--"),
                    "master_model_version_number": "15",
                    "description": None,
                    "is_basic_std": self.parse_bool(row[headers.index("basic_std")]),
                    "variable_type": row[headers.index("type")],
                    "length": row[headers.index("length")],
                    "display_format": row[headers.index("displayformat")],
                    "xml_datatype": row[headers.index("xmldatatype")],
                    "xml_codelist": row[headers.index("xmlcodelist")],
                    "xml_codelist_multi": None,
                    "core": row[headers.index("core")],
                    "role": row[headers.index("role")],
                    "term": row[headers.index("term")],
                    "algorithm": row[headers.index("algorithm")],
                    "qualifiers": row[headers.index("qualifiers")].split(" ")
                    if row[headers.index("qualifiers")]
                    else None,
                    "comment": row[headers.index("comment")],
                    "ig_comment": row[headers.index("IGcomment")],
                    "map_var_flag": self.parse_bool(row[headers.index("map_var_flag")]),
                    "fixed_mapping": row[headers.index("fixed_mapping")],
                    "include_in_raw": self.parse_bool(
                        row[headers.index("include_in_raw")]
                    ),
                    "nn_internal": self.parse_bool(row[headers.index("nn_internal")]),
                    "value_lvl_where_cols": None,
                    "value_lvl_label_col": None,
                    "value_lvl_collect_ct_val": None,
                    "value_lvl_ct_codelist_id_col": None,
                    "enrich_rule": None,
                    "xml_codelist_values": row[
                        headers.index("xmlcodelistvalues")
                    ].split(" ")
                    if row[headers.index("xmlcodelistvalues")]
                    else None,
                    "enrich_build_order": None,
                    "activity_item_class_uid": existing_item_classes.get(
                        self.parse_item_class_name(
                            row[headers.index("activity_item_class")]
                        ),
                        None,
                    )
                    if row[headers.index("activity_item_class")]
                    else None,
                },
            }
            self.log.info(
                f"Add master model variable '{data['body']['variable_uid']}' to dataset '{data['body']['class_uid']}'"
            )
            api_tasks.append(
                self.api.post_to_api_async(
                    url=MASTER_MODELS_VARIABLES_PATH, body=data["body"], session=session
                )
            )
        await asyncio.gather(*api_tasks)

    async def async_run(self):
        timeout = aiohttp.ClientTimeout(None)
        conn = aiohttp.TCPConnector(limit=4, force_close=True)
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            await self.handle_master_model(session)
            await self.handle_datasets(MDR_MIGRATION_MASTER_MODEL_DATASETS, session)
            await self.handle_variables(MDR_MIGRATION_MASTER_MODEL_VARIABLES, session)

    def run(self):
        self.log.info("Importing master models")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_run())
        self.log.info("Done importing master models")


def main():
    metr = Metrics()
    migrator = MasterModels(metrics_inst=metr)
    migrator.run()
    metr.print()


if __name__ == "__main__":
    main()
