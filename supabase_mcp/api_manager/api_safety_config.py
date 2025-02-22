# supabase_mcp/api_manager/config.py
from enum import Enum


class SafetyLevel(Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"
    BLOCKED = "blocked"


class SafetyConfig:
    """Configuration for Supabase Management API safety checks"""

    # Permanently blocked operations - never allowed
    BLOCKED_OPERATIONS = {
        "DELETE": [
            "/v1/projects/{ref}",  # Delete project
            "/v1/organizations/{slug}",  # Delete organization
            "/v1/projects/{ref}/database",  # Delete database
        ]
    }

    # Unsafe operations - require YOLO mode
    UNSAFE_OPERATIONS = {
        "POST": [
            "/v1/projects",  # Create project
            "/v1/organizations",  # Create org
            "/v1/projects/{ref}/restore",  # Restore project
            "/v1/projects/{ref}/pause",  # Pause project - can impact production
        ],
        "PATCH": [
            "/v1/projects/{ref}/config/auth",  # Auth config
            "/v1/projects/{ref}/config/database",  # DB config
            "/v1/projects/{ref}/config/pooler",  # Connection pooling changes - can impact DB performance
        ],
        "PUT": [
            "/v1/projects/{ref}/config/secrets",  # Update secrets
            "/v1/projects/{ref}/config/database/postgres",  # Postgres config changes - critical DB settings
        ],
    }

    def list_all_rules(self) -> str:
        """List all safety rules"""
        return f"Blocked operations: {self.BLOCKED_OPERATIONS}\nUnsafe operations: {self.UNSAFE_OPERATIONS}"

    def is_operation_allowed(self, method: str, path: str) -> tuple[bool, str, SafetyLevel]:
        """Determine operation safety level and status"""
        # Check blocked first
        if self._is_blocked(method, path):
            return False, "Operation is blocked for safety", SafetyLevel.BLOCKED

        # Check if unsafe
        if self._is_unsafe(method, path):
            return True, "Operation requires YOLO mode", SafetyLevel.UNSAFE

        # Default to safe
        return True, "Operation allowed", SafetyLevel.SAFE

    def _is_blocked(self, method: str, path: str) -> bool:
        return self._path_matches_patterns(method, path, self.BLOCKED_OPERATIONS)

    def _is_unsafe(self, method: str, path: str) -> bool:
        return self._path_matches_patterns(method, path, self.UNSAFE_OPERATIONS)

    def _path_matches_patterns(self, method: str, path: str, patterns: dict) -> bool:
        """Check if path matches any pattern"""
        if method not in patterns:
            return False

        for pattern in patterns[method]:
            if self._path_matches(pattern, path):
                return True
        return False

    def _path_matches(self, pattern: str, path: str) -> bool:
        """Check if path matches pattern with parameters"""
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return False

        return all(
            p1 == p2 or (p1.startswith("{") and p1.endswith("}"))
            for p1, p2 in zip(pattern_parts, path_parts, strict=False)
        )
