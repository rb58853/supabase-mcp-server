# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).


## [0.3.5] - 2025-02-26
### Fixed
- Fixed an issue with `get_tables` so that it reliably returns foreign tables and views
- Updated docs to describe how to setup mcp.json with project-specific MCPs
- Expanded and improved test suite to cover each MCP tool


## [0.3.4] - 2025-02-25
### Fixed
- Improved `get_tables` to return foreign data tables


## [0.3.3] - 2025-02-25
### Fixed
- Fixed a bug with `readonly` scope being incorrectly managed in db client

## [0.3.2] - 2025-02-25
### Fixed
- Fixed a bug preventing execution of DDL commands (create, alter tables, etc.)

## [0.3.1] - 2025-02-23
### Changed
- Significantly improved docs to make install, configuration, usage instructions super clear


## [0.3.0] - 2025-02-23
### Added
- Full support for read-write SQL operations:
  - Implemented safety mode system with read-only (default) and read-write modes
  - Added mode switching with automatic reset to read-only
  - Enhanced transaction support for testing write operations
  - Improved error handling for read-only violations
- Support for Supabase Management API
  - Introduces supabase management API integration with safe (enabled by default) and yolo modes
  - Includes the following tools:
    - `send_management_api_request` to send arbitrary requests to Supabase Management API, with auto-injection of project ref and safety mode control.
    - `get_management_api_spec` to get the enriched API specification with safety information
    - `get_management_api_safety_rules` to get all safety rules including blocked and unsafe operations with human-readable explanations
    - `live_dangerously` to switch to yolo mode
  - Safety features:
    - Divides API methods into `safe`, `unsafe` and `blocked` categories based on the risk of the operation
    - Allows to switch between safe and yolo modes dynamically
    - Blocked operations (delete project, delete database) are not allowed regardless of the mode


## [0.2.2] - 2025-02-20
### Added
- Support for different Supabase regions:
  - Configuration via `SUPABASE_REGION` environment variable
  - Validation for all 16 supported AWS regions
  - Default to `us-east-1` for backward compatibility
  - Enhanced logging for region information
  - Comprehensive documentation and examples

## [0.2.1] - 2025-02-19
### Added
- Package distribution support:
  - PyPI package publishing setup
  - Installation via `pipx` and `uv`
  - Entry point scripts for direct execution
- Smithery.ai deployment configuration

### Changed
- BREAKING: Installation and execution methods:
  - Switched from direct script execution to proper module structure
  - Updated Cursor/Windsurf configuration for package-based execution
- Improved setup instructions in README

## [0.2.0] - 2025-02-18
Intermediary release for package distribution support

## [0.1.0] - 2025-02-16
### Added
- Initial release
- Basic MCP server functionality
- Supabase database connection support
- Integration with Cursor and Windsurf IDEs

[0.3.0]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.3.0
[0.2.2]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.2.2
[0.2.1]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.2.1
[0.2.0]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.2.0-dev0
[0.1.0]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.1.0
