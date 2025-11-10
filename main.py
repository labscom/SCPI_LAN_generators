# main.py - Direct Execution with User Selection

import time
import csv
import os
import sys

# Import connection functions
from connection import connect_instrument, close_instrument, identify_instrument

# Import instrument control functions
from func import set_function_square, set_trigger_internal, set_trigger_timer, clear_status

# --- Configuration ---
CONFIG_FILENAME = "config.csv"

def read_config(filename: str) -> list:
    """
    Reads ALL data rows from a CSV configuration file.
    Returns a list of dictionaries, one for each sequence.
    (Keeping your robust reading logic from before)
    """
    all_sequences = [] 
    
    if not os.path.exists(filename):
        print(f"❌ Error: Config file '{filename}' not found. Cannot proceed.")
        sys.exit(1)

    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for i, row in enumerate(reader, start=1):
                if not row or not row.get("pulse_name"): continue 
                
                try:
                    params = {
                        'pulse_name': row['pulse_name'],
                        'freq_hz': float(row['frequency_hz']),
                        'ampl_vpp': float(row['amplitude_vpp']),
                        'offset_v': float(row['offset_v']),
                        'duty_cycle': float(row['duty_cycle']),
                        'trigger_delay_s': float(row['trigger_delay_s'])
                    }
                    all_sequences.append(params)
                except (ValueError, KeyError) as e:
                    print(f"❌ Error converting or accessing column in row {i} ('{row.get('pulse_name', 'Unknown')}'). Skipping. Details: {e}")
            
            if not all_sequences:
                print(f"❌ Error: Config file '{filename}' contains no valid data rows.")
                sys.exit(1)
            
            print(f"✅ Successfully loaded {len(all_sequences)} sequences from '{filename}'.")
            return all_sequences
            
    except Exception as e:
        print(f"❌ An error occurred while reading '{filename}'. Details: {e}")
        sys.exit(1)


def select_sequence(sequences: list) -> dict:
    """
    Displays the list of sequences and prompts the user to select one.
    Returns the dictionary for the selected sequence.
    """
    print("\n" + "=" * 40)
    print("📋 Available Sequences:")
    print("=" * 40)
    
    # 1. Display list of sequences
    for index, seq in enumerate(sequences):
        print(f"[{index + 1}] {seq['pulse_name']}")
    
    print("-" * 40)
    
    while True:
        try:
            # 2. Get user input
            choice = input(f"Enter the number of the sequence to run (1-{len(sequences)}): ")
            choice_index = int(choice) - 1
            
            # 3. Validate input
            if 0 <= choice_index < len(sequences):
                selected_seq = sequences[choice_index]
                print(f"➡️ Selected: **{selected_seq['pulse_name']}**")
                return selected_seq
            else:
                print("❌ Invalid selection. Please enter a number from the list.")
        except ValueError:
            print("❌ Invalid input. Please enter a whole number.")


def execute_sequence(config_params: dict):
    """
    Connects to the instrument, applies the given configuration,
    and runs it for a set time.
    """
    # 1. Connect to the device (will exit if connection fails)
    connect_instrument() 
    
    try:
        print("-" * 50)
        print(f"Connected to: {identify_instrument()}")
        clear_status()
        
        sequence_name = config_params['pulse_name']
        run_time_s = 5 # Define how long this sequence should run
        
        print("\n" + "=" * 50)
        print(f"--- STARTING SEQUENCE: {sequence_name} ---")
        print(f"Running for {run_time_s} seconds...")
        print("=" * 50)
        
        # 2. Set Square Wave Parameters
        square_wave_params = {
            'freq_hz': config_params['freq_hz'],
            'ampl_vpp': config_params['ampl_vpp'],
            'offset_v': config_params['offset_v'],
            'duty_cycle': config_params['duty_cycle']
        }
        set_function_square(**square_wave_params) 
        
        # 3. Set Trigger Source and Period
        set_trigger_internal()
        set_trigger_timer(delay_s=config_params['trigger_delay_s'])
        
        # Wait for the sequence to run
        time.sleep(run_time_s) 
        
        print("\n" + "#" * 50)
        print(f"SEQUENCE '{sequence_name}' COMPLETE.")
        print("#" * 50)
        
    except Exception as e:
        print(f"❌ An unexpected error occurred during live execution: {e}")
        
    finally:
        # 4. Close the connection
        close_instrument()


if __name__ == "__main__":
    
    # 1. Read all available sequences from the config file
    all_sequences = read_config(CONFIG_FILENAME) 
    
    # 2. Prompt the user to select one sequence
    selected_sequence_config = select_sequence(all_sequences)

    # 3. Execute the selected sequence
    execute_sequence(selected_sequence_config)