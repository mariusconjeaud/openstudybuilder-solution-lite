from clinical_mdr_api.domain_repositories.models.generic import Conjunction
from clinical_mdr_api.domain_repositories.models.template_parameter import (
    TemplateParameter,
    TemplateParameterTermRoot,
)


class TemplateParameterRepository:
    def _get_values_for_parameter(self, parameter: TemplateParameter):
        all_terms = parameter.has_parameter_term.all()
        data = []
        term: TemplateParameterTermRoot
        for term in all_terms:
            latest = term.has_latest_final.single()
            if latest is not None:
                data.append({"name": latest.name, "uid": term.uid})
        return data

    def parameter_name_exists(self, parameter_name: str) -> bool:
        return TemplateParameter.nodes.get_or_none(name=parameter_name) is not None

    def is_parameter_term_uid_valid_for_parameter_name(
        self,
        *,
        parameter_name: str,
        parameter_term_uid: str,
    ) -> bool:
        return TemplateParameterTermRoot.check_parameter_term_exists(
            parameter_name, parameter_term_uid
        )

    def close(self) -> None:
        pass

    def get_conjunction_or_create_if_not_exists(self, conjunction_str: str):
        result = Conjunction.nodes.get_or_none(string=conjunction_str)
        if result is None:
            conjunction = Conjunction(string=conjunction_str)
            conjunction.save()
        else:
            conjunction = result
        return conjunction
