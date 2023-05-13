# Contributing Guideline

## Getting Started

1. Fork and clone repository then setup with [development container](https://containers.dev).

2. Migrate database.

   ```bash
   python manage.py migrate
   ```

3. Create admin user.

   ```bash
   python manage.py createsuperuser
   ```

4. Run development server at <http://localhost:8000/> and email server at <http://localhost:8025/>.

   ```bash
   python manage.py runserver
   ```

### Reset Development Server's Database

1. Remove all data.

   ```bash
   rm -r backend/media
   rm backend/db.sqlite3
   ```

2. Migrate database and restart server.

### Additional Resources

- <https://docs.github.com/en/get-started/quickstart/contributing-to-projects>
