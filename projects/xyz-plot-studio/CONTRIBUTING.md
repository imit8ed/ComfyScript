# Contributing to XYZ Plot Studio

Thank you for your interest in contributing to XYZ Plot Studio! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/xyz-plot-studio.git
   cd xyz-plot-studio
   ```
3. **Set up development environment** (see README.md)

## Development Workflow

1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Backend tests
   cd backend && pytest tests/ -v

   # Frontend tests
   cd frontend && npm test
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** on GitHub

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for all function arguments and returns
- Write **docstrings** for all public functions
- Keep functions under 50 lines when possible
- Use **async/await** for I/O operations

**Example:**
```python
async def get_enum_values(self, enum_name: str) -> List[str]:
    """
    Get values for a specific enum.

    Args:
        enum_name: Name of the enum to retrieve

    Returns:
        List of enum values

    Raises:
        ValueError: If enum not found
    """
    # Implementation
```

### TypeScript (Frontend)

- Use **TypeScript strict mode**
- Follow **ESLint** rules
- Use **functional components** with hooks
- Keep components under 200 lines
- Extract reusable logic into custom hooks

**Example:**
```typescript
interface Props {
  value: string
  onChange: (value: string) => void
}

export const MyComponent: React.FC<Props> = ({ value, onChange }) => {
  // Implementation
}
```

## Testing Requirements

All new features must include tests:

### Backend Tests
- Unit tests for business logic
- Integration tests for API endpoints
- Mock external dependencies (ComfyUI, W&B)

### Frontend Tests
- Component tests with React Testing Library
- Integration tests for user flows
- Mock API calls with MSW

## Pull Request Guidelines

### PR Title Format
Use conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Build/tooling changes

### PR Description
Include:
1. **What** - What changes were made
2. **Why** - Why these changes were necessary
3. **How** - How the changes work
4. **Testing** - How you tested the changes
5. **Screenshots** - For UI changes

### Example PR Description
```markdown
## What
Added support for img2img workflow template

## Why
Users requested ability to do parameter sweeps on img2img workflows

## How
- Added Img2ImgConfig model
- Implemented workflow generator for img2img
- Added image upload handling
- Updated frontend to support template selection

## Testing
- Added unit tests for img2img generator
- Tested with various input images
- Verified parameter sweeps work correctly

## Screenshots
[Include screenshots of UI changes]
```

## Code Review Process

1. **Automated Checks**: All PRs must pass CI checks
   - Tests must pass
   - Linting must pass
   - Type checking must pass

2. **Manual Review**: A maintainer will review your code
   - Code quality
   - Test coverage
   - Documentation
   - Adherence to standards

3. **Feedback**: Address any feedback from reviewers

4. **Merge**: Once approved, a maintainer will merge

## Areas Needing Contribution

### High Priority
- [ ] Additional workflow templates (img2img, hires fix, ControlNet)
- [ ] Image quality metrics (aesthetic score, CLIP similarity)
- [ ] Export options (PDF, GIF/video)
- [ ] Prompt matrix support (4D plots)

### Medium Priority
- [ ] Statistical analysis features
- [ ] Multi-model comparison
- [ ] Community template marketplace
- [ ] Mobile-responsive UI improvements

### Documentation
- [ ] Video tutorials
- [ ] More example experiments
- [ ] Troubleshooting guides
- [ ] API usage examples

## Questions or Problems?

- **Questions**: Open a [GitHub Discussion](https://github.com/YourRepo/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/YourRepo/issues)
- **Features**: Open a feature request issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
