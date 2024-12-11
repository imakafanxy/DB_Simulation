# Database Simulation Tool

## Overview
This tool provides a graphical interface for simulating database updates based on historical data. Using the provided datetime and speed factor, the simulation replicates historical events into simulated tables at a user-defined pace.

## Features
- **Simulated Tables**: Automatically creates simulation tables based on the structure of original tables.
- **Custom Speed Factor**: Allows simulation to run at any desired speed.
- **Real-Time Updates**: Continuously populates simulated tables based on historical data.
- **UI Controls**: Start, stop, and delete simulations through a user-friendly interface.

## Requirements
- Python 3.8+
- Dependencies:
  - `pyodbc`
  - `tkinter`

## Usage

### 1. Run the Simulation Tool
Execute the tool with:
```bash
python db_simulation.py
```

### 2. User Interface
#### Input Fields
- **Datetime**: The starting point for the simulation in `YYYY-MM-DD HH:MM:SS` format.
- **Speed Factor**: Controls the speed of the simulation. For example:
  - `1` for real-time simulation.
  - `2` for double the speed.
  - `0.5` for half the speed.

#### Buttons
- **Submit**: Starts the simulation with the specified parameters.
- **Stop**: Stops the running simulation.
- **Delete**: Deletes all simulated tables.
- **Quit**: Stops all operations and closes the tool.

### Example Workflow
1. Enter `2023-01-01 10:00:00` in the datetime field.
2. Enter `2` in the speed factor field to run at double speed.
3. Click **Submit** to start the simulation.
4. Monitor logs to see rows being inserted into simulated tables.
5. Click **Stop** to halt the simulation.
6. Click **Delete** to remove all simulation tables.

## Code Structure

### `connect_to_db()`
Establishes a connection to the SQL Server database.

**Parameters**: None

**Returns**: Connection object

**Example Usage**:
```python
conn = connect_to_db()
```

### `create_simulation_tables(cursor, tables)`
Creates simulation tables for the given list of original tables.

**Parameters**:
- `cursor`: Database cursor.
- `tables`: List of table names to simulate.

**Example Usage**:
```python
create_simulation_tables(cursor, ["dbo.STRAND1_2", "dbo.STRAND3_4"])
```

### `get_first_time(table, datetime_column, datetime_format, datetime_input)`
Retrieves the first datetime in a table greater than or equal to the input datetime.

**Parameters**:
- `table`: Name of the table.
- `datetime_column`: Name of the datetime column.
- `datetime_format`: Format of the datetime.
- `datetime_input`: Input datetime string.

**Returns**: First datetime as a `datetime` object or `None` if no rows match.

### `update_table(selected_table, simulated_table, datetime_input, factor, datetime_column, datetime_format, base_time=None)`
Simulates inserting rows into a table at the specified speed factor.

**Parameters**:
- `selected_table`: Original table name.
- `simulated_table`: Simulated table name.
- `datetime_input`: Starting datetime.
- `factor`: Speed factor.
- `datetime_column`: Name of the datetime column.
- `datetime_format`: Format of the datetime.
- `base_time`: (Optional) Synchronization base time.

### `run_simulation(datetime_input, factor)`
Starts the simulation for all configured tables.

**Parameters**:
- `datetime_input`: Starting datetime.
- `factor`: Speed factor.

### `delete_simulation_tables()`
Deletes all simulated tables.

**Parameters**: None

### `stop_simulation()`
Stops all running simulation threads.

**Parameters**: None

## Notes
- Ensure that the database connection details in `connect_to_db()` are updated for your environment.
- The `tables` list in `run_simulation` should match the tables in your database.
- Simulation assumes datetime fields are consistent across tables.
