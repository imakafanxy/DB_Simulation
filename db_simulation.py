import tkinter as tk
import pyodbc
import time
import threading
from datetime import datetime, timedelta

running_threads = []
stop_flag = threading.Event()

def connect_to_db():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=127.0.0.1;'  
        'DATABASE=STRAND_DATA;'  
        'UID=sa;'
        'PWD=iilab109;'
    )
    return conn

def create_simulation_tables(cursor, tables):
    for table in tables:
        simulated_table = f"SIMULATED_{table.split('.')[1]}"
        cursor.execute(f"IF OBJECT_ID('{simulated_table}', 'U') IS NULL BEGIN "
                       f"SELECT TOP 0 * INTO {simulated_table} FROM {table} END")
    cursor.commit()

def get_first_time(table, datetime_column, datetime_format, datetime_input):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = f"SELECT TOP 1 [{datetime_column}] FROM {table} WHERE [{datetime_column}] >= ? ORDER BY [{datetime_column}] ASC"
    cursor.execute(query, datetime_input)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if result:
        first_time_str = str(result[0])
        return datetime.strptime(first_time_str, datetime_format)
    else:
        return None

def update_table(selected_table, simulated_table, datetime_input, factor, datetime_column, datetime_format, base_time=None):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"SELECT * FROM {selected_table} WHERE [{datetime_column}] >= ? ORDER BY [{datetime_column}] ASC"
    cursor.execute(query, datetime_input)
    
    rows = cursor.fetchall()
    column_names = [f"[{desc[0]}]" for desc in cursor.description]
    
    insert_query = f"INSERT INTO {simulated_table} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
    
    datetime_input_obj = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
    simulation_start_time = time.time()
    
    datetime_column_index = column_names.index(f"[{datetime_column}]")
    
    for i, row in enumerate(rows):
        if stop_flag.is_set():
            break

        row_time_str = str(row[datetime_column_index])
        row_time_obj = datetime.strptime(row_time_str, datetime_format)
        time_difference = (row_time_obj - datetime_input_obj).total_seconds()

        if base_time:
            # 시간 동기화 기준을 맞춰서 시뮬레이션 시간 조정
            simulation_current_time = base_time + (time_difference / factor)
        else:
            simulation_current_time = simulation_start_time + (time_difference / factor)

        while time.time() < simulation_current_time:
            if stop_flag.is_set():
                break
            time.sleep(0.01)

        cursor.execute(insert_query, row)
        conn.commit()  # 각 스레드에서 커밋 처리
        print(f"Inserted row {i+1}/{len(rows)} into {simulated_table}: {row}")
    
    cursor.close()  # 각 스레드에서 커서 닫기
    conn.close()    # 각 스레드에서 연결 닫기

def run_simulation(datetime_input, factor):
    global running_threads
    stop_flag.clear()
    running_threads = []

    tables = [
        ("dbo.STRAND1_2", "DATATIME", "%Y-%m-%d %H:%M:%S"),
        ("dbo.STRAND3_4", "DATATIME", "%Y-%m-%d %H:%M:%S"),
        ("dbo.STRAND5_6", "DATATIME", "%Y-%m-%d %H:%M:%S"),
        ("dbo.SAMPLE", "CREATE_DATE", "%Y%m%d%H%M%S")
    ]
    conn = connect_to_db()
    cursor = conn.cursor()

    create_simulation_tables(cursor, [table[0] for table in tables])

    # 각 테이블의 첫 시간 가져오기
    first_times = []
    for table, datetime_column, datetime_format in tables:
        first_time = get_first_time(table, datetime_column, datetime_format, datetime_input)
        if first_time:
            first_times.append(first_time)
    
    if not first_times:
        print("No data found for the provided datetime input.")
        return

    # 기준 시간을 가장 이른 시간으로 설정
    base_time = min(first_times)
    base_unix_time = time.time() + (base_time - datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")).total_seconds() / factor

    for table, datetime_column, datetime_format in tables:
        simulated_table = f"SIMULATED_{table.split('.')[1]}"
        thread = threading.Thread(target=update_table, args=(table, simulated_table, datetime_input, factor, datetime_column, datetime_format, base_unix_time))
        thread.start()
        running_threads.append(thread)
    
    for thread in running_threads:
        thread.join()

def delete_simulation_tables():
    tables = ["dbo.SIMULATED_STRAND1_2", "dbo.SIMULATED_STRAND3_4", "dbo.SIMULATED_STRAND5_6", "dbo.SIMULATED_SAMPLE"]
    conn = connect_to_db()
    cursor = conn.cursor()
    
    for table in tables:
        cursor.execute(f"IF OBJECT_ID('{table}', 'U') IS NOT NULL DROP TABLE {table}")
    
    cursor.commit()
    cursor.close()
    conn.close()
    print("All simulated tables have been deleted.")

def stop_simulation():
    global running_threads
    stop_flag.set()

    for thread in running_threads:
        thread.join()
    running_threads = []
    print("Simulation stopped.")

def create_ui():
    def on_submit():
        datetime_input = datetime_entry.get()
        factor = float(factor_entry.get())
        run_simulation(datetime_input, factor)
    
    def on_stop():
        stop_simulation()
    
    def on_delete():
        delete_simulation_tables()

    def on_quit():
        stop_simulation()
        root.destroy()

    root = tk.Tk()
    root.title("Database Simulation")

    tk.Label(root, text="Enter Datetime (YYYY-MM-DD HH:MM:SS):").grid(row=0, column=0, padx=10, pady=10)
    datetime_entry = tk.Entry(root)
    datetime_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Enter Speed Factor:").grid(row=1, column=0, padx=10, pady=10)
    factor_entry = tk.Entry(root)
    factor_entry.grid(row=1, column=1, padx=10, pady=10)
    factor_entry.insert(0, "1")

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=2, column=0, columnspan=2, pady=10)

    stop_button = tk.Button(root, text="Stop", command=on_stop)
    stop_button.grid(row=3, column=0, columnspan=2, pady=10)

    delete_button = tk.Button(root, text="Delete", command=on_delete)
    delete_button.grid(row=4, column=0, columnspan=2, pady=10)

    quit_button = tk.Button(root, text="Quit", command=on_quit)
    quit_button.grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_ui()
