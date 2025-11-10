# main.py

import time
import csv
import os
from connection import connect_instrument, close_instrument, identify_instrument
# Import only the required functions
from func import set_function_square, set_trigger_internal, set_trigger_timer, clear_status
# Note: Data logging imports (log_data) are removed

CONFIG_FILENAME = "config.csv"

def read_config(filename: str) -> dict:
    """
    Reads the last data row from a CSV configuration file.
    Returns a dictionary with parameters or defaults if the file is not found.
    """
    defaults = {'freq_hz': 1.0, 'ampl_vpp': 1.0, 'offset_v': 0.0, 'duty_cycle': 50.0, 'trigger_delay_s': 2.0}

    if not os.path.exists(filename):
        print(f"⚠️  Warning: Config file '{filename}' not found. Using default parameters.")
        return defaults

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header
            last_row = None
            for row in reader:
                if row: # Ensure row is not empty
                    last_row = row
            
            if last_row:
                params = {
                    'freq_hz': float(last_row[0]),
                    'ampl_vpp': float(last_row[1]),
                    'offset_v': float(last_row[2]),
                    'duty_cycle': float(last_row[3]),
                    'trigger_delay_s': float(last_row[4])
                }
                print(f"✅ Loaded configuration from '{filename}'.")
                return params
            else:
                print(f"⚠️  Warning: Config file '{filename}' is empty. Using default parameters.")
                return defaults
    except (IOError, ValueError, IndexError) as e:
        print(f"❌ Error reading config file '{filename}': {e}. Using default parameters.")
        return defaults

if __name__ == "__main__":
    
    # Read parameters from the external file first
    config_params = read_config(CONFIG_FILENAME)

    # 1. Connect to the device
    # inst is set globally in connection.py
    connect_instrument() 
    
    try:
        print("-" * 40)
        # Use identify_instrument to confirm communication
        print(f"Connected to: {identify_instrument()}")
        clear_status()

        print("\n--- Device Configuration ---")
        
        # 2. Set Square Wave Parameters
        # Create a separate dictionary for the function arguments to avoid TypeError
        square_wave_params = {
            'freq_hz': config_params['freq_hz'],
            'ampl_vpp': config_params['ampl_vpp'],
            'offset_v': config_params['offset_v'],
            'duty_cycle': config_params['duty_cycle']
        }
        set_function_square(**square_wave_params)
        
        # 3. Set Internal Trigger Source
        set_trigger_internal()
        
        # 4. Set Trigger Timer/Period (e.g., re-trigger every 1 second)
        set_trigger_timer(delay_s=config_params['trigger_delay_s'])
        
        print("\nConfiguration complete. Signal is running.")
        
        # Add a delay here so the instrument stays connected long enough to observe settings
        time.sleep(2)
        
    finally:
        # 5. Close the connection
        print("-" * 40)
        close_instrument()