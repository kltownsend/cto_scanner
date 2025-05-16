# Changelog

All notable changes to the CTO Signal Scanner project will be documented in this file.

## [Unreleased]

### Added
- Advanced feed management system with separate storage for default and custom feeds
- Feed validation and health monitoring system
- Protected default feeds that cannot be removed
- Custom feed support with separate storage in `custom_feeds.json`
- Feed health status indicators in the UI
- Automatic feed validation on addition and during scans
- Real-time progress updates during scan operations
- Detailed article count tracking (total and assessed)
- Improved error handling with specific error messages
- Configurable port through environment variables (default: 5001)
- Enhanced session management with Flask-Session
- Improved CSRF protection and error handling
- Persistent session storage with 7-day lifetime
- Better error messages for session expiration
- Mobile-responsive design improvements
- Dark mode toggle functionality
- Settings page for configuration management
- PDF report generation with download functionality
- Filtering and sorting options for scan results
- GPT response caching system that invalidates only when the prompt changes
- New `get_current_prompt` method in `GPTAgent` class
- Cache management functions: `load_gpt_cache` and `save_gpt_cache`

### Changed
- Restructured feed storage to separate default and custom feeds
- Enhanced feed validation with comprehensive checks
- Improved feed management UI with clear status indicators
- Updated port configuration to use environment variables consistently
- Improved error handling across all endpoints
- Enhanced security with proper CSRF token validation
- Better session persistence across server restarts
- More consistent error response formats
- Modified `fetch_and_process_feeds` to handle dictionary responses from GPT
- Improved error handling in feed processing
- Removed article caching in favor of GPT response caching
- Updated frontend to show real-time progress during scans
- Enhanced progress bar to reflect actual article processing
- Improved error message display in the UI
- Updated rating system from High/Medium/Low to a numerical scale (1-10)
  - 1-3: Low relevance
  - 4-6: Medium relevance
  - 7-10: High relevance
- Updated OpenAI package to version 0.28.1 for better stability
- Simplified README with clearer installation and usage instructions

### Fixed
- Feed management issues with default feed protection
- Custom feed persistence across application updates
- Feed validation error handling and reporting
- Port configuration inconsistencies
- Session expiration issues
- CSRF token validation errors
- Mobile responsiveness on smaller screens
- PDF report download functionality
- Error handling for missing results
- Fixed "No new articles found" error caused by incorrect response parsing
- Resolved rate limiting issues with OpenAI API
- Fixed dictionary response handling in main processing loop
- Fixed progress bar hanging at 90% issue
- Resolved duplicate run_web.py file conflict
- Fixed OpenAI API compatibility issues
- Improved error handling for API responses

## [1.0.0] - 2024-03-20

### Added
- Initial release with basic functionality
- RSS feed scanning and parsing
- GPT-based content analysis
- Basic web interface
- Command-line interface
- Cache management system

## [0.1.0] - 2024-04-22

### Added
- Initial release
- Basic feed processing functionality
- PDF report generation
- Web interface for scanning and viewing results 