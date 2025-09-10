# API Reference

This section provides auto-generated API documentation from the Django codebase using Sphinx autodoc.

## Apps Overview

The KFL API is organized into Django apps, each handling specific functionality:

```{toctree}
:maxdepth: 2

accounts
profiles
kpl
fantasy
```

## Quick Reference

### Authentication Endpoints
- **POST** `/api/v1/auth/jwt/create/` - Login and get JWT tokens
- **POST** `/api/v1/auth/users/` - User registration
- **POST** `/api/v1/auth/jwt/refresh/` - Refresh access token

### KPL Data Endpoints
- **GET** `/api/v1/kpl/teams/` - List KPL teams
- **GET** `/api/v1/kpl/players/` - List KPL players
- **GET** `/api/v1/kpl/fixtures/` - List KPL fixtures
- **GET** `/api/v1/kpl/standings/` - League standings

### Fantasy Endpoints
- **GET** `/api/v1/fantasy/teams/` - List fantasy teams
- **POST** `/api/v1/fantasy/teams/` - Create fantasy team
- **GET** `/api/v1/fantasy/players/` - List fantasy players

### Profile Endpoints
- **GET** `/api/v1/profile/` - Get user profile
- **PUT** `/api/v1/profile/update/{id}/` - Update profile

## Authentication

All API endpoints require JWT authentication unless specified otherwise. Include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Response Format

All API responses follow a consistent format:

**Successful Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8080/api/v1/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

## Rate Limiting

| User Type | Rate Limit |
|-----------|------------|
| Anonymous | 10 requests/minute |
| Authenticated | 1000 requests/minute |

## Pagination

List endpoints use offset-based pagination with 30 items per page by default. Use the `page` parameter to navigate:

```
GET /api/v1/kpl/players/?page=2
```

