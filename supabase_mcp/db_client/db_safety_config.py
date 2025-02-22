from enum import Enum


class DbSafetyLevel(str, Enum):
    RO = "ro"
    RW = "rw"
