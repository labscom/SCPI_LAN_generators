# generate_csv.py
import csv
from data import generate_pulses

pulses = generate_pulses()
with open("pulses_generated.tsv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([
        "pulse_name", "frequency_hz", "amplitude_vpp",
        "offset_v", "duty_cycle", "trigger_delay_s"
    ])
    for p in pulses:
        writer.writerow([
            p["description"],
            p["frequency_hz"],
            p["amplitude_vpp"],
            p["offset_v"],
            p["duty_cycle"],
            p["trigger_delay_s"]
        ])