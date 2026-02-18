from backend.app.services.async_runner import run_async
from backend.app.services.db_service import update_stores_db


def update_db():
    """ Function to update the db with new stores data for all registered chains """
    run_async(update_stores_db)
