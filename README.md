# Inventory Management Web Application

A Flask-based inventory management application for tracking products across multiple warehouse locations. This application enables users to add, edit, and view products, manage locations, track product movements, and view up-to-date inventory balances across warehouses.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [License](#license)

## Features

- Add, update, and delete products and locations
- Track movements of products between locations
- Real-time inventory balance report
- User-friendly interface for efficient management
- Separate views for products, locations, movements, and balance overview

## Technologies

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Testing**: Postman for API endpoint testing

## Installation

### Prerequisites

- Python 3.7 or higher
- Flask
- SQLite

### Steps

1. **Clone the Repository**
    ```bash
    cd inventory-management-app
    ```

2. **Set Up Virtual Environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Run the Application**
    ```bash
    python .\app.py
    ```
    The app will be accessible at `http://127.0.0.1:5000/`.

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:5000/`.
2. Use the navigation links to:
    - View products, locations, and product movements.
    - Add new entries or edit/delete existing entries.
    - Check the balance report to get an overview of current stock across locations.

## Database Schema

### Tables

1. **Product**: Stores product details and quantity.
2. **Location**: Stores warehouse location details.
3. **ProductMovement**: Tracks movement of products between locations.
4. **Balance**: Maintains a report of product quantities per location.
