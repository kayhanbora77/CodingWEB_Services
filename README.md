# Flight Data API Service

This project provides a FastAPI-based web service to query and retrieve flight data from a SQL Server database.

## Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.8+**
- **ODBC Driver 18 for SQL Server**: Required for the `pyodbc` connection.
  - [Download for Linux](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16#ubuntu-1804-2004-2204)
  - [Download for Windows](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)

## Installation

1.  Clone the repository or navigate to the project root directory.
2.  Install the required Python packages using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application uses environment variables for database configuration.

To configure your database connection:

1.  Create a `.env` file in the `C2R` directory or root directory.
2.  Add the following variables to the `.env` file:

    ```env
    DB_SERVER=localhost
    DB_DATABASE=C2RBetaDB
    DB_USERNAME=SA
    DB_PASSWORD=YOUR_PASSWORD_HERE
    DB_DRIVER={ODBC Driver 18 for SQL Server}
    DB_SCHEMA=dbo
    DB_TRUST_CERT=yes
    ```

3.  Update the values with your actual SQL Server credentials.

> [!NOTE]
> Ensure that your SQL Server instance allows TCP/IP connections and that the user has permissions to access the specified database.

## Running the Service

You can run the service using either `uvicorn` directly or by executing the Python script.

### Option 1: Using Uvicorn (Recommended)

Run the following command from the project root directory:

```bash
uvicorn C2R.delay_flights:app --reload
```

The API will be available at `http://localhost:5000` (default port in script) or `http://127.0.0.1:8000` depending on your launch arguments if different.
_Note: The script internally configures uvicorn to run on port 5000._

### Option 2: Using Python

Run the script directly:

```bash
python C2R/delay_flights.py
```

This will start the server on `http://0.0.0.0:5000`.

## API Documentation

Once the application is running, you can access the interactive API documentation (Swagger UI) at:

- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

### Endpoints

#### `GET /api/flights`

Retrieves a list of flights based on problem ID and airline ID.

- **Parameters**:
  - `problem_id` (int, default: 3): The problem ID to filter by.
  - `airline_id` (int, default: 1462): The airline ID to filter by.

- **Example Request**:
  ```
  GET /api/flights?problem_id=3&airline_id=1462
  ```

#### `GET /api/health`

Health check endpoint to verify the service status.

- **Response**: Returns the status, service name, and current timestamp.
