# Contributing Guide

Welcome to the Kenyan Fantasy League project! We're excited to have you contribute to this open-source fantasy sports platform for the Kenyan community.

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Git

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/kenyan-fantasy-league.git
   cd kenyan-fantasy-league
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your development values
   ```

3. **Start Development Environment**
   ```bash
   docker compose up --build
   ```

4. **Initialize Database**
   ```bash
   make migrate
   make superuser
   ```

## Project Structure

```
kenyan-fantasy-league/
├── apps/                    # Django applications
│   ├── accounts/           # User authentication
│   ├── profiles/           # User profiles  
│   ├── kpl/               # KPL data integration
│   └── fantasy/           # Fantasy game logic
├── client/                # Vue.js frontend
│   ├── src/components/    # Reusable components
│   ├── src/views/        # Page components
│   └── src/stores/       # Pinia state management
├── config/               # Django configuration
├── docs/                # Documentation (Sphinx)
├── docker/              # Docker configurations
└── util/                # Shared utilities
```

## Development Workflow

### Branching Strategy

We follow a simplified Git Flow:

```
main           # Production-ready code
develop        # Integration branch
feature/*      # Feature development
bugfix/*       # Bug fixes
hotfix/*       # Critical production fixes
```

### Branch Naming

- `feature/user-authentication`
- `bugfix/player-search-filter`
- `hotfix/security-vulnerability`
- `docs/api-documentation`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(fantasy): add player transfer functionality
fix(kpl): resolve fixture data synchronization issue
docs(api): update authentication endpoints
test(profiles): add profile update validation tests
```

## Code Standards

### Python/Django

We follow PEP 8 and Django coding standards with these tools:

#### Code Formatting
```bash
# Format code with Black
make black

# Check formatting  
make black-check

# Sort imports with isort
make isort
```

#### Linting
```bash
# Run flake8 linting
make flake8
```

#### Code Style Guidelines

**Models:**
```python
class Player(TimeStampedUUIDModel):
    """KPL player representation."""
    
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    
    class Meta:
        ordering = ["team", "name"]
        verbose_name = "Player"
        verbose_name_plural = "Players"
    
    def __str__(self):
        return f"{self.name} ({self.team.name})"
```

**Views:**
```python
class PlayerViewSet(ReadOnlyModelViewSet):
    """ViewSet for KPL players."""
    
    queryset = Player.objects.select_related('team')
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['team', 'position']
    search_fields = ['name']
```

**Services:**
```python
class FantasyService:
    """Service class for fantasy team operations."""
    
    @staticmethod
    def create_team(user: User, name: str, formation: str) -> FantasyTeam:
        """Create a new fantasy team for user."""
        if FantasyTeam.objects.filter(user=user).exists():
            raise ValidationError("User already has a fantasy team")
        
        return FantasyTeam.objects.create(
            user=user,
            name=name,
            formation=formation
        )
```

### TypeScript/Vue.js

#### Code Formatting
```bash
cd client
npm run lint         # ESLint checking
npm run format      # Prettier formatting
npm run type-check  # TypeScript checking
```

#### Component Structure
```vue
<template>
  <div class="player-card">
    <img :src="player.team.logo_url" :alt="player.team.name" />
    <h3>{{ player.name }}</h3>
    <p>{{ player.position }} - {{ player.team.name }}</p>
    <span class="value">£{{ player.current_value }}</span>
  </div>
</template>

<script setup lang="ts">
import type { Player } from '@/types/kpl'

interface Props {
  player: Player
}

defineProps<Props>()
</script>

<style scoped>
.player-card {
  @apply bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow;
}

.value {
  @apply text-green-600 font-semibold;
}
</style>
```

#### State Management (Pinia)
```typescript
export const useKPLStore = defineStore('kpl', () => {
  const teams = ref<Team[]>([])
  const players = ref<Player[]>([])
  const loading = ref(false)
  
  const fetchTeams = async (): Promise<void> => {
    loading.value = true
    try {
      const response = await api.get('/kpl/teams/')
      teams.value = response.data.results
    } catch (error) {
      console.error('Failed to fetch teams:', error)
    } finally {
      loading.value = false
    }
  }
  
  return {
    teams: readonly(teams),
    players: readonly(players),
    loading: readonly(loading),
    fetchTeams
  }
})
```

## Testing

### Backend Testing (Django)

We use pytest for Django testing:

```bash
# Run all tests
make test

# Run with coverage report
make test-html

# Run specific test file
docker compose exec api pytest apps/fantasy/tests/test_models.py

# Run specific test
docker compose exec api pytest apps/fantasy/tests/test_models.py::TestFantasyTeam::test_create_team
```

#### Test Structure
```python
import pytest
from django.contrib.auth import get_user_model
from apps.fantasy.models import FantasyTeam

User = get_user_model()

@pytest.mark.django_db
class TestFantasyTeam:
    """Test FantasyTeam model functionality."""
    
    def test_create_team(self):
        """Test creating a fantasy team."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        team = FantasyTeam.objects.create(
            user=user,
            name="Test Team",
            formation="4-3-3"
        )
        
        assert team.name == "Test Team"
        assert team.formation == "4-3-3"
        assert team.budget == 100.00
        assert team.user == user
```

### Frontend Testing (Vue.js)

```bash
cd client
npm run test          # Run unit tests
npm run test:coverage # Run with coverage
npm run test:e2e     # Run end-to-end tests
```

#### Component Testing
```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PlayerCard from '@/components/PlayerCard.vue'

describe('PlayerCard', () => {
  it('renders player information correctly', () => {
    const player = {
      id: '1',
      name: 'Michael Olunga',
      position: 'FWD',
      current_value: 8.5,
      team: {
        name: 'Gor Mahia FC',
        logo_url: 'https://example.com/logo.png'
      }
    }
    
    const wrapper = mount(PlayerCard, {
      props: { player }
    })
    
    expect(wrapper.text()).toContain('Michael Olunga')
    expect(wrapper.text()).toContain('FWD - Gor Mahia FC')
    expect(wrapper.text()).toContain('£8.5')
  })
})
```

## Database

### Migrations

```bash
# Create migrations
make makemigrations

# Apply migrations
make migrate

# Check migration status
docker compose exec api python manage.py showmigrations
```

### Migration Guidelines

1. **Always create migrations for model changes**
2. **Review migration files before committing**
3. **Test migrations in both directions** (forward and backward)
4. **Use data migrations for complex data transformations**

Example data migration:
```python
from django.db import migrations

def update_player_values(apps, schema_editor):
    Player = apps.get_model('kpl', 'Player')
    for player in Player.objects.all():
        if player.current_value is None:
            player.current_value = 4.0
            player.save()

class Migration(migrations.Migration):
    dependencies = [
        ('kpl', '0011_player_current_value'),
    ]
    
    operations = [
        migrations.RunPython(update_player_values),
    ]
```

## API Development

### Adding New Endpoints

1. **Define the model** (if needed)
2. **Create serializer**
3. **Implement view/viewset**
4. **Add URL routing**
5. **Write tests**
6. **Update API documentation**

Example:
```python
# serializers.py
class GameweekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gameweek
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active']

# views.py
class GameweekViewSet(ReadOnlyModelViewSet):
    queryset = Gameweek.objects.all()
    serializer_class = GameweekSerializer
    permission_classes = [IsAuthenticated]

# urls.py
router.register(r'gameweeks', GameweekViewSet)
```

### API Documentation

Update `docs/source/api.md` when adding new endpoints. Include:
- Endpoint URL and HTTP method
- Request/response examples
- Query parameters
- Error responses

## Pull Request Process

### Before Creating a PR

1. **Ensure all tests pass**
   ```bash
   make test
   cd client && npm run test
   ```

2. **Run code quality checks**
   ```bash
   make black flake8 isort
   cd client && npm run lint
   ```

3. **Update documentation** if needed

4. **Write descriptive commit messages**

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new linting errors
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
Include screenshots for UI changes.
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by at least one maintainer
3. **Manual testing** for significant changes
4. **Documentation review** for API/feature changes

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Version: [e.g. 1.0.0]

## Additional Context
Screenshots, logs, etc.
```

### Feature Requests

```markdown
## Feature Description
Clear description of the proposed feature.

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other solutions you've considered.

## Additional Context
Mockups, examples, etc.
```

## Development Environment

### Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| api | 8000 | Django backend |
| client | 3000 | Vue.js frontend |
| nginx | 8080 | Reverse proxy |
| postgres-db | 5432 | Database |
| redis | 6379 | Cache/message broker |
| flower | 5557 | Celery monitoring |
| selenium | 4444 | E2E testing |

### Useful Commands

```bash
# Development
make up              # Start all services
make down            # Stop all services
make logs            # View logs
make shell           # Django shell

# Database
make migrate         # Run migrations
make dbshell         # Database shell
make superuser       # Create admin user

# Code Quality
make test            # Run tests
make black           # Format Python code
make flake8          # Lint Python code
make isort           # Sort imports

# Frontend
cd client
npm run dev          # Start dev server
npm run build        # Build for production
npm run test         # Run tests
```

### Debugging

#### Backend Debugging
```python
# Add breakpoints in Django code
import pdb; pdb.set_trace()

# Or use Django debug toolbar (development)
# Install: pip install django-debug-toolbar
```

#### Frontend Debugging
```javascript
// Browser DevTools
console.log('Debug info:', data)
debugger; // Browser breakpoint

// Vue DevTools extension recommended
```

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., 1.2.3)
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version numbers bumped
- [ ] Release notes prepared
- [ ] Production deployment tested

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers
- Follow the project's technical standards
- Report issues and security vulnerabilities responsibly

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Documentation credits

## Getting Help

### Documentation
- [Quickstart Guide](quickstart.md)
- [Architecture Overview](architecture.md)
- [API Reference](api.md)

### Support Channels
- GitHub Issues for bugs
- GitHub Discussions for questions
- Documentation for guides

### Maintainers

Current project maintainers:
- @maintainer1 - Backend/DevOps
- @maintainer2 - Frontend/UI
- @maintainer3 - Product/Design

---

Thank you for contributing to the Kenyan Fantasy League! Your contributions help build a better fantasy sports experience for the Kenyan community. 🇰🇪⚽
