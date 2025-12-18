# Contributing to Competitive Intelligence Monitor

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/competitive-intelligence.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes: `python3 test_results.py`
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Install dependencies
pip install -e .

# Copy environment template
cp .env.example .env

# Add your API keys to .env
# Run tests
python3 test_results.py
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

## Testing

Before submitting a PR:

1. **Run the test suite**:
   ```bash
   python3 test_results.py
   ```

2. **Test with fresh data**:
   ```bash
   python3 clear_and_run.py
   ```

3. **Verify report generation**:
   ```bash
   python3 generate_report.py
   ```

## Adding New Features

### Adding a New Data Source

1. Create a new `SourceSpec` class in `main.py`
2. Implement the `@source_connector` decorator
3. Add `async def list()` and `async def get_value()` methods
4. Register in the flow definition
5. Update documentation

Example:
```python
@source_connector(spec_cls=YourSource, key_type=YourKey, value_type=YourValue)
class YourSourceConnector:
    async def list(self) -> AsyncIterator[PartialSourceRow]:
        # Fetch data
        pass

    async def get_value(self, key) -> PartialSourceRowData:
        # Get specific item
        pass
```

### Adding a New Event Type

1. Update `CompetitiveEvent` dataclass in `main.py`
2. Modify LLM extraction instruction
3. Add query handlers if needed
4. Update documentation

### Adding a Query Handler

```python
@competitive_intelligence_flow.query_handler()
def your_query(param1: str, param2: int = 10) -> cocoindex.QueryOutput:
    # Query logic
    return cocoindex.QueryOutput(results=results)
```

## Documentation

When adding features, update:
- `README.md` - User-facing documentation
- `CLAUDE.md` - Developer guidance
- `USAGE_GUIDE.md` - Usage examples
- Docstrings in code

## Pull Request Guidelines

### PR Title Format
- `feat: Add new feature`
- `fix: Fix bug description`
- `docs: Update documentation`
- `refactor: Refactor code`
- `test: Add tests`

### PR Description Should Include
- What changes were made
- Why the changes were made
- How to test the changes
- Screenshots (if UI changes)
- Related issues

### Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass (`python3 test_results.py`)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits (API keys, passwords)

## Reporting Issues

When reporting bugs, include:
- Python version (`python3 --version`)
- CocoIndex version (`pip show cocoindex`)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces
- Environment details (OS, database version)

## Feature Requests

Feature requests are welcome! Please include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Willingness to implement

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

- Open an issue for questions
- Check existing documentation first
- Search closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
