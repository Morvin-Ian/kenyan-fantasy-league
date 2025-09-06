# API Reference

The Kenyan Fantasy League provides a comprehensive REST API built with Django REST Framework. All endpoints require authentication unless specified otherwise.

## Base URL

```
http://localhost:8080/api/v1/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Obtaining Tokens

```bash
# Login to get access and refresh tokens
POST /api/v1/auth/jwt/create/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refreshing Tokens

```bash
POST /api/v1/auth/jwt/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Rate Limiting

| User Type | Rate Limit |
|-----------|------------|
| Anonymous | 10 requests/minute |
| Authenticated | 1000 requests/minute |
| Premium | 12 requests/minute |

## Error Handling

The API returns standard HTTP status codes and JSON error responses:

```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Authentication Endpoints

### User Registration

Register a new user account. Account activation via email is required.

```bash
POST /api/v1/auth/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "newuser",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "re_password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "username": "newuser",
  "first_name": "John",
  "last_name": "Doe"
}
```

### User Activation

Activate user account via email link.

```bash
POST /api/v1/auth/users/activation/
Content-Type: application/json

{
  "uid": "activation-uid",
  "token": "activation-token"
}
```

### Password Reset

Request password reset email.

```bash
POST /api/v1/auth/users/reset_password/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Current User Info

Get current authenticated user information.

```bash
GET /api/v1/auth/users/me/
Authorization: Bearer <token>
```

## KPL (Kenyan Premier League) Endpoints

All KPL endpoints are read-only and require authentication.

### Teams

Get list of active KPL teams.

```bash
GET /api/v1/kpl/teams/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 18,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "team-uuid",
      "name": "Gor Mahia FC",
      "logo_url": "https://example.com/logo.png",
      "jersey_image": "/mediafiles/team_jerseys/gor_mahia.png",
      "is_relegated": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Team Detail

Get specific team information.

```bash
GET /api/v1/kpl/teams/{team_id}/
Authorization: Bearer <token>
```

### Players

Get list of KPL players.

```bash
GET /api/v1/kpl/players/
Authorization: Bearer <token>

# Filter by team
GET /api/v1/kpl/players/?team={team_id}

# Filter by position
GET /api/v1/kpl/players/?position=GKP
```

**Query Parameters:**
- `team` - Filter by team ID
- `position` - Filter by position (GKP, DEF, MID, FWD)
- `search` - Search by player name

**Response:**
```json
{
  "count": 400,
  "next": "http://localhost:8080/api/v1/kpl/players/?page=2",
  "previous": null,
  "results": [
    {
      "id": "player-uuid",
      "name": "Michael Olunga",
      "team": {
        "id": "team-uuid",
        "name": "Gor Mahia FC",
        "logo_url": "https://example.com/logo.png"
      },
      "position": "FWD",
      "jersey_number": 9,
      "age": 29,
      "current_value": 8.50,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Standings

Get current league standings.

```bash
GET /api/v1/kpl/standings/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 18,
  "results": [
    {
      "id": "standing-uuid",
      "team": {
        "id": "team-uuid",
        "name": "Gor Mahia FC",
        "logo_url": "https://example.com/logo.png"
      },
      "position": 1,
      "played": 28,
      "won": 20,
      "drawn": 5,
      "lost": 3,
      "goals_for": 58,
      "goals_against": 22,
      "goal_difference": 36,
      "points": 65,
      "form": "WWWDW"
    }
  ]
}
```

### Fixtures

Get current gameweek fixtures.

```bash
GET /api/v1/kpl/fixtures/
Authorization: Bearer <token>

# Filter by status
GET /api/v1/kpl/fixtures/?status=upcoming
```

**Query Parameters:**
- `status` - Filter by status (upcoming, live, completed, postponed)
- `team` - Filter by team ID

**Response:**
```json
{
  "count": 9,
  "results": [
    {
      "id": "fixture-uuid",
      "home_team": {
        "id": "team-uuid", 
        "name": "Gor Mahia FC",
        "logo_url": "https://example.com/logo.png"
      },
      "away_team": {
        "id": "team-uuid",
        "name": "AFC Leopards",
        "logo_url": "https://example.com/logo.png"  
      },
      "home_score": null,
      "away_score": null,
      "kick_off": "2024-01-15T15:00:00Z",
      "status": "upcoming",
      "gameweek": {
        "id": "gameweek-uuid",
        "name": "Gameweek 15",
        "is_active": true
      }
    }
  ]
}
```

## Fantasy Endpoints

Fantasy team and player management endpoints.

### Fantasy Teams

#### List User's Fantasy Teams

```bash
GET /api/v1/fantasy/teams/
Authorization: Bearer <token>
```

#### Create Fantasy Team

```bash
POST /api/v1/fantasy/teams/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Dream Team",
  "formation": "4-3-3"
}
```

**Response (201 Created):**
```json
{
  "id": "team-uuid",
  "name": "My Dream Team", 
  "budget": 100.00,
  "formation": "4-3-3",
  "free_transfers": 1,
  "total_points": 0,
  "overall_rank": null,
  "transfer_budget": 0.00,
  "user": "user-uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Fantasy Team Details

```bash
GET /api/v1/fantasy/teams/{team_id}/
Authorization: Bearer <token>
```

#### Update Fantasy Team

```bash
PUT /api/v1/fantasy/teams/{team_id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Team Name",
  "formation": "3-4-3"
}
```

#### Delete Fantasy Team

```bash
DELETE /api/v1/fantasy/teams/{team_id}/
Authorization: Bearer <token>
```

### Fantasy Players

#### List Fantasy Team Players

```bash
GET /api/v1/fantasy/players/
Authorization: Bearer <token>

# Filter by fantasy team
GET /api/v1/fantasy/players/?fantasy_team={team_id}
```

#### Add Player to Fantasy Team

```bash
POST /api/v1/fantasy/players/
Authorization: Bearer <token>
Content-Type: application/json

{
  "fantasy_team": "team-uuid",
  "player": "player-uuid",
  "is_captain": false,
  "is_vice_captain": false
}
```

**Response (201 Created):**
```json
{
  "id": "fantasy-player-uuid",
  "fantasy_team": "team-uuid",
  "player": {
    "id": "player-uuid",
    "name": "Michael Olunga", 
    "position": "FWD",
    "current_value": 8.50,
    "team": {
      "name": "Gor Mahia FC",
      "logo_url": "https://example.com/logo.png"
    }
  },
  "is_captain": false,
  "is_vice_captain": false,
  "gameweek_added": {
    "id": "gameweek-uuid",
    "name": "Gameweek 15"
  },
  "purchase_price": 8.50
}
```

#### Remove Player from Fantasy Team

```bash
DELETE /api/v1/fantasy/players/{fantasy_player_id}/
Authorization: Bearer <token>
```

### Fantasy Team Actions

#### Set Captain

```bash
POST /api/v1/fantasy/teams/{team_id}/set_captain/
Authorization: Bearer <token>
Content-Type: application/json

{
  "player_id": "player-uuid"
}
```

#### Set Vice Captain  

```bash
POST /api/v1/fantasy/teams/{team_id}/set_vice_captain/
Authorization: Bearer <token>
Content-Type: application/json

{
  "player_id": "player-uuid"
}
```

#### Make Transfers

```bash
POST /api/v1/fantasy/teams/{team_id}/make_transfers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "transfers": [
    {
      "player_out": "old-player-uuid",
      "player_in": "new-player-uuid"
    }
  ]
}
```

## Profile Endpoints

User profile management.

### Get Profile

Get current user's profile information.

```bash
GET /api/v1/profile/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "profile-uuid",
  "user": {
    "id": "user-uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "avatar": null,
  "bio": "Fantasy football enthusiast",
  "location": "Nairobi, Kenya",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Update Profile

```bash
PUT /api/v1/profile/update/{profile_uuid}/
Authorization: Bearer <token>
Content-Type: multipart/form-data

{
  "bio": "Updated bio text",
  "location": "Mombasa, Kenya",
  "avatar": <file>
}
```

## Data Models

### Key Model Schemas

#### User
```json
{
  "id": "uuid",
  "username": "string",
  "email": "email",
  "first_name": "string",
  "last_name": "string",
  "is_active": "boolean",
  "date_joined": "datetime"
}
```

#### Team (KPL)
```json
{
  "id": "uuid",
  "name": "string",
  "logo_url": "url",
  "jersey_image": "image_url",
  "is_relegated": "boolean",
  "created_at": "datetime"
}
```

#### Player (KPL)
```json
{
  "id": "uuid", 
  "name": "string",
  "team": "Team object",
  "position": "GKP|DEF|MID|FWD",
  "jersey_number": "integer",
  "age": "integer",
  "current_value": "decimal",
  "created_at": "datetime"
}
```

#### Fantasy Team
```json
{
  "id": "uuid",
  "user": "uuid",
  "name": "string",
  "budget": "decimal",
  "formation": "string",
  "free_transfers": "integer",
  "total_points": "integer",
  "overall_rank": "integer",
  "transfer_budget": "decimal",
  "created_at": "datetime"
}
```

## Pagination

All list endpoints use cursor pagination:

```json
{
  "count": 100,
  "next": "http://localhost:8080/api/v1/kpl/players/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 30, max: 100)

## Filtering and Search

### Common Filters

Most list endpoints support filtering:

```bash
# Search by name
GET /api/v1/kpl/players/?search=olunga

# Filter by related field
GET /api/v1/kpl/players/?team=team-uuid

# Multiple filters
GET /api/v1/kpl/players/?position=FWD&team=team-uuid
```

### Ordering

```bash
# Order by field
GET /api/v1/kpl/standings/?ordering=position

# Reverse order
GET /api/v1/kpl/standings/?ordering=-points
```

## Webhooks

*Webhooks are planned for future releases to notify external systems of events like:*
- New fixture results
- Player transfers
- Gameweek completion

## Rate Limiting Headers

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## API Versioning

The API uses URL path versioning:
- Current version: `v1`
- Base URL: `/api/v1/`

## Testing the API

### Using curl

```bash
# Get access token
TOKEN=$(curl -X POST http://localhost:8080/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access')

# Make authenticated request
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/v1/kpl/teams/
```

### Using Python requests

```python
import requests

# Login
response = requests.post('http://localhost:8080/api/v1/auth/jwt/create/', {
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
teams = requests.get('http://localhost:8080/api/v1/kpl/teams/', headers=headers)
print(teams.json())
```

## OpenAPI/Swagger Documentation

*Note: OpenAPI documentation generation is planned. The API will be documented using `drf-spectacular` for interactive API exploration.*

Future endpoint: `http://localhost:8080/api/v1/docs/`

---

*This API documentation reflects the current implementation. For the latest updates, refer to the source code or contact the development team.*
