from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import os
from dotenv import load_dotenv
from config import (
    SECRET_KEY,
    UPLOAD_FOLDER
)

from werkzeug.utils import secure_filename

from database import (
    get_db,
    init_db
)

load_dotenv()
app = Flask(__name__)
app.secret_key = SECRET_KEY


# =====================================================
# UPLOAD SETTINGS
# =====================================================

UPLOAD_FOLDER = "static/uploads"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():

    connection = get_db()

    search = request.args.get(
        "search",
        ""
    ).strip()

    property_type = request.args.get(
        "property_type",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()


    query = """
        SELECT *
        FROM properties
        WHERE 1=1
    """

    parameters = []


    # -------------------------
    # SEARCH BY TITLE OR LOCATION
    # -------------------------

    if search:

        query += """
            AND (
                title LIKE ?
                OR location LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value
        ])


    # -------------------------
    # FILTER BY PROPERTY TYPE
    # -------------------------

    if property_type:

        query += """
            AND property_type = ?
        """

        parameters.append(
            property_type
        )


    # -------------------------
    # FILTER BY STATUS
    # -------------------------

    if status:

        query += """
            AND status = ?
        """

        parameters.append(
            status
        )


    # -------------------------
    # SORT
    # -------------------------

    query += """
        ORDER BY id DESC
    """


    properties = connection.execute(
        query,
        parameters
    ).fetchall()


    connection.close()


    return render_template(
        "index.html",
        properties=properties,
        search=search,
        property_type=property_type,
        status=status
    )


# =====================================================
# PROPERTIES PAGE
# =====================================================

@app.route("/properties")
def properties():

    connection = get_db()

    search = request.args.get(
        "search",
        ""
    ).strip()

    property_type = request.args.get(
        "property_type",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()


    query = """
        SELECT *
        FROM properties
        WHERE 1=1
    """

    parameters = []


    if search:

        query += """
            AND (
                title LIKE ?
                OR location LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value
        ])


    if property_type:

        query += """
            AND property_type = ?
        """

        parameters.append(property_type)


    if status:

        query += """
            AND status = ?
        """

        parameters.append(status)


    query += """
        ORDER BY id DESC
    """


    properties = connection.execute(
        query,
        parameters
    ).fetchall()


    connection.close()


    return render_template(
        "properties.html",
        properties=properties,
        search=search,
        property_type=property_type,
        status=status
    )


# =====================================================
# ABOUT PAGE
# =====================================================

@app.route("/about")
def about():

    return redirect(
        url_for("home") + "#about"
    )


# =====================================================
# CONTACT
# =====================================================

@app.route("/contact")
def contact():

    return redirect(
        url_for("home") + "#contact"
    )


# =====================================================
# OWNER LOGIN
# =====================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        connection = get_db()

        owner = connection.execute("""
            SELECT *
            FROM owners
            WHERE email = ?
            AND password = ?
        """, (
            email,
            password
        )).fetchone()

        connection.close()


        if owner:
            session.clear()

            session["owner_id"] = owner["id"]

            return redirect(
                url_for("dashboard")
            )


        return render_template(
            "login.html",
            error="Invalid email or password"
        )


    return render_template(
        "login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =====================================================
# OWNER DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "owner_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    properties = connection.execute("""
        SELECT *
        FROM properties
        ORDER BY id DESC
    """).fetchall()


    enquiry_count = connection.execute("""
        SELECT COUNT(*)
        FROM enquiries
    """).fetchone()[0]


    connection.close()


    return render_template(
        "dashboard.html",
        properties=properties,
        enquiry_count=enquiry_count
    )


# =====================================================
# ADD PROPERTY
# =====================================================

@app.route(
    "/add-property",
    methods=["GET", "POST"]
)
def add_property():

    if "owner_id" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":


        # -------------------------
        # PROPERTY DETAILS
        # -------------------------

        title = request.form["title"]

        property_type = request.form[
            "property_type"
        ]

        price = request.form["price"]

        location = request.form["location"]

        area = request.form["area"]

        bedrooms = request.form["bedrooms"]

        bathrooms = request.form["bathrooms"]

        description = request.form[
            "description"
        ]


        # -------------------------
        # PROPERTY IMAGE
        # -------------------------

        image_file = request.files.get(
            "image"
        )

        image_path = ""


        if image_file and image_file.filename:

            if allowed_file(
                image_file.filename
            ):

                filename = secure_filename(
                    image_file.filename
                )


                name, extension = os.path.splitext(
                    filename
                )

                counter = 1

                final_filename = filename


                while os.path.exists(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        final_filename
                    )
                ):

                    final_filename = (
                        f"{name}_{counter}{extension}"
                    )

                    counter += 1


                image_file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        final_filename
                    )
                )


                image_path = (
                    "uploads/" +
                    final_filename
                )


        # -------------------------
        # SAVE PROPERTY
        # -------------------------

        connection = get_db()


        connection.execute("""
            INSERT INTO properties
            (
                title,
                property_type,
                price,
                location,
                area,
                bedrooms,
                bathrooms,
                description,
                image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            property_type,
            price,
            location,
            area,
            bedrooms,
            bathrooms,
            description,
            image_path
        ))


        connection.commit()

        connection.close()


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "add_property.html"
    )


# =====================================================
# PROPERTY DETAILS
# =====================================================

@app.route(
    "/property/<int:property_id>"
)
def property_details(property_id):

    connection = get_db()


    property_data = connection.execute("""
        SELECT *
        FROM properties
        WHERE id = ?
    """, (
        property_id,
    )).fetchone()


    connection.close()


    if property_data is None:

        return "Property not found", 404


    return render_template(
        "property_details.html",
        property=property_data
    )


# =====================================================
# EDIT PROPERTY
# =====================================================

@app.route(
    "/edit-property/<int:property_id>",
    methods=["GET", "POST"]
)
def edit_property(property_id):

    if "owner_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    property_data = connection.execute("""
        SELECT *
        FROM properties
        WHERE id = ?
    """, (
        property_id,
    )).fetchone()


    if property_data is None:

        connection.close()

        return "Property not found", 404


    if request.method == "POST":

        title = request.form["title"]

        property_type = request.form[
            "property_type"
        ]

        price = request.form["price"]

        location = request.form["location"]

        area = request.form["area"]

        bedrooms = request.form["bedrooms"]

        bathrooms = request.form["bathrooms"]

        description = request.form[
            "description"
        ]

        status = request.form["status"]


        # -------------------------
        # IMAGE
        # -------------------------

        image_file = request.files.get(
            "image"
        )

        image_path = property_data["image"]


        if image_file and image_file.filename:

            if allowed_file(
                image_file.filename
            ):

                filename = secure_filename(
                    image_file.filename
                )


                name, extension = os.path.splitext(
                    filename
                )

                counter = 1

                final_filename = filename


                while os.path.exists(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        final_filename
                    )
                ):

                    final_filename = (
                        f"{name}_{counter}{extension}"
                    )

                    counter += 1


                image_file.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        final_filename
                    )
                )


                image_path = (
                    "uploads/" +
                    final_filename
                )


        # -------------------------
        # UPDATE DATABASE
        # -------------------------

        connection.execute("""
            UPDATE properties

            SET
                title = ?,
                property_type = ?,
                price = ?,
                location = ?,
                area = ?,
                bedrooms = ?,
                bathrooms = ?,
                description = ?,
                image = ?,
                status = ?

            WHERE id = ?
        """, (
            title,
            property_type,
            price,
            location,
            area,
            bedrooms,
            bathrooms,
            description,
            image_path,
            status,
            property_id
        ))


        connection.commit()

        connection.close()


        return redirect(
            url_for("dashboard")
        )


    connection.close()


    return render_template(
        "edit_property.html",
        property=property_data
    )


# =====================================================
# DELETE PROPERTY
# =====================================================

@app.route(
    "/delete-property/<int:property_id>",
    methods=["POST"]
)
def delete_property(property_id):

    if "owner_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    property_data = connection.execute("""
        SELECT *
        FROM properties
        WHERE id = ?
    """, (
        property_id,
    )).fetchone()


    if property_data is None:

        connection.close()

        return "Property not found", 404


    connection.execute("""
        DELETE FROM properties
        WHERE id = ?
    """, (
        property_id,
    ))


    connection.commit()

    connection.close()


    # -------------------------
    # DELETE IMAGE FILE
    # -------------------------

    if property_data["image"]:

        image_file = os.path.join(
            "static",
            property_data["image"]
        )


        if os.path.exists(image_file):

            try:

                os.remove(image_file)

            except OSError:

                pass


    return redirect(
        url_for("dashboard")
    )


# =====================================================
# PROPERTY ENQUIRY
# =====================================================

@app.route(
    "/property/<int:property_id>/enquire",
    methods=["POST"]
)
def property_enquiry(property_id):


    # -------------------------
    # GET FORM DATA
    # -------------------------

    name = request.form["name"]

    email = request.form["email"]

    phone = request.form["phone"]

    message = request.form["message"]


    # -------------------------
    # CHECK PROPERTY
    # -------------------------

    connection = get_db()


    property_data = connection.execute("""
        SELECT *
        FROM properties
        WHERE id = ?
    """, (
        property_id,
    )).fetchone()


    if property_data is None:

        connection.close()

        return "Property not found", 404


    # -------------------------
    # SAVE ENQUIRY
    # -------------------------

    connection.execute("""
        INSERT INTO enquiries
        (
            property_id,
            name,
            email,
            phone,
            message
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        property_id,
        name,
        email,
        phone,
        message
    ))


    connection.commit()

    connection.close()


    # -------------------------
    # SUCCESS
    # -------------------------

    return redirect(
        url_for(
            "property_details",
            property_id=property_id
        )
    )


# =====================================================
# OWNER ENQUIRIES
# =====================================================

@app.route("/enquiries")
def enquiries():

    if "owner_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    enquiries = connection.execute("""
        SELECT
            enquiries.id,
            enquiries.name,
            enquiries.email,
            enquiries.phone,
            enquiries.message,
            enquiries.created_at,

            properties.title AS property_title,
            properties.location AS property_location

        FROM enquiries

        LEFT JOIN properties
        ON enquiries.property_id = properties.id

        ORDER BY enquiries.id DESC
    """).fetchall()


    connection.close()


    return render_template(
        "enquiries.html",
        enquiries=enquiries
    )


# =====================================================
# ENQUIRY DETAILS
# =====================================================

@app.route(
    "/enquiry/<int:enquiry_id>"
)
def enquiry_details(enquiry_id):

    if "owner_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    enquiry = connection.execute("""
        SELECT
            enquiries.id,
            enquiries.name,
            enquiries.email,
            enquiries.phone,
            enquiries.message,
            enquiries.created_at,

            properties.title AS property_title,
            properties.location AS property_location,
            properties.price AS property_price

        FROM enquiries

        LEFT JOIN properties
        ON enquiries.property_id = properties.id

        WHERE enquiries.id = ?
    """, (
        enquiry_id,
    )).fetchone()


    connection.close()


    if enquiry is None:

        return "Enquiry not found", 404


    return render_template(
        "enquiry_details.html",
        enquiry=enquiry
    )


# =====================================================
# START APPLICATION
# =====================================================

if __name__ == "__main__":

    # Make sure upload folder exists

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    # Initialize database

    init_db()


    # Start Flask

    app.run(
    debug=os.getenv(
        "FLASK_DEBUG",
        "True"
    ).lower() == "true"
)