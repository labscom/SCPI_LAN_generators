# data.py
from typing import List, TypedDict

class PulseParams(TypedDict):
    frequency_hz: float
    amplitude_vpp: float
    offset_v: float
    duty_cycle: float
    trigger_delay_s: float
    description: str

# ----------------------------------------------------------------------
# Base configurations
PULSE1_BASE = {
    "frequency_hz": 2.5,
    "amplitude_vpp": 5.0,
    "offset_v": 2.5,
    "duty_cycle": 50,
}
PULSE1_DELAYS = [1.0, 0.5, 0.333]

PULSE2_BASE = {
    "frequency_hz": 1000,
    "amplitude_vpp": 5.0,
    "offset_v": 2.5,
    "duty_cycle": 50,
}
PULSE2_DELAYS = [5.0, 1.0, 0.333]

# ----------------------------------------------------------------------
def generate_pulses() -> List[PulseParams]:
    """Generate full list of pulse configurations with descriptions."""
    pulses = []

    for delay in PULSE1_DELAYS:
        pulses.append(PulseParams(
            **PULSE1_BASE,
            trigger_delay_s=delay,
            description=f"ISO7637-2 Pulse 1 (Freq 2.5Hz, Delay {1/delay:.0f}s, ~{int(5000/(1/delay))} pulses)"
        ))

    for delay in PULSE2_DELAYS:
        pulses.append(PulseParams(
            **PULSE2_BASE,
            trigger_delay_s=delay,
            description=f"ISO7637-2 Pulse 2a (Freq 1kHz, Delay {delay}s)"
        ))

    return pulses

# ----------------------------------------------------------------------
# Also expose grouped version for web/JSON
PULSE_GROUPS = {
    "ISO7637-2 Pulse 1": [
        {**PULSE1_BASE, "trigger_delay_s": d} for d in PULSE1_DELAYS
    ],
    "ISO7637-2 Pulse 2a": [
        {**PULSE2_BASE, "trigger_delay_s": d} for d in PULSE2_DELAYS
    ]
}