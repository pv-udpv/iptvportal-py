"""Query builder for IPTVPortal JSONSQL API."""

from .builder import QueryBuilder
from .operators import Q

__all__ = ["QueryBuilder", "Q"]
