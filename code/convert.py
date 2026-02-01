import pandas as pd

# Load the CSV
df = pd.read_csv("../data/attendance.csv", header=None, names=["Student ID", "Timestamp"])

# Save as Excel
df.to_excel("../data/attendance.xlsx", index=False)

print("✅ Excel file saved as attendance.xlsx")
