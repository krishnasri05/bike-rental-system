# Bike Rental System (Flask + SQLite)

This is the Flask/SQLite conversion of the original PHP project.

## Run

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start app:
   - `python app.py`
4. Open:
   - `http://127.0.0.1:5000`

## Important routes

- `/` home
- `/main` landing page with available bikes
- `/register`, `/login`, `/logout`
- `/admin/dashboard`
- `/client/dashboard`
- `/init-db` (optional manual DB initialization)

## Default admin

- Email: `admin@bikerental.com`
- Password: `admin123`

## Notes

- Database file: `bike_rental.db`
- Bike uploads: `static/uploads/bikes`
- License uploads: `static/uploads/licenses`
