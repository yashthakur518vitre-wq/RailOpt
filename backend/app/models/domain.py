from enum import Enum

class DepartmentType(str, Enum):
    TRACK = "TRACK"
    SIGNAL = "SIGNAL"
    OHE = "OHE"
    BRIDGE = "BRIDGE"

class CriticalityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TaskType(str, Enum):
    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    INSPECTION = "INSPECTION"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    OVERDUE = "OVERDUE"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    OPTIMIZED = "OPTIMIZED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class BlockStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
