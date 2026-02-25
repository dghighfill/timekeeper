# Soccer Timekeeper App

A Streamlit web application that enables match administrators to create and manage 90-minute soccer match timers, while allowing spectators to discover and follow matches through QR code scanning.

## Project Structure

```
soccer-timekeeper-app/
├── data/               # Storage directory for match and user data
├── src/                # Source code for application components
├── tests/              # Unit and property-based tests
├── config.py           # Application configuration constants
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore patterns
└── README.md          # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Application constants are defined in `config.py`:
- Timer duration: 90 minutes (5400 seconds)
- Green soccer theme colors
- Storage paths and settings
- QR code generation parameters

## Running the Application

```bash
streamlit run app.py
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Features

- Create 90-minute soccer match timers
- Generate QR codes for match sharing
- Scan QR codes to follow matches
- Role-based access control (Admin vs Spectator)
- Real-time timer synchronization
- Persistent storage across page refreshes
- Green soccer-themed UI
