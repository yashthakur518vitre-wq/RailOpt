import re

with open('scripts/generate_synthetic_data.py', 'r') as f:
    code = f.read()

code = code.replace(
    '\"status\": \"OVERDUE\" if due_date < current_date else np.random.choice([\"PENDING\", \"SCHEDULED\", \"IN_PROGRESS\", \"COMPLETED\"], p=[0.7, 0.15, 0.05, 0.1]),',
    '\"status\": \"OVERDUE\" if due < current_date else np.random.choice([\"PENDING\", \"SCHEDULED\", \"IN_PROGRESS\", \"COMPLETED\"], p=[0.7, 0.15, 0.05, 0.1]),'
)

with open('scripts/generate_synthetic_data.py', 'w') as f:
    f.write(code)
