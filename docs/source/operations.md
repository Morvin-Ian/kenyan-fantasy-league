# Operations Guide

This guide covers operational aspects of the Kenyan Fantasy League, including deployment, monitoring, maintenance, and troubleshooting.

## Deployment

### Production Environment Setup

#### Infrastructure Requirements

**Minimum Production Setup:**
- 2 CPU cores, 4GB RAM
- 50GB SSD storage
- Ubuntu 20.04 LTS
- Docker & Docker Compose

**Recommended Production Setup:**
- 4+ CPU cores, 8GB+ RAM
- 100GB+ SSD storage
- Load balancer (nginx/HAProxy)
- Managed PostgreSQL database
- Managed Redis cache
- CDN for static files

#### Production Deployment Steps

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Application Deployment**
   ```bash
   # Clone repository
   git clone https://github.com/your-org/kenyan-fantasy-league.git
   cd kenyan-fantasy-league
   
   # Setup production environment
   cp .env.example .env.production
   # Edit .env.production with production values
   
   # Deploy with production configuration
   docker-compose -f docker-compose.prod.yml up -d
   
   # Run database migrations
   docker-compose -f docker-compose.prod.yml exec api python manage.py migrate
   
   # Collect static files
   docker-compose -f docker-compose.prod.yml exec api python manage.py collectstatic --noinput
   
   # Create admin user
   docker-compose -f docker-compose.prod.yml exec api python manage.py createsuperuser
   ```

3. **SSL/HTTPS Setup**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Obtain SSL certificate
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   
   # Auto-renewal setup
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Environment Variables (Production)

Critical production environment variables:

```env
# Security
DEBUG=0
SECRET_KEY=very-long-random-string-minimum-50-characters
SIGNING_KEY=another-secure-random-string-for-jwt-tokens
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (use managed service)
PG_USER=production_user
PG_PASSWORD=very_secure_database_password
POSTGRES_DB=kfl_production
DB_HOST=your-managed-db-host.com
DB_PORT=5432

# Redis (use managed service)
REDIS_URL=redis://your-managed-redis-host:6379/0

# Email
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@mg.yourdomain.com
EMAIL_HOST_PASSWORD=your-mailgun-api-key
EMAIL_USE_TLS=1

# Storage (AWS S3)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=kfl-media-files
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

## Monitoring

### Application Monitoring

#### Health Checks

Set up health check endpoints:

```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection
import redis

def health_check(request):
    """Application health check endpoint."""
    status = {}
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'healthy'
    except Exception as e:
        status['database'] = f'unhealthy: {str(e)}'
    
    # Redis check
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        status['redis'] = 'healthy'
    except Exception as e:
        status['redis'] = f'unhealthy: {str(e)}'
    
    # Celery check
    from celery import current_app
    try:
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        status['celery'] = 'healthy' if stats else 'unhealthy'
    except Exception as e:
        status['celery'] = f'unhealthy: {str(e)}'
    
    return JsonResponse(status)
```

#### Monitoring Stack

**Recommended Monitoring Tools:**

1. **Application Performance**: Sentry for error tracking
2. **Infrastructure**: Prometheus + Grafana
3. **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
4. **Uptime**: UptimeRobot or Pingdom

**Prometheus Metrics:**
```python
# apps/core/middleware.py
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('django_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('django_request_duration_seconds', 'Request latency')

class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path
        ).inc()
        
        REQUEST_LATENCY.observe(time.time() - start_time)
        
        return response
```

### Logging Configuration

Production logging setup:

```python
# config/settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/kfl/application.log',
            'maxBytes': 50 * 1024 * 1024,  # 50MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.SentryHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'sentry'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['file', 'sentry'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

## Backup and Recovery

### Database Backup

#### Automated Backup Script

```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_NAME="kfl_production"
DB_USER="production_user"
DB_HOST="your-db-host.com"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/kfl_backup_$DATE.sql.gz

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/kfl_backup_$DATE.sql.gz s3://your-backup-bucket/database/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Database backup completed: kfl_backup_$DATE.sql.gz"
```

#### Automated Backup with Cron

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup_database.sh

# Weekly full backup at Sunday 1 AM
0 1 * * 0 /path/to/full_backup.sh
```

#### Database Recovery

```bash
# Restore from backup
gunzip -c kfl_backup_20241215_020000.sql.gz | psql -h $DB_HOST -U $DB_USER -d $DB_NAME

# Docker-based restore
docker-compose exec postgres-db psql -U postgres -d kfl_production < backup.sql
```

### Media Files Backup

```bash
#!/bin/bash
# backup_media.sh

DATE=$(date +%Y%m%d_%H%M%S)
MEDIA_DIR="/app/mediafiles"
BACKUP_DIR="/backups/media"

# Create backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $MEDIA_DIR .

# Upload to S3
aws s3 cp $BACKUP_DIR/media_backup_$DATE.tar.gz s3://your-backup-bucket/media/

# Cleanup old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## Performance Optimization

### Database Optimization

#### Query Optimization

```python
# Use select_related for foreign keys
players = Player.objects.select_related('team').all()

# Use prefetch_related for many-to-many or reverse foreign keys
teams = Team.objects.prefetch_related('players').all()

# Avoid N+1 queries in templates
fantasy_teams = FantasyTeam.objects.select_related('user').prefetch_related(
    'fantasyplayer_set__player__team'
)
```

#### Database Indexes

```python
# models.py
class Player(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_index=True)
    position = models.CharField(max_length=50, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['team', 'position']),
            models.Index(fields=['name']),
        ]
```

#### Connection Pooling

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('PG_USER'),
        'PASSWORD': os.getenv('PG_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,  # Connection pooling
        'OPTIONS': {
            'MAX_CONNS': 20,
        },
    }
}
```

### Caching Strategy

#### Redis Caching

```python
# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        }
    }
}

# Cache usage example
from django.core.cache import cache

def get_kpl_standings():
    cache_key = 'kpl_standings'
    standings = cache.get(cache_key)
    
    if standings is None:
        standings = Standing.objects.select_related('team').order_by('position')
        cache.set(cache_key, standings, 3600)  # Cache for 1 hour
    
    return standings
```

#### View Caching

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60 * 15), name='list')  # 15 minutes
class TeamViewSet(ReadOnlyModelViewSet):
    queryset = Team.objects.filter(is_relegated=False)
    serializer_class = TeamSerializer
```

## Security

### Security Checklist

#### Production Security

- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] Secure secret keys (50+ characters)
- [ ] HTTPS enabled with valid SSL certificates
- [ ] Secure headers configured
- [ ] Database connections encrypted
- [ ] Regular security updates applied
- [ ] Access logs monitored
- [ ] Rate limiting implemented
- [ ] Input validation enforced
- [ ] CORS properly configured

#### Security Headers

```python
# settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

### Rate Limiting

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/min',
    }
}

# Custom throttle for login
class LoginRateThrottle(UserRateThrottle):
    scope = 'login'
```

## Maintenance

### Regular Maintenance Tasks

#### Daily Tasks

```bash
#!/bin/bash
# daily_maintenance.sh

# Cleanup old logs
find /var/log/kfl -name "*.log" -mtime +30 -delete

# Clear expired sessions
docker-compose exec api python manage.py clearsessions

# Update KPL data
docker-compose exec api python manage.py shell -c "
from apps.kpl.tasks.fixtures import get_kpl_fixtures
from apps.kpl.tasks.standings import get_kpl_table
get_kpl_fixtures.delay()
get_kpl_table.delay()
"

# Check disk space
df -h | grep -E "(Filesystem|/dev/)"
```

#### Weekly Tasks

```bash
#!/bin/bash
# weekly_maintenance.sh

# Database maintenance
docker-compose exec postgres-db psql -U postgres -d kfl_production -c "
VACUUM ANALYZE;
REINDEX DATABASE kfl_production;
"

# Docker cleanup
docker system prune -f
docker volume prune -f

# Security updates
sudo apt update && sudo apt upgrade -y
```

#### Monthly Tasks

```bash
#!/bin/bash
# monthly_maintenance.sh

# Full database backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > monthly_backup.sql

# Log rotation
logrotate /etc/logrotate.d/kfl

# Certificate renewal check
sudo certbot renew --dry-run

# Performance review
docker-compose exec api python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT * FROM pg_stat_user_tables;')
    print(cursor.fetchall())
"
```

## Troubleshooting

### Common Production Issues

#### High CPU Usage

```bash
# Check processes
top -p $(pgrep -d',' -f 'python|celery')

# Django debug toolbar for development
pip install django-debug-toolbar

# Profile slow queries
# Add to settings/production.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

#### Memory Issues

```bash
# Check memory usage
free -h
docker stats

# Django memory profiling
pip install memory-profiler
# Add @profile decorator to functions
python -m memory_profiler manage.py shell
```

#### Database Connection Issues

```bash
# Check active connections
docker-compose exec postgres-db psql -U postgres -c "
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';
"

# Check connection limits
docker-compose exec postgres-db psql -U postgres -c "
SHOW max_connections;
"

# Kill long-running queries
docker-compose exec postgres-db psql -U postgres -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
AND state_change < now() - interval '5 minutes';
"
```

#### Celery Task Issues

```bash
# Check worker status
docker-compose exec worker celery -A config inspect active

# Check queue status
docker-compose exec worker celery -A config inspect reserved

# Purge failed tasks
docker-compose exec worker celery -A config purge

# Monitor tasks with Flower
docker-compose logs flower
```

### Emergency Procedures

#### Service Recovery

```bash
#!/bin/bash
# emergency_recovery.sh

echo "Starting emergency recovery..."

# Stop all services
docker-compose down

# Check disk space
df -h

# Clear logs if disk full
if [ $(df / | tail -1 | awk '{print $5}' | sed 's/%//') -gt 90 ]; then
    find /var/log -name "*.log" -mtime +1 -delete
    docker system prune -f
fi

# Start essential services only
docker-compose up -d postgres-db redis
sleep 10

# Start application
docker-compose up -d api

# Verify health
curl -f http://localhost:8000/health/ || echo "Health check failed"

echo "Emergency recovery completed"
```

#### Database Recovery

```bash
# Emergency database recovery
docker-compose down
docker volume create postgres_data_backup
docker run --rm -v postgres_data:/from -v postgres_data_backup:/to alpine ash -c "cd /from ; cp -av . /to"

# Restore from latest backup
gunzip -c latest_backup.sql.gz | docker-compose exec -T postgres-db psql -U postgres -d kfl_production
```

## Monitoring Dashboards

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "KFL Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(django_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, django_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "singlestat",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends{datname=\"kfl_production\"}"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

```yaml
# prometheus_alerts.yml
groups:
  - name: kfl_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(django_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: DatabaseConnectionHigh
        expr: pg_stat_database_numbackends > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Database connection count is high"
          
      - alert: DiskSpaceHigh
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.9
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Disk space usage above 90%"
```

---

*This operations guide provides the foundation for running KFL in production. Adapt the procedures to your specific infrastructure and requirements.*

