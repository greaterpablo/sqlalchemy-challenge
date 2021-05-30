import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, json, jsonify
from sqlalchemy.sql.expression import all_

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())

# Save reference to the table
measurement=Base.classes.measurement
station=Base.classes.station

#Flask Setup
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        
        f"/api/v1.0/precipitation <br/>" 
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/[Start Date]    <>     /api/v1.0/YYYY-MM-DD <br/>"
        f"/api/v1.0/[Start Date]/[End Date]     <>    /api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    print('Access precipitations page')
  
    session = Session(engine)
    prcp_results = session.query(measurement.date, measurement.prcp).\
        order_by(measurement.date).all()
    session.close()

    prcp = list(np.ravel(prcp_results))
    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results=session.query(measurement.station).group_by(measurement.station)
    session.close()

    all_stations=[]
    for sta in results:
        station_dict={}
        station_dict['station']=sta
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    ma_station=session.query(measurement.station,func.count(measurement.station)).group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]

    results=session.query(measurement.station, measurement.tobs,measurement.date).\
        filter(measurement.station==ma_station).filter(measurement.date>'2016-08-23').all()

    session.close()

    all_tobs=[]
    for _ in results:
        tobs_dict={}
        tobs_dict['Station']=_[0]
        tobs_dict['Temperature']=_[1]
        tobs_dict['Date']=_[2]
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def date_filter(start):
    session=Session(engine)

    Lowest=session.query(func.min(measurement.tobs)).filter(measurement.date>start).all()
    Highest=session.query(func.max(measurement.tobs)).filter(measurement.date>start).all()
    Average=session.query(func.avg(measurement.tobs)).filter(measurement.date>start).all()

    query_dict={}
    query_dict['Lowest']=Lowest[0]
    query_dict['Highest']=Highest[0]
    query_dict['Average']=Average[0]

    # query_dict.append(Lowest)
    return jsonify(query_dict)

@app.route("/api/v1.0/<start>/<end>")
def date_filter2(start,end):
    session=Session(engine)

    Lowest=session.query(func.min(measurement.tobs)).filter(measurement.date>start).filter(measurement.date<end).all()
    Highest=session.query(func.max(measurement.tobs)).filter(measurement.date>start).filter(measurement.date<end).all()
    Average=session.query(func.avg(measurement.tobs)).filter(measurement.date>start).filter(measurement.date<end).all()

    query_dict={}
    query_dict['Lowest']=Lowest[0]
    query_dict['Highest']=Highest[0]
    query_dict['Average']=Average[0]

    # query_dict.append(Lowest)
    return jsonify(query_dict)


if __name__ == '__main__':
    app.run(debug=True)

