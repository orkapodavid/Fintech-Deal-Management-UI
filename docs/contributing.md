# Contributing Guide

Thank you for your interest in contributing to the Deal Management App! This document provides guidelines for setting up your environment and submitting contributions.

## Development Workflow

1.  **Fork and Clone**: Fork the repository and clone it locally.
2.  **Environment Setup**: Follow the [Setup Guide](setup.md) to create a virtual environment and install dependencies.
3.  **Branching**: Create a new branch for your feature or bug fix.
    ```bash
    git checkout -b feature/my-new-feature
    ```
4.  **Coding Standards**:
    *   **Style**: We use [Black](https://github.com/psf/black) for code formatting. Please run `black .` before committing.
    *   **Linting**: We recommend using `ruff` or `pylint` to catch common errors.
    *   **Type Hinting**: Use Python type hints strictly, especially in State classes and Components.

## Testing

*   Currently, the project lacks a comprehensive test suite (see `IMPROVEMENTS.md`).
*   **Requirement**: New features *must* include unit tests if applicable. Place tests in `tests/`.
*   **Running Tests**:
    ```bash
    pytest
    ```

## Pull Request Process

1.  Ensure your code builds and runs locally (`reflex run`).
2.  Update documentation if you change state logic or UI components.
3.  Submit a Pull Request with a clear description of changes.

## Reporting Bugs

Please use the GitHub Issues tracker to report bugs. Include:
*   Steps to reproduce.
*   Expected vs. actual behavior.
*   Screenshots if UI-related.
