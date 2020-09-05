import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime as dt

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def home():
    return (
        f"Welcome to my API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create link from Python to DB
    session = Session(engine)

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    all_measurements = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict[date] = prcp
        all_measurements.append(measurement_dict)
    
    #Return the JSON representation of your dictionary.    
    return jsonify(all_measurements)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    
    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tob():

    session = Session(engine)
    most_active = session.query(Measurement.station, func.count(Measurement.station)).order_by(func.count(Measurement.station).desc()).group_by(Measurement.station)[0][0]
    
    last_date = session.query(Measurement.date).order_by(sqlalchemy.desc(Measurement.date)).limit(1)[0][0]
    last_date_obj = dt.strptime(last_date, '%Y-%m-%d')
    str_year = str(last_date_obj.year - 1)
    str_month = str(last_date_obj.month)
    str_day = str(last_date_obj.day)
    if last_date_obj.month < 10:
        str_month = '0' + str_month
    if last_date_obj.day < 10:
        str_day = '0' + str_day
    one_year_ago = str_year + '-' + str_month + '-' + str_day

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).filter(Measurement.date > one_year_ago).all()
    session.close()
    
    return jsonify(results)

@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start, end):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)