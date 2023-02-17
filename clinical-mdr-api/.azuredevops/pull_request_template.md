Before submitting this PR, please make sure to address the following checklist:

## Basics
- [ ] Main branch is merged into your PR branch
- [ ] There are no merge conflicts
- [ ] Links to related PRs are included
- [ ] Are you including new dependencies? 
- [ ] Are they in a stable state and widely used?
- [ ] Are their licences appropriate?

## Quality  
- [ ] Code builds clean without any errors or warnings
- [ ] No issues reported by SonarQube
- [ ] No issues reported by schemathesis
- [ ] No warnings reported by pytest
- [ ] Tests cover the implemented functionality/code sufficiently
- [ ] Consider refactoring code that needs it, e.g. remove duplicate lines by adding reusable methods

## Performance
- [ ] Performance of endpoints is satisfactory
- [ ] Are API calls paginated where appropriate?
- [ ] Is there a simpler and faster API endpoint that provides only the needed data?
- [ ] If filtering is applied, can we include it in the database query instead of applying it after retrieving all instances?
- [ ] Can many small calls be replaced by fewer larger ones?

## Documentation
- [ ] API documentation (OpenAPI specification) is sufficient and in accordance with the implemented functionality
- [ ] Descriptions/examples of API endpoints/parameters are grammatically and semantically correct, and easy to use by API consumers
- [ ] Default/example values of API query parameters do not produce errors when consumer tries to send a request via SwaggerUI
- [ ] Physical data model is in sync with our nemodel data model (defined in `domain_repositories/models` folder)
- [ ] Relationship cardinalities in the physical data model are the same as defined in the `domain_repositories/models` folder
- [ ] `README` file is up-to-date

## Other
- [ ] Are there any breaking changes to existing API endpoints that affect other systems?
- [ ] If yes, we need to inform client applications to synchronize with the changes (e.g. frontend, Word add-in, data-migration/data-import repos etc.)

---

