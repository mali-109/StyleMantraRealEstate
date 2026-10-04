import sqlite3


DATABASE = "database/stylemantra.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def init_db():

    connection = get_db()


    # =================================================
    # OWNERS TABLE
    # =================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS owners (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)


    # =================================================
    # PROPERTIES TABLE
    # =================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS properties (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            property_type TEXT NOT NULL,

            price TEXT NOT NULL,

            location TEXT NOT NULL,

            area TEXT,

            bedrooms INTEGER,

            bathrooms INTEGER,

            description TEXT,

            image TEXT,

            status TEXT DEFAULT 'Available'

        )
    """)


    # =================================================
    # ENQUIRIES TABLE
    # =================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            property_id INTEGER,

            name TEXT NOT NULL,

            email TEXT NOT NULL,

            phone TEXT,

            message TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (property_id)
            REFERENCES properties(id)

        )
    """)


    # =================================================
    # DEFAULT OWNER
    # =================================================

    owner = connection.execute("""
        SELECT *
        FROM owners
        WHERE email = ?
    """, (
        "owner@stylemantra.com",
    )).fetchone()


    if owner is None:

        connection.execute("""
            INSERT INTO owners
            (
                email,
                password
            )
            VALUES (?, ?)
        """, (
            "owner@stylemantra.com",
            "admin123"
        ))


    connection.commit()

    connection.close()