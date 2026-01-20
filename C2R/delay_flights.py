from datetime import date
from fastapi import FastAPI, Query, HTTPException
import pyodbc
from datetime import datetime, timedelta
from typing import List, Dict
from pydantic import BaseModel
import os
from dotenv import load_dotenv

app = FastAPI(title="Flight Data API", version="1.0.0")

# Database configuration
# Load environment variables
load_dotenv()

# Database configuration
load_dotenv()

# Database configuration
DB_CONFIG = {
    "server": os.getenv("DB_SERVER", "localhost"),
    "database": os.getenv("DB_DATABASE", "C2RBetaDB"),
    "username": os.getenv("DB_USERNAME", "SA"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": os.getenv("DB_DRIVER", "{ODBC Driver 18 for SQL Server}"),
    "schema": os.getenv("DB_SCHEMA", "dbo"),
    "trust_cert": os.getenv("DB_TRUST_CERT", "yes"),
}


# Response models
class FlightData(BaseModel):
    FlightNumber: str
    FlightDate: date
    DepartureAirPort: str
    ArriveAirport: str


class FlightResponse(BaseModel):
    success: bool
    count: int
    data: List[FlightData]
    parameters: Dict


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


def get_db_connection():
    """Create and return a database connection"""
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate=yes;"  # Add this for SSL/TLS issues
    )
    return pyodbc.connect(conn_str)


def get_flight_data(problem_id: int, airline_id: int) -> List[Dict]:
    """
    Execute SQL query to get flight data

    Args:
        problem_id: The problem ID to filter by
        airline_id: The airline ID to filter by

    Returns:
        List of dictionaries containing flight information
    """
    # Calculate date range (current time - 6 months to current time)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months (365 * 3)

    schema = DB_CONFIG.get("schema", "dbo")

    # Updated SQL query with schema prefix
    sql_query = f"""
    SELECT 
        f.FlightNumber,
        af.[Date] AS FlightDate,
        depAirport.Name AS DepartureAirPort,
        arrAirport.Name AS ArriveAirport
    FROM {schema}.ActualFlights af
    JOIN {schema}.Flights f ON af.FlightId = f.Id
    JOIN {schema}.Airports depAirport ON f.DepartureAirportId = depAirport.Id
    JOIN {schema}.Airports arrAirport ON f.ArriveAirportId = arrAirport.Id
    WHERE af.ProblemId = ?
      AND f.AirlineId = ?
      AND af.[Date] >= ?
      AND af.[Date] < ?
    """

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute query with parameters
        cursor.execute(sql_query, (problem_id, airline_id, start_date, end_date))

        # Fetch all results
        columns = [column[0] for column in cursor.description]
        results = []

        for row in cursor.fetchall():
            result_dict = {}
            for i, column in enumerate(columns):
                value = row[i]
                # Convert datetime to string for JSON serialization
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d")
                result_dict[column] = value
            results.append(result_dict)

        return results

    except pyodbc.Error as e:
        raise Exception(f"Database error: {str(e)}")

    finally:
        if conn:
            conn.close()


@app.get("/api/flights", response_model=FlightResponse)
async def get_flights(
    problem_id: int = Query(default=3, description="Problem ID filter"),
    airline_id: int = Query(default=1462, description="Airline ID filter"),
):
    """
    API endpoint to retrieve flight data

    Args:
        problem_id: Problem ID filter (default: 3)
        airline_id: Airline ID filter (default: 1462)

    Returns:
        JSON response with flight data or error message
    """
    try:
        # Get flight data
        flights = get_flight_data(problem_id, airline_id)

        # Return successful response
        return {
            "success": True,
            "count": len(flights),
            "data": flights,
            "parameters": {
                "problem_id": problem_id,
                "airline_id": airline_id,
                "date_range": {
                    "start": (datetime.now() - timedelta(days=1095)).strftime(
                        "%Y-%m-%d"
                    ),
                    "end": datetime.now().strftime("%Y-%m-%d"),
                },
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Flight Data API",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=5000)
