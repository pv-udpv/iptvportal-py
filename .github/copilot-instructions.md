# Copilot Instructions: iptvportal-py

## Project Overview

- Full-featured Python SDK for IPTVPortal JSONSQL API with sync and async clients, robust authentication, Pydantic v2 models, Python DSL query builder, CRUD resource managers, and a Typer CLI.
- Follow modern Python practices for 2025: strict type hints, mypy, async/await, dependency injection, and context managers.
- Maintain separation of architectural layers (Config, Models, Query Builder, Authentication, Transport, Resources, Client, CLI).

## Coding Standards

- Use **PEP8** and enforce with flake8/black.
- All code should have **type hints**; run mypy in strict mode.
- Docstrings for every public API, method, and class using Google or NumPy style.
- Line length: 100 characters maximum.

## File Structure

- All source files are under `src/iptvportal/`.
- Main client: `client.py` (sync) and `async_client.py` (async).
- Auth and config: `auth.py`, `config.py` with Pydantic Settings.
- Models follow Pydantic v2 in `models/` directory.
- Query builder is in `query/`, with DSL and Q objects (Django-style lookups).
- Resource managers (CRUD) are in `resources/`.
- CLI logic belongs in `cli/` using Typer.
- Tests are in `tests/` with unit, integration, and e2e subdirectories.

## Patterns and Practices

### Resource Management
- Prefer **context managers** for resource cleanup.
- Use exponential backoff and retry logic for HTTP requests.
- Implement proper connection pooling.

### Async Implementation
- Async implementation relies on HTTPX with connection pooling.
- Maintain both sync and async APIs with strict separation.
- Use `asyncio.run()` in CLI when needed.

### Authentication & Session
- Session management must cache session tokens with TTL.
- Implement automatic re-authentication on token expiry.
- Support both API key and username/password authentication.

### Query Builder
- Use Django-style Q objects for complex queries.
- Provide type-safe DSL for JSONSQL construction.
- Support all JSONSQL operators (IN, LIKE, BETWEEN, etc.).

### Testing
- Use Pytest with httpx-mock for tests.
- Keep tests in `tests/` and cover all layers.
- Ensure 80%+ code coverage.
- Test edge cases, especially the query builder and resource managers.

## Example Usage

### Synchronous Client

\`\`\`python
from iptvportal import IPTVPortalClient
from iptvportal.models.subscriber import SubscriberCreate

with IPTVPortalClient() as client:
    # Create subscriber
    subscriber = client.subscribers.create(
        SubscriberCreate(username='testuser', password='secure123')
    )
    
    # List subscribers
    subscribers = client.subscribers.list(limit=10)
    
    # Disable subscriber
    client.subscribers.disable(subscriber.id)
\`\`\`

### Asynchronous Client

\`\`\`python
import asyncio
from iptvportal import AsyncIPTVPortalClient
from iptvportal.models.subscriber import SubscriberCreate

async def main():
    async with AsyncIPTVPortalClient() as client:
        subscriber = await client.subscribers.create(
            SubscriberCreate(username='testuser', password='secure123')
        )
        subscribers = await client.subscribers.list(limit=10)

asyncio.run(main())
\`\`\`

### Query Builder

\`\`\`python
from iptvportal.query import Q, QueryBuilder

query = (
    QueryBuilder('subscriber')
    .select('id', 'username', 'email')
    .where(Q(status='active') & Q(balance__gte=100))
    .order_by('-created_at')
    .limit(50)
    .build()
)
\`\`\`

## CLI Example

\`\`\`bash
# List subscribers
iptvportal subscriber list --limit 10

# Create subscriber
iptvportal subscriber create testuser --password mypass

# Update subscriber balance
iptvportal subscriber update 123 --balance 100.50

# Disable subscriber
iptvportal subscriber disable 123
\`\`\`

## Documentation

- Add API usage guides and examples to the `docs/` directory.
- Ensure CLI help and auto-completion are available via Typer.
- Document architecture and design decisions in Markdown.
- Include quickstart guide and API reference.
- Provide migration guides for major version changes.

## Dependencies

### Core
- **Pydantic v2**: Data validation and settings
- **Typer**: CLI framework
- **HTTPX**: HTTP client (sync & async)

### Development
- **Pytest**: Testing framework
- **pytest-httpx**: HTTP mocking
- **pytest-asyncio**: Async test support
- **mypy**: Static type checking
- **black**: Code formatting
- **flake8**: Linting
- **coverage**: Code coverage

## Best Practices

### Type Safety
- Ensure 100% type coverage and mypy strict mode.
- Use `TypedDict`, `Protocol`, and generics where appropriate.
- Avoid `Any` type except when absolutely necessary.

### Documentation
- All user-facing APIs must have docstring explanations and usage examples.
- Include parameter descriptions, return types, and raised exceptions.
- Provide code examples in docstrings.

### API Design
- Strict separation of sync and async APIs.
- Leverage Q objects and type-safe DSL for query construction.
- Follow robust session management and HTTP transport design.
- Use resource managers for all CRUD operations.

### Error Handling
- Define custom exceptions in `exceptions.py`.
- Provide clear error messages with actionable solutions.
- Include context in exceptions (request/response details).

### Performance
- Implement request caching where appropriate.
- Use connection pooling for HTTP requests.
- Optimize query builder for minimal overhead.

## References

- [IPTVPortal API Documentation](https://iptvportal.ru/doc/api/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Type Hints PEP 484](https://peps.python.org/pep-0484/)

## Version Support

- Python 3.11+ required
- Support latest stable Python version
- Test against Python 3.11, 3.12, and 3.13 in CI

## Security

- Never commit API keys or credentials.
- Use environment variables for sensitive configuration.
- Validate all user inputs.
- Sanitize error messages to avoid leaking sensitive information.
