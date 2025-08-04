## 🤝 Contributing

We welcome contributions to ALX Project Nexus! This project follows the **open source best practices** and encourages community involvement.

### 🎯 How to Contribute

1. **🍴 Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/alx-project-nexus.git
   cd alx-project-nexus
   ```

2. **🌿 Create a feature branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   # or
   git checkout -b bugfix/fix-important-bug
   # or
   git checkout -b docs/improve-documentation
   ```

3. **💻 Make your changes**
   - Write clean, well-documented code
   - Follow the existing code style and conventions
   - Add tests for new functionality
   - Update documentation as needed

4. **🧪 Test your changes**
   ```bash
   # Run the full test suite
   pytest

   # Check code style
   black --check .
   flake8 .
   mypy .

   # Test coverage
   pytest --cov=apps --cov-report=html
   ```

5. **📝 Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   # Follow conventional commits format
   ```

6. **🚀 Push and create PR**
   ```bash
   git push origin feature/amazing-new-feature
   # Create Pull Request on GitHub
   ```

### 📋 Development Guidelines

#### Code Style
- **Python**: Follow PEP 8, use Black for formatting
- **Imports**: Use isort for import organization
- **Type Hints**: Use type hints for better code documentation
- **Docstrings**: Follow Google-style docstrings

#### Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Pull Request Guidelines
- **Clear Title**: Use descriptive titles
- **Detailed Description**: Explain what changes were made and why
- **Link Issues**: Reference related issues using `Fixes #123`
- **Screenshots**: Include screenshots for UI changes
- **Breaking Changes**: Clearly document any breaking changes

### 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment Information**
   - Python version
   - Django version
   - Operating system
   - Browser (if applicable)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots or error logs

3. **Additional Context**
   - Configuration details
   - Related issues or PRs

### 💡 Feature Requests

We love feature requests! Please provide:

- **Clear Description**: What feature you'd like to see
- **Use Case**: Why this feature would be valuable
- **Implementation Ideas**: Any thoughts on how it could work
- **Alternatives**: Other solutions you've considered

### 🏆 Recognition

Contributors will be recognized in:
- **README Contributors Section**: Listed with contributions
- **Release Notes**: Mentioned in version releases
- **Hall of Fame**: Special recognition for significant contributions
