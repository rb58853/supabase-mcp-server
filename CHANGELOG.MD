# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

[0.2.1]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.2.1
[0.2.0]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.2.0-dev0
[0.1.0]: https://github.com/alexander-zuev/supabase-mcp-server/releases/tag/v0.1.0
