import os
import pytest
from iptvportal import IPTVPortalClient

def test_connect_and_query_media():
    """
    Test connection with credentials from env and select 10 media records.
    """
    username = os.getenv("IPTVPORTAL_CLIENT__USERNAME", "admin")
    password = os.getenv("IPTVPORTAL_CLIENT__PASSWORD", "changeme")
    domain = os.getenv("IPTVPORTAL_DOMAIN", "https://iptvportal.ru")
    api_url = os.getenv("IPTVPORTAL_API_URL", f"{domain}/api/jsonrpc")
    client = IPTVPortalClient(
        username=username,
        password=password,
        apiurl=api_url
    )
    with client:
        query = client.query.select(
            data=["id", "title", "category", "year"],
            from_="media",
            limit=10
        )
        result = client.execute(query)
        assert isinstance(result, list)
        assert len(result) <= 10
        for row in result:
            assert "id" in row
            assert "title" in row
