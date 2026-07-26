# Contributing to Digital Art Platform

Thank you for your interest in contributing to the Digital Art Platform! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Git
- Python 3.11+ (for backend)
- Node.js 18+ (for web dashboard)
- PostgreSQL 15+
- Redis 7+
- Docker (optional but recommended)

### Development Setup

1. **Fork the Repository**

   Click the "Fork" button on GitHub to create your own copy of the repository.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/digital-art-platform.git
   cd digital-art-platform
   ```

3. **Add Upstream Remote**

   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/digital-art-platform.git
   ```

4. **Set Up Development Environment**

   Follow the setup instructions in the README for each component you'll be working on.

## How to Contribute

### Reporting Bugs

1. Check the [Issues](https://github.com/yourusername/digital-art-platform/issues) page to see if the bug has already been reported
2. If not, create a new issue using the **Bug Report** template
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, browser, versions)

### Suggesting Features

1. Check existing issues to avoid duplicates
2. Create a new issue using the **Feature Request** template
3. Include:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Mockups or examples (if applicable)

### Submitting Code Changes

#### 1. Create a Branch

```bash
# Make sure you're on the latest main branch
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

Branch naming conventions:
- `feature/add-ai-recommendations`
- `bugfix/fix-image-upload`
- `refactor/improve-api-performance`
- `docs/update-deployment-guide`
- `test/add-artwork-service-tests`

#### 2. Make Your Changes

- Follow the [Coding Standards](./CODING_STANDARDS.md)
- Write clear, self-documenting code
- Add comments for complex logic
- Update documentation as needed
- Add or update tests

#### 3. Commit Your Changes

Follow the **Conventional Commits** specification:

```bash
git add .
git commit -m "feat(api): add artwork recommendation endpoint

Implement AI-powered artwork recommendations based on user viewing
history and preferences. Uses OpenAI embeddings for similarity search.

Closes #123"
```

Commit message format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

#### 4. Push Your Changes

```bash
git push origin feature/your-feature-name
```

#### 5. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill out the pull request template
5. Link related issues (e.g., "Closes #123")
6. Request review from maintainers

### Pull Request Guidelines

#### Before Submitting

- [ ] Code follows the project's [Coding Standards](./CODING_STANDARDS.md)
- [ ] Tests pass locally (`pytest` for backend, `npm test` for frontend)
- [ ] Linting passes (`black`, `flake8`, `mypy`, `eslint`)
- [ ] Documentation is updated
- [ ] Commit messages follow Conventional Commits
- [ ] Branch is up to date with main

#### PR Title

Use Conventional Commits format:
```
feat(backend): add artwork recommendation API
fix(web): prevent memory leak in image carousel
docs: update deployment guide
```

#### PR Description

Use the provided template and include:
- What: What changes were made
- Why: Why these changes were necessary
- How: How the changes were implemented
- Testing: How to test the changes
- Screenshots: For UI changes
- Related Issues: Link to issues

#### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR
4. Your contribution will be included in the next release!

## Development Workflow

### Working with Git

#### Sync with Upstream

Regularly sync your fork with the upstream repository:

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

#### Rebasing Your Branch

Keep your feature branch up to date:

```bash
git checkout feature/your-feature-name
git rebase main

# If there are conflicts, resolve them and continue
git add .
git rebase --continue

# Force push (only to your own branch!)
git push origin feature/your-feature-name --force
```

### Testing

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/unit/test_artwork_service.py

# Run specific test
pytest app/tests/unit/test_artwork_service.py::test_create_artwork
```

#### Frontend Tests

```bash
cd web-dashboard

# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### Code Quality

#### Backend (Python)

```bash
cd backend

# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
pylint app/
```

#### Frontend (TypeScript)

```bash
cd web-dashboard

# Format code
npm run format

# Linting
npm run lint
npm run lint:fix

# Type checking
npm run type-check
```

## Project Structure

Understanding the project structure helps you know where to make changes:

```
DigitalArtPlatform/
├── backend/              # Python FastAPI backend
├── web-dashboard/        # React + TypeScript web app
├── ios-app/             # Swift iOS app
├── samsung-tv-app/      # Tizen TV app
├── raspberry-pi-player/ # Python display client
├── shared/              # Shared code and resources
└── documentation/       # Project documentation
```

## Areas to Contribute

### Good First Issues

Look for issues labeled `good first issue` - these are great for newcomers!

Example areas:
- Add unit tests
- Fix typos in documentation
- Improve error messages
- Add museum API integrations
- Enhance UI components

### Help Wanted

Issues labeled `help wanted` are important and need community support:
- Performance optimizations
- Accessibility improvements
- Internationalization
- Platform-specific features

### Feature Development

Major features require more experience:
- AI features (recommendations, generation)
- Advanced search
- Smart scheduling
- Additional platform support

## Style Guidelines

### Code Style

Follow the [Coding Standards](./CODING_STANDARDS.md) document for:
- Python (PEP 8 with modifications)
- TypeScript (Airbnb style guide)
- Swift (Swift API Design Guidelines)
- JavaScript (Airbnb style guide)

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex systems
- Keep documentation up to date with code changes

### Commit Messages

Good commit messages:
```
feat(api): add pagination to artworks endpoint

Implement cursor-based pagination for better performance with large
datasets. Includes limit, offset, and cursor parameters.

- Add pagination parameters to endpoint
- Update response format with pagination metadata
- Add tests for pagination edge cases

Closes #234
```

Bad commit messages:
```
fix stuff
update code
wip
```

## Communication

### GitHub Issues

- For bug reports, feature requests, and discussions
- Use appropriate labels
- Be respectful and constructive

### Pull Request Comments

- Ask questions if something is unclear
- Provide constructive feedback
- Suggest improvements, don't just criticize

### Email

For security vulnerabilities, email: security@digitalartplatform.com

## Recognition

Contributors will be recognized in:
- [CONTRIBUTORS.md](./CONTRIBUTORS.md) file
- Release notes for significant contributions
- GitHub's contributor graph

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search closed issues
3. Open a new issue with the `question` label
4. Join our community Discord (link in README)

Thank you for contributing to Digital Art Platform! 🎨
