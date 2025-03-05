from abc import ABC, abstractmethod
from enum import Enum, IntEnum
from typing import Generic, TypeVar


class OperationRiskLevel(IntEnum):
    """Universal operation risk level mapping.

    Higher number reflects higher risk levels with 4 being the highest."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4


class SafetyMode(str, Enum):
    """Universal safety mode of a client (database, api, etc).
    Clients should always default to safe mode."""

    SAFE = "safe"
    UNSAFE = "unsafe"


class ClientType(str, Enum):
    """Types of clients that can be managed by the safety system."""

    DATABASE = "database"
    API = "api"


# Define a type variable for operations
T = TypeVar("T")


class SafetyConfigBase(Generic[T], ABC):
    """Abstract base class for all SafetyConfig classes of specific clients.

    Provides methods:
    - register safety configuration
    - to get / set safety level
    - check safety level of operation
    """

    @abstractmethod
    def get_risk_level(self, operation: T) -> OperationRiskLevel:
        """Get the risk level for an operation.

        Args:
            operation: The operation to check

        Returns:
            The risk level for the operation
        """
        pass

    def is_operation_allowed(self, risk_level: OperationRiskLevel, mode: SafetyMode) -> bool:
        """Check if an operation is allowed based on its risk level and the current safety mode.

        Args:
            risk_level: The risk level of the operation
            mode: The current safety mode

        Returns:
            True if the operation is allowed, False otherwise
        """
        # LOW risk operations are always allowed
        if risk_level == OperationRiskLevel.LOW:
            return True

        # MEDIUM risk operations are allowed only in UNSAFE mode
        if risk_level == OperationRiskLevel.MEDIUM:
            return mode == SafetyMode.UNSAFE

        # HIGH risk operations are allowed only in UNSAFE mode with confirmation
        if risk_level == OperationRiskLevel.HIGH:
            return mode == SafetyMode.UNSAFE

        # EXTREME risk operations are never allowed
        return False

    def needs_confirmation(self, risk_level: OperationRiskLevel) -> bool:
        """Check if an operation needs confirmation based on its risk level.

        Args:
            risk_level: The risk level of the operation

        Returns:
            True if the operation needs confirmation, False otherwise
        """
        # Only HIGH and EXTREME risk operations require confirmation
        return risk_level >= OperationRiskLevel.HIGH
