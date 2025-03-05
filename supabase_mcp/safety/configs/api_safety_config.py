"""API safety configuration for Supabase Management API.

This module defines the safety configuration for the Supabase Management API,
mapping API operations to risk levels and providing methods to check if operations
are allowed based on the current safety mode.
"""

from enum import Enum

from supabase_mcp.safety.core import OperationRiskLevel, SafetyConfigBase


class HTTPMethod(str, Enum):
    """HTTP methods used in API operations."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APISafetyConfig(SafetyConfigBase[tuple[str, str]]):
    """Safety configuration for API operations.

    The operation type is a tuple of (method, path).
    """

    # Maps risk levels to operations (method + path patterns)
    PATH_SAFETY_CONFIG = {
        OperationRiskLevel.EXTREME: {
            HTTPMethod.DELETE: [
                "/v1/projects/{ref}",  # Delete project.  Irreversible, complete data loss.
            ]
        },
        OperationRiskLevel.HIGH: {
            HTTPMethod.DELETE: [
                "/v1/projects/{ref}/branches/{branch_id}",  # Delete a database branch.  Data loss on branch.
                "/v1/projects/{ref}/branches",  # Disables preview branching. Disruptive to development workflows.
                "/v1/projects/{ref}/custom-hostname",  # Deletes custom hostname config.  Can break production access.
                "/v1/projects/{ref}/vanity-subdomain",  # Deletes vanity subdomain config.  Breaks vanity URL access.
                "/v1/projects/{ref}/network-bans",  # Remove network bans (can expose database to wider network).
                "/v1/projects/{ref}/secrets",  # Bulk delete secrets. Can break application functionality if critical secrets are removed.
                "/v1/projects/{ref}/functions/{function_slug}",  # Delete function.  Breaks functionality relying on the function.
                "/v1/projects/{ref}/api-keys/{id}",  # Delete api key.  Can break API access.
                "/v1/projects/{ref}/config/auth/sso/providers/{provider_id}",  # Delete SSO Provider.  Breaks SSO login.
                "/v1/projects/{ref}/config/auth/signing-keys/{id}",  # Delete signing key. Can break JWT verification.
            ],
            HTTPMethod.POST: [
                "/v1/projects/{ref}/pause",  # Pause project - Impacts production, database becomes unavailable.
                "/v1/projects/{ref}/restore",  # Restore project - Can overwrite existing data with backup.
                "/v1/projects/{ref}/upgrade",  # Upgrades the project's Postgres version - potential downtime/compatibility issues.
                "/v1/projects/{ref}/read-replicas/remove",  # Remove a read replica.  Can impact read scalability.
                "/v1/projects/{ref}/restore/cancel",  # Cancels the given project restoration. Can leave project in inconsistent state.
                "/v1/projects/{ref}/readonly/temporary-disable",  # Disables readonly mode. Allows potentially destructive operations.
            ],
        },
        OperationRiskLevel.MEDIUM: {
            HTTPMethod.POST: [
                "/v1/projects",  # Create project.  Significant infrastructure change.
                "/v1/organizations",  # Create org. Significant infrastructure change.
                "/v1/projects/{ref}/branches",  # Create a database branch.  Could potentially impact production if misused.
                "/v1/projects/{ref}/branches/{branch_id}/push",  # Push a database branch.  Could overwrite production data if pushed to the wrong branch.
                "/v1/projects/{ref}/branches/{branch_id}/reset",  # Reset a database branch. Data loss on the branch.
                "/v1/projects/{ref}/custom-hostname/initialize",  # Updates custom hostname configuration, potentially breaking existing config.
                "/v1/projects/{ref}/custom-hostname/reverify",  # Attempts to verify DNS configuration.  Could disrupt custom hostname if misconfigured.
                "/v1/projects/{ref}/custom-hostname/activate",  # Activates custom hostname. Could lead to downtime during switchover.
                "/v1/projects/{ref}/network-bans/retrieve",  # Gets project's network bans. Information disclosure, though less risky than removing bans.
                "/v1/projects/{ref}/network-restrictions/apply",  # Updates project's network restrictions. Could block legitimate access if misconfigured.
                "/v1/projects/{ref}/secrets",  # Bulk create secrets.  Could overwrite existing secrets if names collide.
                "/v1/projects/{ref}/upgrade/status",  # get status for upgrade
                "/v1/projects/{ref}/database/webhooks/enable",  # Enables Database Webhooks.  Could expose data if webhooks are misconfigured.
                "/v1/projects/{ref}/functions",  # Create a function (deprecated).
                "/v1/projects/{ref}/functions/deploy",  # Deploy a function. Could break functionality if deployed code has errors.
                "/v1/projects/{ref}/config/auth/sso/providers",  # Create SSO provider.  Could impact authentication if misconfigured.
                "/v1/projects/{ref}/database/backups/restore-pitr",  # Restore a PITR backup.  Can overwrite data.
                "/v1/projects/{ref}/read-replicas/setup",  # Setup a read replica
                "/v1/projects/{ref}/database/query",  # Run SQL query.  *Crucially*, this allows arbitrary SQL, including `DROP TABLE`, `DELETE`, etc.
                "/v1/projects/{ref}/config/auth/signing-keys",  # Create a new signing key, requires key rotation.
                "/v1/oauth/token",  # Exchange auth code for user's access token. Security-sensitive.
                "/v1/oauth/revoke",  # Revoke oauth app authorization.  Can break application access.
                "/v1/projects/{ref}/api-keys",  # Create an API key
            ],
            HTTPMethod.PATCH: [
                "/v1/projects/{ref}/config/auth",  # Auth config.  Could lock users out or introduce vulnerabilities if misconfigured.
                "/v1/projects/{ref}/config/database/pooler",  # Connection pooling changes.  Can impact database performance.
                "/v1/projects/{ref}/postgrest",  # Update Postgrest config.  Can impact API behavior.
                "/v1/projects/{ref}/functions/{function_slug}",  # Updates a function.  Can break functionality.
                "/v1/projects/{ref}/config/storage",  # Update Storage config.  Can change file size limits, etc.
                "/v1/branches/{branch_id}",  # Update database branch config.
                "/v1/projects/{ref}/api-keys/{id}",  # Updates a API key
                "/v1/projects/{ref}/config/auth/signing-keys/{id}",  # updates signing key.
            ],
            HTTPMethod.PUT: [
                "/v1/projects/{ref}/config/database/postgres",  # Postgres config changes.  Can significantly impact database performance/behavior.
                "/v1/projects/{ref}/pgsodium",  # Update pgsodium config.  *Critical*: Updating the `root_key` can cause data loss.
                "/v1/projects/{ref}/ssl-enforcement",  # Update SSL enforcement config.  Could break access if misconfigured.
                "/v1/projects/{ref}/functions",  # Bulk update Edge Functions. Could break multiple functions at once.
                "/v1/projects/{ref}/config/auth/sso/providers/{provider_id}",  # Update sso provider.
            ],
        },
    }

    def get_risk_level(self, operation: tuple[str, str]) -> OperationRiskLevel:
        """Get the risk level for an API operation.

        Args:
            operation: Tuple of (method, path)

        Returns:
            The risk level for the operation
        """
        method, path = operation

        # Check each risk level from highest to lowest
        for risk_level in sorted(self.PATH_SAFETY_CONFIG.keys(), reverse=True):
            if self._path_matches_risk_level(method, path, risk_level):
                return risk_level

        # Default to medium risk
        return OperationRiskLevel.MEDIUM

    def _path_matches_risk_level(self, method: str, path: str, risk_level: OperationRiskLevel) -> bool:
        """Check if the method and path match any pattern for the given risk level."""
        patterns = self.PATH_SAFETY_CONFIG.get(risk_level, {})

        if method not in patterns:
            return False

        for pattern in patterns[method]:
            # Convert placeholder pattern to regex
            regex_pattern = self._convert_pattern_to_regex(pattern)
            if re.match(regex_pattern, path):
                return True

        return False

    def _convert_pattern_to_regex(self, pattern: str) -> str:
        """Convert a placeholder pattern to a regex pattern.

        Replaces placeholders like {ref} with regex patterns for matching.
        """
        # Replace common placeholders with regex patterns
        regex_pattern = pattern
        regex_pattern = regex_pattern.replace("{ref}", r"[^/]+")
        regex_pattern = regex_pattern.replace("{id}", r"[^/]+")
        regex_pattern = regex_pattern.replace("{slug}", r"[^/]+")
        regex_pattern = regex_pattern.replace("{table}", r"[^/]+")
        regex_pattern = regex_pattern.replace("{branch_id}", r"[^/]+")
        regex_pattern = regex_pattern.replace("{function_slug}", r"[^/]+")

        # Add end anchor to ensure full path matching
        if not regex_pattern.endswith("$"):
            regex_pattern += "$"

        return regex_pattern
