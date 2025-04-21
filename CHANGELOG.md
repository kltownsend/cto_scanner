# Changelog

All notable changes to the CTO Signal Scanner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for GPT-4o-2024-08-06 model in configuration options
- Improved virtual environment handling in installation scripts
- Better error messages and troubleshooting guidance
- Error report generation when PDF creation fails

### Changed
- Updated README.md with more comprehensive installation and usage instructions
- Enhanced install.py script to detect and fix corrupted virtual environments
- Improved port configuration for macOS to avoid AirPlay conflicts
- Enhanced PDF generation with better error handling and informative messages

### Fixed
- Fixed issue with Python executable not being found in virtual environment
- Improved error handling during installation process
- Fixed PDF download button not working when API errors occur
- Resolved issue with PDF path handling in the web application
- Fixed URL encoding for PDF download paths with special characters
- Fixed JSON serialization error with PosixPath objects causing scan to fail at 90%
- Fixed download route to properly handle URL-encoded paths and subdirectories

## [0.1.0] - 2024-07-15

### Added
- Initial release of CTO Signal Scanner
- Web-based interface for scanning and analyzing CTO signals
- AI-powered signal analysis using OpenAI's GPT models
- Report generation functionality
- Cross-platform compatibility (Windows, macOS, Linux)
- Installation scripts for different operating systems
- Configuration through .env file 