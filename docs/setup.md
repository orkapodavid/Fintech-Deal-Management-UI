# Setup & Installation Guide

This guide details how to set up, run, and deploy the Deal Management application.

## Prerequisites

*   **Python**: 3.8 or higher
*   **Node.js**: 16.14.0 or higher (required for Reflex frontend)
*   **Reflex**: Installed via pip (see below)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Reflex project:**
    ```bash
    reflex init
    ```

## Running the Development Server

To start the app in development mode with hot-reloading:

```bash
reflex run
```

*   The frontend will be available at: `http://localhost:3000`
*   The backend server runs on: `http://localhost:8000`

## Configuration

*   **Environment Variables**: Currently, the app relies on internal defaults and mock data. No `.env` file is strictly required for local dev.
*   **Tailwind CSS**: Configured in `rxconfig.py` via `rx.plugins.TailwindV3Plugin()`. Custom styles can be added in standard Tailwind fashion.

## Common Issues & Debugging

*   **Port Conflicts**: Ensure ports 3000 and 8000 are free.
    *   *Fix*: Kill processes on these ports or change ports using `reflex run --frontend-port <port> --backend-port <port>`.
*   **Database Errors**: The current app uses in-memory lists (`self.deals` in `DealState`). If you see persistence errors, ensure you are not expecting data to survive a server restart.
*   **Missing Dependencies**: If `reflex` command is not found, ensure your virtual environment is active.
