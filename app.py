from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bike_rental.db"
UPLOAD_BIKES = BASE_DIR / "static" / "uploads" / "bikes"
UPLOAD_LICENSES = BASE_DIR / "static" / "uploads" / "licenses"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "bike-rental-dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    UPLOAD_BIKES.mkdir(parents=True, exist_ok=True)
    UPLOAD_LICENSES.mkdir(parents=True, exist_ok=True)

    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            profile_image TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            last_login TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            license_number TEXT,
            license_proof_path TEXT,
            profile_completed INTEGER NOT NULL DEFAULT 0,
            license_verification_status TEXT NOT NULL DEFAULT 'pending',
            license_verified_at TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bikes (
            bike_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            model TEXT,
            type TEXT,
            bike_condition TEXT NOT NULL DEFAULT 'good',
            status TEXT NOT NULL DEFAULT 'available',
            price_per_hour REAL NOT NULL,
            image_path TEXT,
            description TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS rentals (
            rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            bike_id INTEGER NOT NULL,
            rental_start TEXT NOT NULL,
            rental_end TEXT NOT NULL,
            total_hours INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            payment_status TEXT NOT NULL DEFAULT 'pending',
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
            FOREIGN KEY (bike_id) REFERENCES bikes(bike_id) ON DELETE RESTRICT
        );
        """
    )
    
    # Clear bikes if user wants a full reset logic check inside the db
    # We will just delete all old bikes and rentals to accomplish the 'clear the db' request completely
    db.execute("DELETE FROM rentals")
    db.execute("DELETE FROM bikes")

    admin = db.execute("SELECT admin_id FROM admins WHERE email = ?", ("admin@bikerental.com",)).fetchone()
    if not admin:
        db.execute(
            """
            INSERT INTO admins (username, email, password, full_name, phone, status)
            VALUES (?, ?, ?, ?, ?, 'active')
            """,
            (
                "admin",
                "admin@bikerental.com",
                generate_password_hash("admin123"),
                "Admin User",
                "1234567890",
            ),
        )

    client = db.execute("SELECT client_id FROM clients WHERE email = ?", ("client@bikerental.com",)).fetchone()
    if not client:
        db.execute(
            """
            INSERT INTO clients (
                username, email, password, full_name, phone, address,
                license_number, license_proof_path, profile_completed,
                license_verification_status, license_verified_at, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'verified', CURRENT_TIMESTAMP, 'active')
            """,
            (
                "clientdemo",
                "client@bikerental.com",
                generate_password_hash("client123"),
                "Client Demo",
                "9876543210",
                "Visakhapatnam",
                "MH1420110012345",
                "demo_license.png",
            ),
        )

    bikes_count = db.execute("SELECT COUNT(*) FROM bikes").fetchone()[0]
    if bikes_count == 0:
        demo_bikes = [
            ("AeroBlade V9", "Ducati", "V9-Sport", "road", 35.0, "Futuristic luxury sport motorcycle built for performance and speed.", "luxury_sport.png", "available"),
            ("TerraVolt X", "Specialized", "TV-X", "mountain", 25.0, "Premium electric mountain bike with unparalleled trail capabilities.", "mountain_electric.png", "available"),
            ("Neon Glide", "Yamaha", "Neo-C01", "city", 18.0, "High-tech neo-noir cyberpunk city commuter for a smooth urban ride.", "cyberpunk.png", "available"),
        ]
        db.executemany(
            """
            INSERT INTO bikes (name, brand, model, type, price_per_hour, description, image_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            demo_bikes,
        )

    rentals_count = db.execute("SELECT COUNT(*) FROM rentals").fetchone()[0]
    if rentals_count == 0:
        demo_client = db.execute("SELECT client_id FROM clients WHERE email = ?", ("client@bikerental.com",)).fetchone()
        demo_bike = db.execute("SELECT bike_id FROM bikes ORDER BY bike_id LIMIT 1").fetchone()

        if demo_client and demo_bike:
            db.execute(
                """
                INSERT INTO rentals (
                    client_id, bike_id, rental_start, rental_end, total_hours,
                    total_cost, status, payment_status, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, 'completed', 'paid', ?)
                """,
                (
                    demo_client["client_id"],
                    demo_bike["bike_id"],
                    "2026-03-15 09:00:00",
                    "2026-03-15 13:00:00",
                    4,
                    20.0,
                    "Demo completed rental",
                ),
            )

    db.commit()


def login_required(role: str | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not session.get("user_id") or not session.get("user_type"):
                return redirect(url_for("login"))
            if role and session.get("user_type") != role:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def format_currency(amount: float | int | None) -> str:
    value = amount or 0
    return f"${value:,.2f}"


def format_datetime(dt_str: str | None) -> str:
    if not dt_str:
        return "N/A"
    try:
        parsed = datetime.fromisoformat(dt_str.replace(" ", "T"))
    except ValueError:
        return dt_str
    return parsed.strftime("%b %d, %Y %I:%M %p")


def badge_class(status: str | None) -> str:
    mapping = {
        "active": "bg-success",
        "available": "bg-success",
        "pending": "bg-warning text-dark",
        "completed": "bg-info",
        "cancelled": "bg-danger",
        "failed": "bg-danger",
        "paid": "bg-success",
        "inactive": "bg-secondary",
        "suspended": "bg-danger",
        "rented": "bg-primary",
    }
    return mapping.get((status or "").lower(), "bg-secondary")


def resolve_image_path(image_path: str | None) -> str:
    if not image_path:
        return "https://via.placeholder.com/640x360?text=Bike"
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path
    if "/" in image_path or "\\" in image_path:
        return f"/{image_path.lstrip('/')}"
    return url_for("static", filename=f"uploads/bikes/{image_path}")


@app.context_processor
def inject_helpers() -> dict[str, Any]:
    return {
        "format_currency": format_currency,
        "format_datetime": format_datetime,
        "badge_class": badge_class,
        "resolve_image_path": resolve_image_path,
    }


@app.route("/init-db")
def init_db_route():
    init_db()
    flash("Database initialized successfully. Admin: admin@bikerental.com / admin123", "success")
    return redirect(url_for("login", type="admin"))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/main")
def main_page():
    bikes = get_db().execute(
        "SELECT * FROM bikes WHERE status = 'available' ORDER BY created_at DESC LIMIT 6"
    ).fetchall()
    return render_template("main.html", bikes=bikes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("admin_dashboard" if session.get("user_type") == "admin" else "client_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        license_number = re.sub(r"[^A-Z0-9]", "", request.form.get("license_number", "").upper())

        if not username or not email or not password or not full_name:
            flash("Please fill in all required fields.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        else:
            db = get_db()
            exists = db.execute(
                "SELECT client_id FROM clients WHERE username = ? OR email = ?", (username, email)
            ).fetchone()
            if exists:
                flash("Username or email already exists.", "danger")
            else:
                db.execute(
                    """
                    INSERT INTO clients (username, email, password, full_name, phone, address, license_number, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
                    """,
                    (username, email, generate_password_hash(password), full_name, phone, address, license_number),
                )
                db.commit()
                flash("Registration successful. You can now log in.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("admin_dashboard" if session.get("user_type") == "admin" else "client_dashboard"))

    login_type = request.args.get("type", "client")

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        login_type = request.form.get("login_type", "client")
        db = get_db()

        if login_type == "admin":
            user = db.execute(
                "SELECT * FROM admins WHERE email = ? AND status = 'active'", (email,)
            ).fetchone()
            if user and check_password_hash(user["password"], password):
                session.clear()
                session.update(
                    {
                        "user_id": user["admin_id"],
                        "user_type": "admin",
                        "username": user["username"],
                        "full_name": user["full_name"],
                        "email": user["email"],
                    }
                )
                db.execute("UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE admin_id = ?", (user["admin_id"],))
                db.commit()
                return redirect(url_for("admin_dashboard"))
            flash("Invalid admin credentials or inactive account.", "danger")
        else:
            user = db.execute(
                "SELECT * FROM clients WHERE email = ? AND status = 'active'", (email,)
            ).fetchone()
            if user and check_password_hash(user["password"], password):
                session.clear()
                session.update(
                    {
                        "user_id": user["client_id"],
                        "user_type": "client",
                        "username": user["username"],
                        "full_name": user["full_name"],
                        "email": user["email"],
                    }
                )
                return redirect(url_for("client_dashboard"))
            flash("Invalid client credentials or inactive account.", "danger")

    return render_template("login.html", login_type=login_type)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    db = get_db()
    bikes_count = db.execute("SELECT COUNT(*) FROM bikes").fetchone()[0]
    clients_count = db.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    active_rentals = db.execute("SELECT COUNT(*) FROM rentals WHERE status = 'active'").fetchone()[0]
    pending_rentals = db.execute("SELECT COUNT(*) FROM rentals WHERE status = 'pending'").fetchone()[0]
    total_revenue = db.execute(
        "SELECT COALESCE(SUM(total_cost),0) FROM rentals WHERE status='completed' AND payment_status='paid'"
    ).fetchone()[0]

    recent_rentals = db.execute(
        """
        SELECT r.*, c.full_name, b.name AS bike_name
        FROM rentals r
        JOIN clients c ON c.client_id = r.client_id
        JOIN bikes b ON b.bike_id = r.bike_id
        ORDER BY r.created_at DESC
        LIMIT 8
        """
    ).fetchall()

    return render_template(
        "admin/dashboard.html",
        bikes_count=bikes_count,
        clients_count=clients_count,
        active_rentals=active_rentals,
        pending_rentals=pending_rentals,
        total_revenue=total_revenue,
        recent_rentals=recent_rentals,
    )


@app.route("/admin/bikes")
@login_required("admin")
def admin_bikes():
    search = request.args.get("search", "").strip()
    db = get_db()
    if search:
        query = """
            SELECT * FROM bikes
            WHERE name LIKE ? OR brand LIKE ? OR model LIKE ?
            ORDER BY created_at DESC
        """
        term = f"%{search}%"
        bikes = db.execute(query, (term, term, term)).fetchall()
    else:
        bikes = db.execute("SELECT * FROM bikes ORDER BY created_at DESC").fetchall()
    return render_template("admin/bikes.html", bikes=bikes, search=search)


@app.route("/admin/bikes/add", methods=["GET", "POST"])
@login_required("admin")
def admin_add_bike():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        bike_type = request.form.get("type", "").strip()
        price_per_hour = float(request.form.get("price_per_hour", 0) or 0)
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "available").strip()

        image_name = ""
        image = request.files.get("image_path")
        if image and image.filename:
            image_name = f"{datetime.utcnow().timestamp():.0f}_{secure_filename(image.filename)}"
            image.save(UPLOAD_BIKES / image_name)

        db = get_db()
        db.execute(
            """
            INSERT INTO bikes (name, brand, model, type, price_per_hour, description, image_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, brand, model, bike_type, price_per_hour, description, image_name, status),
        )
        db.commit()
        flash("Bike added successfully.", "success")
        return redirect(url_for("admin_bikes"))

    return render_template("admin/bike_form.html", bike=None)


@app.route("/admin/bikes/edit/<int:bike_id>", methods=["GET", "POST"])
@login_required("admin")
def admin_edit_bike(bike_id: int):
    db = get_db()
    bike = db.execute("SELECT * FROM bikes WHERE bike_id = ?", (bike_id,)).fetchone()
    if not bike:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        brand = request.form.get("brand", "").strip()
        model = request.form.get("model", "").strip()
        bike_type = request.form.get("type", "").strip()
        price_per_hour = float(request.form.get("price_per_hour", 0) or 0)
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "available").strip()

        image_name = bike["image_path"]
        image = request.files.get("image_path")
        if image and image.filename:
            image_name = f"{datetime.utcnow().timestamp():.0f}_{secure_filename(image.filename)}"
            image.save(UPLOAD_BIKES / image_name)

        db.execute(
            """
            UPDATE bikes
            SET name=?, brand=?, model=?, type=?, price_per_hour=?, description=?, image_path=?, status=?, updated_at=CURRENT_TIMESTAMP
            WHERE bike_id=?
            """,
            (name, brand, model, bike_type, price_per_hour, description, image_name, status, bike_id),
        )
        db.commit()
        flash("Bike updated successfully.", "success")
        return redirect(url_for("admin_bikes"))

    return render_template("admin/bike_form.html", bike=bike)


@app.post("/admin/bikes/delete/<int:bike_id>")
@login_required("admin")
def admin_delete_bike(bike_id: int):
    db = get_db()
    db.execute("DELETE FROM bikes WHERE bike_id = ?", (bike_id,))
    db.commit()
    flash("Bike deleted successfully.", "success")
    return redirect(url_for("admin_bikes"))


@app.route("/admin/rentals", methods=["GET", "POST"])
@login_required("admin")
def admin_rentals():
    db = get_db()

    if request.method == "POST":
        action = request.form.get("action")
        rental_id = int(request.form.get("rental_id", 0) or 0)
        if action == "status":
            new_status = request.form.get("status", "pending")
            db.execute(
                "UPDATE rentals SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE rental_id = ?",
                (new_status, rental_id),
            )
            flash("Rental status updated.", "success")
        elif action == "payment":
            payment_status = request.form.get("payment_status", "pending")
            db.execute(
                "UPDATE rentals SET payment_status = ?, updated_at = CURRENT_TIMESTAMP WHERE rental_id = ?",
                (payment_status, rental_id),
            )
            flash("Payment status updated.", "success")
        db.commit()
        return redirect(url_for("admin_rentals"))

    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    payment_filter = request.args.get("payment", "").strip()

    query = """
        SELECT r.*, c.full_name, c.email, b.name AS bike_name, b.brand, b.model
        FROM rentals r
        JOIN clients c ON c.client_id = r.client_id
        JOIN bikes b ON b.bike_id = r.bike_id
        WHERE 1=1
    """
    params: list[Any] = []

    if search:
        query += " AND (c.full_name LIKE ? OR c.email LIKE ? OR b.name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if status_filter:
        query += " AND r.status = ?"
        params.append(status_filter)
    if payment_filter:
        query += " AND r.payment_status = ?"
        params.append(payment_filter)

    query += " ORDER BY r.created_at DESC"
    rentals = db.execute(query, params).fetchall()

    return render_template(
        "admin/rentals.html",
        rentals=rentals,
        search=search,
        status_filter=status_filter,
        payment_filter=payment_filter,
    )


@app.route("/admin/rentals/<int:rental_id>")
@login_required("admin")
def admin_rental_view(rental_id: int):
    rental = get_db().execute(
        """
        SELECT r.*, c.full_name, c.email, c.phone, b.name AS bike_name, b.brand, b.model, b.type
        FROM rentals r
        JOIN clients c ON c.client_id = r.client_id
        JOIN bikes b ON b.bike_id = r.bike_id
        WHERE r.rental_id = ?
        """,
        (rental_id,),
    ).fetchone()
    if not rental:
        abort(404)
    return render_template("admin/rental_view.html", rental=rental)


@app.route("/admin/profile")
@login_required("admin")
def admin_profile():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = "SELECT * FROM admins WHERE 1=1"
    params: list[Any] = []

    if search:
        query += " AND (username LIKE ? OR email LIKE ? OR full_name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC"

    admins = get_db().execute(query, params).fetchall()
    return render_template("admin/profile.html", admins=admins, search=search, status_filter=status)


@app.post("/admin/profile/toggle/<int:admin_id>")
@login_required("admin")
def admin_toggle_status(admin_id: int):
    if admin_id == session["user_id"]:
        flash("You cannot change your own status.", "danger")
        return redirect(url_for("admin_profile"))

    db = get_db()
    admin = db.execute("SELECT status FROM admins WHERE admin_id = ?", (admin_id,)).fetchone()
    if admin:
        next_status = "inactive" if admin["status"] == "active" else "active"
        db.execute("UPDATE admins SET status = ? WHERE admin_id = ?", (next_status, admin_id))
        db.commit()
        flash("Admin status updated.", "success")
    return redirect(url_for("admin_profile"))


@app.post("/admin/profile/delete/<int:admin_id>")
@login_required("admin")
def admin_delete_profile(admin_id: int):
    if admin_id == session["user_id"]:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin_profile"))

    db = get_db()
    db.execute("DELETE FROM admins WHERE admin_id = ?", (admin_id,))
    db.commit()
    flash("Admin deleted.", "success")
    return redirect(url_for("admin_profile"))


@app.route("/admin/profile/edit/<int:admin_id>", methods=["GET", "POST"])
@login_required("admin")
def admin_edit_profile(admin_id: int):
    db = get_db()
    admin = db.execute("SELECT * FROM admins WHERE admin_id = ?", (admin_id,)).fetchone()
    if not admin:
        abort(404)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        status = request.form.get("status", "active")

        exists = db.execute(
            "SELECT admin_id FROM admins WHERE (username = ? OR email = ?) AND admin_id != ?",
            (username, email, admin_id),
        ).fetchone()
        if exists:
            flash("Username or email already exists.", "danger")
        else:
            db.execute(
                "UPDATE admins SET username=?, email=?, full_name=?, status=? WHERE admin_id=?",
                (username, email, full_name, status, admin_id),
            )
            db.commit()
            flash("Admin updated successfully.", "success")
            return redirect(url_for("admin_profile"))

    return render_template("admin/edit_admin.html", admin=admin)


@app.route("/client/dashboard")
@login_required("client")
def client_dashboard():
    client_id = session["user_id"]
    db = get_db()

    rentals_count = db.execute("SELECT COUNT(*) FROM rentals WHERE client_id = ?", (client_id,)).fetchone()[0]
    active_count = db.execute(
        "SELECT COUNT(*) FROM rentals WHERE client_id = ? AND status = 'active'", (client_id,)
    ).fetchone()[0]
    spent_amount = db.execute(
        "SELECT COALESCE(SUM(total_cost),0) FROM rentals WHERE client_id = ? AND payment_status = 'paid'",
        (client_id,),
    ).fetchone()[0]

    recent_rentals = db.execute(
        """
        SELECT r.*, b.name AS bike_name, b.brand, b.type
        FROM rentals r
        JOIN bikes b ON b.bike_id = r.bike_id
        WHERE r.client_id = ?
        ORDER BY r.created_at DESC
        LIMIT 5
        """,
        (client_id,),
    ).fetchall()

    available_bikes = db.execute("SELECT COUNT(*) FROM bikes WHERE status = 'available'").fetchone()[0]

    return render_template(
        "client/dashboard.html",
        rentals_count=rentals_count,
        active_count=active_count,
        spent_amount=spent_amount,
        recent_rentals=recent_rentals,
        available_bikes=available_bikes,
    )


@app.route("/client/profile", methods=["GET", "POST"])
@login_required("client")
def client_profile():
    client_id = session["user_id"]
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,)).fetchone()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        license_number = re.sub(r"[^A-Z0-9]", "", request.form.get("license_number", "").upper())
        license_proof = client["license_proof_path"]

        file = request.files.get("license_proof")
        if file and file.filename:
            filename = f"license_{client_id}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
            file.save(UPLOAD_LICENSES / filename)
            license_proof = filename

        is_complete = int(bool(full_name and phone and address and license_number and license_proof))
        verification_status = "verified" if is_complete else "pending"
        verified_at = datetime.utcnow().isoformat(sep=" ") if verification_status == "verified" else None

        db.execute(
            """
            UPDATE clients
            SET full_name=?, phone=?, address=?, license_number=?, license_proof_path=?,
                profile_completed=?, license_verification_status=?, license_verified_at=?, updated_at=CURRENT_TIMESTAMP
            WHERE client_id=?
            """,
            (
                full_name,
                phone,
                address,
                license_number,
                license_proof,
                is_complete,
                verification_status,
                verified_at,
                client_id,
            ),
        )
        db.commit()
        session["full_name"] = full_name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("client_profile"))

    total_rentals = db.execute("SELECT COUNT(*) FROM rentals WHERE client_id = ?", (client_id,)).fetchone()[0]
    active_rentals = db.execute(
        "SELECT COUNT(*) FROM rentals WHERE client_id = ? AND status = 'active'", (client_id,)
    ).fetchone()[0]

    return render_template(
        "client/profile.html",
        client=client,
        total_rentals=total_rentals,
        active_rentals=active_rentals,
    )


@app.route("/client/bikes")
@login_required("client")
def client_bikes():
    bike_type = request.args.get("type", "").strip()
    search = request.args.get("search", "").strip()

    query = "SELECT * FROM bikes WHERE status = 'available'"
    params: list[Any] = []

    if bike_type:
        query += " AND type = ?"
        params.append(bike_type)
    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR model LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY created_at DESC"
    db = get_db()
    bikes = db.execute(query, params).fetchall()
    types = db.execute("SELECT DISTINCT type FROM bikes WHERE status='available' AND type IS NOT NULL AND type != ''").fetchall()

    return render_template("client/bikes.html", bikes=bikes, types=types, bike_type=bike_type, search=search)


@app.route("/client/rentals/book/<int:bike_id>", methods=["GET", "POST"])
@login_required("client")
def client_book_bike(bike_id: int):
    client_id = session["user_id"]
    db = get_db()

    profile = db.execute(
        "SELECT full_name, phone, address, license_number, license_proof_path, license_verification_status FROM clients WHERE client_id = ?",
        (client_id,),
    ).fetchone()

    profile_ready = all(
        [
            profile["full_name"],
            profile["phone"],
            profile["address"],
            profile["license_number"],
            profile["license_proof_path"],
        ]
    )
    if not profile_ready:
        flash("Complete your profile and upload license proof before booking.", "danger")
        return redirect(url_for("client_profile"))
    if profile["license_verification_status"] != "verified":
        flash("Your license is pending verification.", "danger")
        return redirect(url_for("client_profile"))

    bike = db.execute("SELECT * FROM bikes WHERE bike_id = ? AND status = 'available'", (bike_id,)).fetchone()
    if not bike:
        flash("Bike not available.", "danger")
        return redirect(url_for("client_bikes"))

    if request.method == "POST":
        rental_start = request.form.get("rental_start", "")
        rental_end = request.form.get("rental_end", "")

        try:
            start_dt = datetime.fromisoformat(rental_start)
            end_dt = datetime.fromisoformat(rental_end)
        except ValueError:
            flash("Invalid rental dates.", "danger")
            return render_template("client/book_bike.html", bike=bike)

        if start_dt >= end_dt:
            flash("Rental end must be after start.", "danger")
            return render_template("client/book_bike.html", bike=bike)

        total_hours = int((end_dt - start_dt).total_seconds() // 3600)
        if total_hours < 1:
            total_hours = 1
        total_cost = total_hours * float(bike["price_per_hour"])

        db.execute(
            """
            INSERT INTO rentals (client_id, bike_id, rental_start, rental_end, total_hours, total_cost, status, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', 'pending')
            """,
            (
                client_id,
                bike_id,
                start_dt.isoformat(sep=" "),
                end_dt.isoformat(sep=" "),
                total_hours,
                total_cost,
            ),
        )
        db.execute("UPDATE bikes SET status = 'rented', updated_at = CURRENT_TIMESTAMP WHERE bike_id = ?", (bike_id,))
        db.commit()

        flash(f"Bike booked successfully. Total: {format_currency(total_cost)}", "success")
        return redirect(url_for("client_rentals"))

    return render_template("client/book_bike.html", bike=bike)


@app.route("/client/rentals", methods=["GET", "POST"])
@login_required("client")
def client_rentals():
    client_id = session["user_id"]
    db = get_db()

    if request.method == "POST":
        rental_id = int(request.form.get("rental_id", 0) or 0)
        rental = db.execute(
            "SELECT payment_status FROM rentals WHERE rental_id = ? AND client_id = ?",
            (rental_id, client_id),
        ).fetchone()
        if rental and rental["payment_status"] in {"pending", "failed"}:
            db.execute(
                "UPDATE rentals SET payment_status = 'paid', updated_at = CURRENT_TIMESTAMP WHERE rental_id = ?",
                (rental_id,),
            )
            db.commit()
            flash("Payment completed successfully.", "success")
        else:
            flash("This rental is not eligible for payment.", "danger")
        return redirect(url_for("client_rentals"))

    rentals = db.execute(
        """
        SELECT r.*, b.name AS bike_name, b.brand, b.type, b.image_path
        FROM rentals r
        JOIN bikes b ON b.bike_id = r.bike_id
        WHERE r.client_id = ?
        ORDER BY r.created_at DESC
        """,
        (client_id,),
    ).fetchall()

    return render_template("client/rentals.html", rentals=rentals)


@app.route("/client/rentals/<int:rental_id>")
@login_required("client")
def client_rental_view(rental_id: int):
    rental = get_db().execute(
        """
        SELECT r.*, b.name AS bike_name, b.brand, b.type
        FROM rentals r
        JOIN bikes b ON b.bike_id = r.bike_id
        WHERE r.rental_id = ? AND r.client_id = ?
        """,
        (rental_id, session["user_id"]),
    ).fetchone()
    if not rental:
        abort(404)
    return render_template("client/rental_view.html", rental=rental)


@app.route("/client/rentals/<int:rental_id>/cancel", methods=["GET", "POST"])
@login_required("client")
def client_cancel_rental(rental_id: int):
    db = get_db()
    rental = db.execute(
        """
        SELECT r.*, b.name AS bike_name
        FROM rentals r
        JOIN bikes b ON b.bike_id = r.bike_id
        WHERE r.rental_id = ? AND r.client_id = ?
        """,
        (rental_id, session["user_id"]),
    ).fetchone()

    if not rental:
        abort(404)

    if rental["status"] != "pending":
        flash("Only pending rentals can be cancelled.", "danger")
        return redirect(url_for("client_rental_view", rental_id=rental_id))

    if request.method == "POST":
        db.execute(
            "UPDATE rentals SET status='cancelled', updated_at=CURRENT_TIMESTAMP WHERE rental_id = ?",
            (rental_id,),
        )
        db.execute("UPDATE bikes SET status='available', updated_at=CURRENT_TIMESTAMP WHERE bike_id = ?", (rental["bike_id"],))
        db.commit()
        flash("Rental cancelled successfully.", "success")
        return redirect(url_for("client_rentals"))

    return render_template("client/cancel_rental.html", rental=rental)


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
