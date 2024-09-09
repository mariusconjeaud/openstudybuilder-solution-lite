"""
This list must contain all routes of the main application as (path:str, method:str, required_roles:Set[str])
"""


ALL_ROUTES_METHODS_ROLES = (("/v1/studies", "GET", {"Study.Read"}),)
