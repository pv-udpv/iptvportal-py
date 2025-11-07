"""JSONSQL query builder."""

from typing import Any, Optional, Union, List


class QueryBuilder:
    """Builder for JSONSQL queries.
    
    Provides Python DSL for generating JSONRPC-compatible query structures.
    Supports SELECT, INSERT, UPDATE, DELETE, and UPSERT operations.
    
    Example:
        >>> qb = QueryBuilder()
        >>> query = qb.select(
        ...     data=["id", "name"],
        ...     from_="tv_channel",
        ...     limit=10
        ... )
    """
    
    def __init__(self):
        self._request_id = 1
    
    def select(
        self,
        data: Union[str, List[Union[str, dict]]],
        from_: Union[str, List[dict]],
        where: Optional[dict] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        group_by: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """Build SELECT query.
        
        Args:
            data: Fields to select (string, list of strings, or list of dicts for aliases)
            from_: Table name or join specification
            where: WHERE conditions (use Q operators)
            order_by: ORDER BY fields
            limit: LIMIT clause
            offset: OFFSET clause
            group_by: GROUP BY fields
            
        Returns:
            JSONRPC request dict
        """
        params: dict[str, Any] = {
            "data": data,
            "from": from_
        }
        
        if where:
            params["where"] = where
        if order_by:
            params["order_by"] = order_by
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if group_by:
            params["group_by"] = group_by
        
        return self._build_request("select", params)
    
    def insert(
        self,
        into: str,
        columns: List[str],
        values: List[List[Any]],
        returning: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """Build INSERT query.
        
        Args:
            into: Table name
            columns: Column names
            values: List of value tuples
            returning: Fields to return after insert
            
        Returns:
            JSONRPC request dict
        """
        params = {
            "into": into,
            "columns": columns,
            "values": values
        }
        
        if returning:
            params["returning"] = returning
        
        return self._build_request("insert", params)
    
    def update(
        self,
        table: str,
        set_: dict[str, Any],
        where: Optional[dict] = None,
        returning: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """Build UPDATE query.
        
        Args:
            table: Table name
            set_: Fields and values to update
            where: WHERE conditions (use Q operators)
            returning: Fields to return after update
            
        Returns:
            JSONRPC request dict
        """
        params = {
            "table": table,
            "set": set_
        }
        
        if where:
            params["where"] = where
        if returning:
            params["returning"] = returning
        
        return self._build_request("update", params)
    
    def delete(
        self,
        from_: str,
        where: Optional[dict] = None,
        returning: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """Build DELETE query.
        
        Args:
            from_: Table name
            where: WHERE conditions (use Q operators)
            returning: Fields to return after delete
            
        Returns:
            JSONRPC request dict
        """
        params = {
            "from": from_
        }
        
        if where:
            params["where"] = where
        if returning:
            params["returning"] = returning
        
        return self._build_request("delete", params)
    
    def upsert(
        self,
        into: str,
        columns: List[str],
        values: List[List[Any]],
        conflict_columns: List[str],
        update_set: dict[str, Any],
        returning: Optional[Union[str, List[str]]] = None
    ) -> dict:
        """Build UPSERT query (INSERT ... ON CONFLICT ... DO UPDATE).
        
        Based on official IPTVPortal API examples. Uses PostgreSQL UPSERT syntax.
        
        Args:
            into: Table name
            columns: Column names to insert
            values: Values to insert
            conflict_columns: Columns to check for conflicts
            update_set: Fields to update on conflict (use {"excluded": "column"} for new values)
            returning: Fields to return
            
        Returns:
            JSONRPC request dict
            
        Example:
            >>> qb.upsert(
            ...     into="subscriber",
            ...     columns=["username", "password"],
            ...     values=[["user1", "pass1"]],
            ...     conflict_columns=["username"],
            ...     update_set={"password": {"excluded": "password"}},
            ...     returning=["id"]
            ... )
        """
        params = {
            "into": into,
            "columns": columns,
            "values": values,
            "on_conflict": {
                "columns": conflict_columns,
                "do": "update",
                "set": update_set
            }
        }
        
        if returning:
            params["returning"] = returning
        
        return self._build_request("insert", params)
    
    def select_subquery(
        self,
        data: Union[str, List[str]],
        from_: Union[str, List[dict]],
        where: Optional[dict] = None
    ) -> dict:
        """Build subquery for use in WHERE IN clause.
        
        Args:
            data: Fields to select
            from_: Table name
            where: WHERE conditions
            
        Returns:
            Subquery dict (not full JSONRPC request)
            
        Example:
            >>> subquery = qb.select_subquery(
            ...     data="id",
            ...     from_="subscriber",
            ...     where=Q.eq("username", "test")
            ... )
            >>> qb.delete(
            ...     from_="subscriber_package",
            ...     where=Q.in_("subscriber_id", subquery)
            ... )
        """
        subquery = {
            "select": {
                "data": data,
                "from": from_
            }
        }
        
        if where:
            subquery["select"]["where"] = where
        
        return subquery
    
    def _build_request(self, method: str, params: dict) -> dict:
        """Build JSONRPC request."""
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }
        self._request_id += 1
        return request
