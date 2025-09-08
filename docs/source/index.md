# Kenyan Fantasy League Documentation

Welcome to the **Kenyan Fantasy League (KFL)** documentation! This is the premier platform for fantasy sports enthusiasts in Kenya, allowing you to create and manage your own fantasy teams.

## Quick Links

- [Getting Started](quickstart.md) - Get up and running in 10 minutes
- [Architecture Overview](architecture.md) - Understanding the system design
- [API Reference](api.md) - Complete API documentation
- [Configuration](configuration.md) - Environment and settings
- [Contributing](contributing.md) - How to contribute to the project

## Documentation Sections

```{toctree}
:maxdepth: 2
:caption: Getting Started

quickstart
installation
configuration
```

```{toctree}
:maxdepth: 2
:caption: User Guide

usage
features
api
```

```{toctree}
:maxdepth: 2
:caption: Development

architecture
contributing
testing
deployment
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
api/apps
```

```{toctree}
:maxdepth: 2
:caption: Operations

operations
monitoring
troubleshooting
```

## Project Overview

**Kenyan Fantasy League (KFL)** is a full-stack web application that enables fantasy sports management for Kenyan football leagues. The platform features:

- 🏆 **Fantasy Team Management** - Create and manage fantasy teams with budget constraints
- ⚽ **Real KPL Integration** - Live data from Kenyan Premier League
- 📊 **Performance Tracking** - Player stats and team rankings
- 🎮 **Interactive Interface** - Modern Vue.js frontend with responsive design
- 🔐 **User Authentication** - Secure JWT-based authentication system
- 📱 **API-First Design** - RESTful API with Django REST Framework

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework, Celery, Redis
- **Database**: PostgreSQL
- **Frontend**: Vue.js 3, TypeScript, Tailwind CSS
- **Infrastructure**: Docker, Nginx
- **Testing**: Pytest, Vue Test Utils
- **Documentation**: Sphinx with MyST (Markdown)

## Get Started

Ready to dive in? Start with our [Quickstart Guide](quickstart.md) to get the project running locally in under 10 minutes!

---

*Built with ❤️ for the Kenyan fantasy sports community*
