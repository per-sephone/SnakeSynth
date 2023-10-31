# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.5] - 2023-10-31
### Added
- Added docstrings to the ADSREnvelope class and methods (adsr.py).
- Added type hints to variables and methods in ADSREnvelope class (adsr.py).
### Changed
- Updated variable names in adsr.py to improve readability.

## [1.1.4] - 2023-10-27
### Added
- Added more detailed docstrings in form.py
- Added type hints to variables in form.py
### Changed
- Refactored form.py by moving portions of code into new functions


## [1.1.3] - 2023-10-25
### Added
- Added .gitignore to keep __pycache__ and env directories out of the repository

### Removed
- Removed existing __pycache__ directories from the repository

## [1.1.2] - 2023-10-25
### Added
- Added CHANGELOG.md for keeping track of changes in the repository

## [1.1.1] - 2023-10-25
### Added
- Added dev-requirements.txt

### Updated
- Updated README.md to include instructions for creating a development py environment
- Updated requirements.txt

## [1.1.0] - 2023-10-21
### Removed
- Removed the base, mid, and treble knobs from the ui

### Changed
- Moved the thread class into a separate file. 
- Updated naming in midi_detect

## [1.0.1] - 2023-10-21
### Changed
- Used black to lint all python src and test files.

## [1.0.0] - 2023-10-12
### Changed
- Updated README for Code Reading and Review to include new contributers and documentation