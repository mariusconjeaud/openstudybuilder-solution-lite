class DataModelVariable:
    def __init__(self, href: str):
        self.href = href

    def set_attributes(
        self,
        name: str,
        title: str,
        label: str,
        description: str,
        ordinal: str,
        role: str,
        role_description: str,
        simple_datatype: str,
        definition: str,
        implementation_notes: str,
        mapping_instructions: str,
        prompt: str,
        question_text: str,
        completion_instructions: str,
        core: str,
        codelists: "list[str]",
        implements_variables: "list[str]",
        mapping_targets: "list[str]",
        prior_version: str,
    ):
        self.name: str = name
        self.title: str = title
        self.label: str = label
        self.description: str = description if description else definition
        self.ordinal: str = ordinal
        self.role: str = role
        self.role_description: str = role_description
        self.simple_datatype: str = simple_datatype
        self.codelists: list[str] = codelists
        self.prior_version: str = prior_version

        # CDASH & CDASHIG specific
        self.implementation_notes: str = implementation_notes
        self.mapping_instructions: str = mapping_instructions
        self.prompt: str = prompt
        self.question_text: str = question_text
        self.completion_instructions: str = completion_instructions

        # IG specific
        self.core: str = core
        self.implements_variables: list[str] = implements_variables

        # CDASHIG specific
        self.mapping_targets: list[str] = mapping_targets
