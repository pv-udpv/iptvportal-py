"""Q operators for building WHERE conditions."""

from typing import Any, List


class Q:
    """Helper for building WHERE conditions in JSONSQL queries.
    
    Provides a clean Python interface for building SQL-like conditions
    that are translated into JSONSQL format.
    
    Example:
        >>> Q.and_(
        ...     Q.eq("status", "active"),
        ...     Q.gt("views", 1000)
        ... )
        {'and': [{'eq': ['status', 'active']}, {'gt': ['views', 1000]}]}
    """
    
    @staticmethod
    def eq(field: str, value: Any) -> dict:
        """Equal: field = value"""
        return {"eq": [field, value]}
    
    @staticmethod
    def neq(field: str, value: Any) -> dict:
        """Not equal: field != value"""
        return {"neq": [field, value]}
    
    @staticmethod
    def gt(field: str, value: Any) -> dict:
        """Greater than: field > value"""
        return {"gt": [field, value]}
    
    @staticmethod
    def gte(field: str, value: Any) -> dict:
        """Greater than or equal: field >= value"""
        return {"gte": [field, value]}
    
    @staticmethod
    def lt(field: str, value: Any) -> dict:
        """Less than: field < value"""
        return {"lt": [field, value]}
    
    @staticmethod
    def lte(field: str, value: Any) -> dict:
        """Less than or equal: field <= value"""
        return {"lte": [field, value]}
    
    @staticmethod
    def in_(field: str, values: List[Any]) -> dict:
        """IN: field IN (values)"""
        return {"in": [field, values]}
    
    @staticmethod
    def like(field: str, pattern: str) -> dict:
        """LIKE: field LIKE pattern"""
        return {"like": [field, pattern]}
    
    @staticmethod
    def ilike(field: str, pattern: str) -> dict:
        """ILIKE: field ILIKE pattern (case-insensitive)"""
        return {"ilike": [field, pattern]}
    
    @staticmethod
    def is_(field: str, value: Any) -> dict:
        """IS: field IS value (for NULL checks)"""
        return {"is": [field, value]}
    
    @staticmethod
    def is_not(field: str, value: Any) -> dict:
        """IS NOT: field IS NOT value"""
        return {"is_not": [field, value]}
    
    @staticmethod
    def and_(*conditions: dict) -> dict:
        """AND: condition1 AND condition2 AND ..."""
        return {"and": list(conditions)}
    
    @staticmethod
    def or_(*conditions: dict) -> dict:
        """OR: condition1 OR condition2 OR ..."""
        return {"or": list(conditions)}
    
    @staticmethod
    def not_(condition: dict) -> dict:
        """NOT: NOT condition"""
        return {"not": [condition]}
