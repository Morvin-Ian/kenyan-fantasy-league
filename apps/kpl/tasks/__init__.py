from .fixtures import get_kpl_fixtures
from .scorers import scrape_top_scorers
from .standings import get_kpl_table

# Imported so Celery registers the tasks when the package is loaded; listed
# here so they read as deliberate re-exports rather than unused imports.
__all__ = ["get_kpl_fixtures", "scrape_top_scorers", "get_kpl_table"]
