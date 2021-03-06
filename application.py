import requests
from flask import Flask, render_template, jsonify, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def index():
    flights = Flight.query.all()
    return render_template("index.html", flights=flights)


@app.route("/book", methods=["POST"])
def book():
    """Book a flight."""

    # Get form information.
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure the flight exists.
    flight = Flight.query.get(flight_id)
    if not flight:
        return render_template("error.html", message="No such flight with that id.")

    # Add passenger.
    flight.add_passenger(name)
    return render_template("success.html")


@app.route("/flights")
def flights():
    """List all flights."""
    flights = Flight.query.all()
    return render_template("flights.html", flights=flights)


@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    """List details about a single flight."""

    # flight_info = flight_api(flight_id).json
    flight_info = requests.get(f"http://localhost:5000/api/flights/{flight_id}").json()
    if "error" in flight_info:

        return render_template("error.html", message="No such flight.")
    return render_template("flight.html", flight=flight_info, passengers=flight_info['passengers'])
    # # Make sure flight exists.
    # flight = Flight.query.get(flight_id)
    # if flight is None:
    #     return render_template("error.html", message="No such flight.")
    #
    # # Get all passengers.
    # passengers = flight.passengers
    # return render_template("flight.html", flight=flight, passengers=passengers)


@app.route("/api/flights/<int:flight_id>", methods=['GET'])
def flight_api(flight_id):
    """Return details about a single flight."""

    # Make sure flight exists.
    flight = Flight.query.get(flight_id)
    if flight is None:
        return jsonify({"error": "Invalid flight_id"}), 422

    # Get all passengers.
    passengers = flight.passengers
    names = []
    for passenger in passengers:
        names.append(passenger.name)
    return jsonify({
            "origin": flight.origin,
            "destination": flight.destination,
            "duration": flight.duration,
            "passengers": names
        })

@app.route("/api/reservations/<int:reservation_id>", methods=['GET'])
def reservations_api(reservation_id):
    """Return details about a reservation flight."""

    # Make sure flight exists.
    reservation = Passenger.query.get(reservation_id)

    if reservation is None:
        return jsonify({"error": "Invalid reservation_id"}), 422

    flight_info = Flight.query.get(reservation.flight_id)

    if flight_info is None:
        return jsonify({"error": "Invalid flight_id: {reservation.flight_id}"}), 422
    # return flight reservation info
    return jsonify({
            "origin": flight_info.origin,
            "destination": flight_info.destination,
            "duration": flight_info.duration,
            "passenger": reservation.name,
            "reservation_id": reservation.id
        })

@app.route("/api/reservation/new", methods=['POST'])
def api_book_flight():
    name = request.json['name']
    flight_id = request.json['flight_id']
    #Make sure the flight exists
    flight = Flight.query.get(flight_id)
    if not flight:
        return jsonify({"error": "No such flight id"})
    reservation_id = flight.add_passenger(name)

    return jsonify({
            "origin": flight.origin,
            "destination": flight.destination,
            "duration": flight.duration,
            "name": name,
            "reservation_id": reservation_id
    })

@app.route("/api/flight/new", methods=["POST"])
def api_create_flight():
    origin = request.json['origin']
    destination = request.json['destination']
    duration = request.json['duration']

    flight = Flight(origin, destination, duration)
    flight_id = flight.add_flight()

    return jsonify({
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "duration": duration
    })