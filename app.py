from blog import create_app, db
from blog.models import Post

import os

app = create_app()

with app.app_context():
    # We rely on Flask-Migrate / Alembic for schema changes.
    # Create tables if they don't exist for initial development convenience.
    db.create_all()

    # ensure uploads folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)


if __name__ == "__main__":
    app.run( debug=True)