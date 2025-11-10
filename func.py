# func.py

import time
# Assuming your connection.py provides inst and get_instrument
from connection import inst, get_instrument 

# --- Waveform and Amplitude Functions ---

def set_function_square(freq_hz: float, ampl_vpp: float, offset_v: float, duty_cycle: float):
    """
    Sets the output to a Square Wave and immediately applies 
    Frequency, Amplitude, Offset, and Duty Cycle.
    
    Args:
        freq_hz (float): Frequency in Hertz.
        ampl_vpp (float): Amplitude in Volts Peak-to-Peak (VPP).
        offset_v (float): DC Offset Voltage in Volts.
        duty_cycle (float): Duty Cycle in percent (0.0 to 100.0).
    """
    inst_obj = get_instrument()
    if inst_obj:
        freq_str = f"{freq_hz:.2E}"
        ampl_str = f"{ampl_vpp:.2f}"
        offset_str = f"{offset_v:.2f}"
        duty_str = f"{duty_cycle:.2f}"
        
        # Reset the instrument to a known default state
        inst_obj.write("*RST")
        time.sleep(0.1) # Wait for reset to complete
        
        # SCPI command to set all parameters at once
        apply_cmd = f":SOURce:APPLy:SQUare {freq_str}, {ampl_str}, {offset_str}"
        inst_obj.write(apply_cmd)
        inst_obj.write(f":SOURce:FUNCtion:SQUare:DCYCle {duty_str}") # Set Duty Cycle separately
        inst_obj.write(":OUTPut:STATe ON") # Turn on the output
        
        print(f"Applied Square Wave: Freq={freq_hz:,.2f} Hz, Ampl={ampl_vpp:.2f} Vpp, Duty={duty_cycle:.2f}%")

# --- Trigger Functions ---

def set_trigger_internal():
    """Sets the trigger source to internal (Timer mode)."""
    inst_obj = get_instrument()
    if inst_obj:
        # 1. Set the trigger source to internal
        inst_obj.write(":TRIGger:SOURce INTernal")
        # 2. Set the trigger mode to Timer (or equivalent continuous mode)
        # Note: INIT:IMM usually starts a continuous run if not explicitly pulsed
        inst_obj.write(":INITiate:CONTinuous OFF") 
        print("Set Trigger Source to Internal (Continuous/Timer).")

def set_trigger_timer(delay_s: float):
    """
    Sets the time delay between internal triggers (the internal timer period).
    
    Args:
        delay_s (float): Delay time in seconds.
    """
    inst_obj = get_instrument()
    if inst_obj:
        # SCPI command to set the internal trigger period/timer delay
        #cmd = f":TRIGger:INTernal:TIMer {delay_s}"
        cmd = f":TRIGger:TIMer {delay_s}"
        inst_obj.write(cmd)
        print(f"Set Internal Trigger Timer (Period) to {delay_s} seconds.")
        
def clear_status():
    """Clears the instrument's status byte and error queue."""
    inst_obj = get_instrument()
    if inst_obj:
        inst_obj.write("*CLS")
        print("Status cleared.")