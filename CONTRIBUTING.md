# Contributing Guideline

## Getting Started

1. Fork and clone repository.

2. Setup and activate virtual environment with [`virtualenv`](https://virtualenv.pypa.io/en/latest/).

   ```bash
   python -m virtualenv venv
   source venv/bin/activate
   pip install -r backend/requirements/dev.txt
   ```

   In windows, change `source venv/bin/activate` to `venv/Scripts/activate`

3. Migrate database.

   ```bash
   python manage.py migrate
   ```

4. Create admin user.

   ```bash
   python manage.py createsuperuser
   ```

5. Setup and run [MailHog](https://github.com/mailhog/MailHog).

6. Run development server at <http://localhost:8000/>.

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
