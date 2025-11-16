# connection.py

import pyvisa
import pyvisa.errors
import sys

# --- Configuration ---
#VISA_ADDRESS = "visa://192.168.32.11/GPIB0::10::INSTR"
#VISA_ADDRESS = "visa://192.168.32.226/GPIB0::10::INSTR"
VISA_ADDRESS = "GPIB0::10::INSTR"

# Use the default ResourceManager to leverage NI-VISA, which fixed your error.
rm = pyvisa.ResourceManager()
inst = None
def get_instrument():
    """Returns the globally connected instrument object."""
    global inst
    return inst

def connect_instrument():
    """Establishes the PyVISA connection to the instrument."""
    global inst
    try:
        print(f"Attempting connection to: {VISA_ADDRESS}")
        inst = rm.open_resource(VISA_ADDRESS, timeout=5000)
        
        # Configure common communication settings
        inst.encoding = 'ascii'
        inst.read_termination = '\n'
        inst.write_termination = '\n'
        inst.timeout = 5000 # Set timeout for subsequent operations
        
        print("✅ Connection successful!")
        return inst
    
    except pyvisa.errors.VisaIOError as e:
        print(f"❌ ERROR: Could not connect to the instrument.")
        print(f"Details: {e}")
        # Terminate the script cleanly if connection fails
        sys.exit(1)

def close_instrument():
    """Closes the PyVISA connection."""
    global inst
    if inst and inst.session != 0:
        inst.close()
        print("🔌 Connection closed.")

# A helpful function for initial check
def identify_instrument():
    """Queries and returns the instrument ID string."""
    if inst:
        return inst.query("*IDN?").strip()
    return "Not Connected"