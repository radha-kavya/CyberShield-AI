import pandas as pd
from pathlib import Path

# Create security event data
data = {
    "event_id": [
        "XLS001",
        "XLS002",
        "XLS003",
        "XLS004",
        "XLS005"
    ],
    "source_ip": [
        "198.51.100.23",
        "203.0.113.10",
        "192.0.2.15",
        "198.51.100.50",
        "203.0.113.10"
    ],
    "event_type": [
        "Failed login",
        "SSH access attempt",
        "Normal login",
        "RDP access",
        "Repeated SSH attempt"
    ],
    "severity": [
        "High",
        "High",
        "Low",
        "Medium",
        "High"
    ]
}

# Convert data into DataFrame
df = pd.DataFrame(data)

# Create output folder
output_path = Path("data/logs/security_events.xlsx")
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save as Excel file
df.to_excel(output_path, index=False)

print("Excel dataset created successfully!")
print(f"File location: {output_path}")
print(f"Total records: {len(df)}")