import re

with open('scripts/generate_synthetic_data.py', 'r') as f:
    code = f.read()

code = code.replace(
    '\"status\": np.random.choice([\"Pending\", \"Scheduled\", \"In_Progress\", \"Completed\"], p=[0.7, 0.15, 0.05, 0.1]),',
    '\"status\": \"OVERDUE\" if due_date < current_date else np.random.choice([\"PENDING\", \"SCHEDULED\", \"IN_PROGRESS\", \"COMPLETED\"], p=[0.7, 0.15, 0.05, 0.1]),'
)

code = code.replace(
    '\"status\": \"Approved\",',
    '\"status\": \"APPROVED\",'
)

with open('scripts/generate_synthetic_data.py', 'w') as f:
    f.write(code)
