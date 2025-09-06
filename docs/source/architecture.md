# Architecture Overview

This document provides a comprehensive overview of the Kenyan Fantasy League (KFL) system architecture, including its components, data flow, and design decisions.

## System Context

```{mermaid}
graph TB
    subgraph "External Systems"
        KPL[Kenyan Premier League APIs]
        Email[Email Services]
        CDN[Content Delivery Network]
    end
    
    subgraph "KFL System"
        Users[Users] --> Frontend[Vue.js Frontend]
        Frontend --> API[Django REST API]
        API --> DB[(PostgreSQL)]
        API --> Cache[(Redis)]
        API --> Tasks[Celery Workers]
        Tasks --> KPL
        API --> Email
        Frontend --> CDN
    end
```

## Container Architecture

The KFL system is containerized using Docker and orchestrated with Docker Compose:

```{mermaid}
graph TB
    subgraph "Docker Network: fpl-vue"
        subgraph "Web Tier"
            NGINX[nginx:80] --> API[api:8000]
            Client[client:3000]
        end
        
        subgraph "Application Tier"
            API --> Worker[celery_worker]
            API --> Beat[celery_beat]
            Worker --> Beat
            Flower[flower:5555] --> Worker
        end
        
        subgraph "Data Tier"
            API --> Redis[redis:6379]
            API --> DB[(postgres-db:5432)]
            Worker --> Redis
            Worker --> DB
        end
        
        subgraph "Testing"
            Selenium[selenium:4444]
        end
    end
```

## Application Architecture

### Backend (Django)

The backend follows Django's app-based architecture with clear separation of concerns:

```{mermaid}
graph TD
    subgraph "Django Project"
        subgraph "Core Config"
            Settings[config/settings/]
            URLs[config/urls.py]
            WSGI[config/wsgi.py]
            Celery[config/celery.py]
        end
        
        subgraph "Apps"
            Accounts[apps/accounts/]
            Profiles[apps/profiles/]
            KPL[apps/kpl/]
            Fantasy[apps/fantasy/]
        end
        
        subgraph "Utilities"
            Utils[util/models.py]
        end
    end
```

#### App Responsibilities

| App | Purpose | Key Models |
|-----|---------|------------|
| **accounts** | User authentication and management | `User`, Custom auth manager |
| **profiles** | User profiles and social features | `Profile`, User preferences |
| **kpl** | Kenyan Premier League data integration | `Team`, `Player`, `Fixture`, `Gameweek` |
| **fantasy** | Fantasy league game logic | `FantasyTeam`, `FantasyPlayer`, `PlayerPerformance` |

### Frontend (Vue.js)

The frontend is a Single Page Application (SPA) built with Vue.js 3:

```{mermaid}
graph TD
    subgraph "Vue.js Application"
        subgraph "Core"
            Main[main.ts] --> App[App.vue]
            Router[router/index.ts]
            Stores[stores/]
        end
        
        subgraph "Views"
            Home[HomeView.vue]
            Team[TeamView.vue]
            Fixtures[FixturesView.vue]
            Standings[StandingsView.vue]
            Profile[ProfileView.vue]
            Auth[Auth Views]
        end
        
        subgraph "Components"
            TeamComponents[Team/]
            HomeComponents[Home/]
            Reusables[reusables/]
        end
        
        subgraph "State Management"
            AuthStore[auth.ts]
            FantasyStore[fantasy.ts] 
            KPLStore[kpl.ts]
        end
    end
```

## Data Model

### Core Entities

```{mermaid}
erDiagram
    User ||--|| Profile : has
    User ||--o{ FantasyTeam : creates
    
    FantasyTeam ||--o{ FantasyPlayer : contains
    FantasyPlayer }o--|| Player : references
    
    Team ||--o{ Player : employs
    Team ||--o{ Fixture : participates
    
    Gameweek ||--o{ Fixture : contains
    Gameweek ||--o{ PlayerPerformance : tracks
    
    Player ||--o{ PlayerPerformance : has
    FantasyPlayer ||--o{ PlayerPerformance : generates
```

### Entity Details

#### User Management
- **User**: Extended Django user model with email authentication
- **Profile**: User preferences, stats, and social features

#### KPL Data  
- **Team**: Kenyan Premier League teams with logos and jerseys
- **Player**: Player information, positions, and current market values
- **Fixture**: Match schedules, results, and status
- **Gameweek**: Weekly periods for organizing fixtures

#### Fantasy Game
- **FantasyTeam**: User's fantasy team with budget and formation
- **FantasyPlayer**: Players selected in fantasy teams
- **PlayerPerformance**: Points and statistics per gameweek

## Data Flow

### User Registration & Authentication

```{mermaid}
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant DB
    participant Email
    
    User->>Frontend: Register
    Frontend->>API: POST /api/v1/auth/users/
    API->>DB: Create user (inactive)
    API->>Email: Send activation email
    API-->>Frontend: Success response
    User->>Email: Click activation link
    Email->>API: GET /activate/{uid}/{token}
    API->>DB: Activate user
    API-->>Frontend: Redirect to login
```

### KPL Data Synchronization

```{mermaid}
sequenceDiagram
    participant CeleryBeat
    participant Worker
    participant KPL_API
    participant DB
    participant WebScraper
    
    CeleryBeat->>Worker: Trigger fixtures update (daily)
    Worker->>WebScraper: Scrape KPL website
    WebScraper->>KPL_API: Fetch latest data
    KPL_API-->>Worker: Return fixture data
    Worker->>DB: Update fixtures, teams, players
    Worker->>DB: Update gameweek status
```

### Fantasy Team Management

```{mermaid}
sequenceDiagram
    participant User
    participant Frontend  
    participant API
    participant DB
    participant Cache
    
    User->>Frontend: Select players
    Frontend->>API: POST /api/v1/fantasy/teams/
    API->>DB: Validate budget & rules
    API->>DB: Create fantasy team
    API->>Cache: Cache team data
    API-->>Frontend: Return team info
    Frontend-->>User: Show updated team
```

## Background Tasks

The system uses Celery for asynchronous task processing:

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Purpose |
|------|----------|---------|
| `get_kpl_table` | Daily | Update league standings |
| `get_kpl_fixtures` | Every 2 days | Sync fixture data |
| `update_active_gameweek` | Daily | Update current gameweek |

### Task Queue Architecture

```{mermaid}
graph LR
    Beat[Celery Beat] --> Queue[Redis Queue]
    Queue --> Worker1[Worker 1]
    Queue --> Worker2[Worker 2]
    Queue --> WorkerN[Worker N]
    
    Worker1 --> KPL[KPL APIs]
    Worker2 --> DB[(Database)]
    WorkerN --> Email[Email Service]
    
    Flower[Flower Monitor] --> Queue
```

## Security Architecture

### Authentication & Authorization

```{mermaid}
graph TD
    subgraph "Auth Flow"
        Login[User Login] --> JWT[JWT Token]
        JWT --> Access[Access Token]
        JWT --> Refresh[Refresh Token]
    end
    
    subgraph "API Protection"
        Request[API Request] --> Header[Auth Header]
        Header --> Validate[Validate JWT]
        Validate --> Endpoint[Protected Endpoint]
    end
    
    subgraph "Permissions"
        User[User] --> Own[Own Data]
        Staff[Staff] --> Admin[Admin Access]
        Public[Public] --> Read[Read Only]
    end
```

### Security Measures

- **JWT Authentication**: Stateless token-based auth with refresh mechanism
- **CSRF Protection**: Django CSRF middleware for form submissions  
- **CORS Configuration**: Controlled cross-origin access
- **Input Validation**: DRF serializers with comprehensive validation
- **SQL Injection Protection**: Django ORM with parameterized queries
- **Password Security**: Django's built-in password validation and hashing

## Performance & Scalability

### Caching Strategy

```{mermaid}
graph TD
    subgraph "Caching Layers"
        Browser[Browser Cache] --> CDN[CDN Cache]
        CDN --> Redis[Redis Cache]
        Redis --> DB[(Database)]
    end
    
    subgraph "Cache Types"
        Session[Session Data]
        API[API Responses]
        Static[Static Files]
        Tasks[Task Results]
    end
```

### Database Optimization

- **Indexing**: Strategic indexes on foreign keys and query fields
- **Query Optimization**: Select/prefetch related for N+1 prevention
- **Connection Pooling**: PostgreSQL connection management
- **Migrations**: Versioned schema changes with rollback support

## Deployment Architecture

### Container Orchestration

```{mermaid}
graph TB
    subgraph "Load Balancer"
        LB[nginx] --> API1[Django API 1]
        LB --> API2[Django API 2]
    end
    
    subgraph "Application Tier"
        API1 --> Worker1[Celery Worker 1]
        API2 --> Worker2[Celery Worker 2]
        Beat[Celery Beat]
    end
    
    subgraph "Data Tier"
        API1 --> Redis[Redis Cluster]
        API2 --> Redis
        Worker1 --> DB[(PostgreSQL)]
        Worker2 --> DB
    end
```

## Design Decisions

### Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Backend Framework** | Django + DRF | Rapid development, excellent ORM, mature ecosystem |
| **Database** | PostgreSQL | ACID compliance, JSON support, excellent Django integration |
| **Cache/Queue** | Redis | High performance, persistence options, Celery integration |
| **Frontend** | Vue.js 3 | Reactive, component-based, TypeScript support |
| **Styling** | Tailwind CSS | Utility-first, consistent design system |
| **Containerization** | Docker | Environment consistency, easy deployment |
| **Task Queue** | Celery | Mature, reliable, excellent Django integration |

### Architectural Patterns

- **API-First Design**: Clean separation between frontend and backend
- **Microservices-Ready**: App-based structure enables future service extraction
- **Event-Driven**: Celery tasks for decoupled background processing
- **CQRS Pattern**: Separate read/write operations for complex queries
- **Repository Pattern**: Service layer abstracts data access logic

## Future Considerations

### Scalability Roadmap

1. **Phase 1**: Horizontal scaling with multiple Django instances
2. **Phase 2**: Database read replicas and connection pooling
3. **Phase 3**: Microservices extraction for KPL and Fantasy domains
4. **Phase 4**: Event streaming with Kafka for real-time features

### Technical Debt

- **Monitoring**: Add comprehensive logging and metrics (Prometheus/Grafana)
- **Testing**: Increase test coverage, add integration tests
- **Documentation**: Auto-generate API docs with OpenAPI
- **CI/CD**: Implement automated testing and deployment pipelines

---

*This architecture supports the current requirements while maintaining flexibility for future growth and feature additions.*
