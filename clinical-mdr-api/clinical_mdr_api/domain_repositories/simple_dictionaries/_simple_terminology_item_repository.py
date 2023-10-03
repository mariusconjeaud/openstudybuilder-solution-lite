from typing import Collection

# noinspection PyProtectedMember
from clinical_mdr_api.domains.simple_dictionaries.simple_terminology_item import (
    SimpleTerminologyItem,
)


class SimpleTerminologyItemRepository:
    def find_by_code_and_codelist_code(
        self, code: str, codelist_code: str
    ) -> SimpleTerminologyItem | None:
        raise NotImplementedError

    def find_by_codelist_code(
        self, codelist_code: str
    ) -> Collection[SimpleTerminologyItem]:
        raise NotImplementedError

    def close(self) -> None:
        pass

    def __del__(self):
        self.close()
