# Price Tracker

A Django web application that tracks product prices over time by scraping information from online retailers.

## Features

- **Product Tracking**: Add products by their URL and monitor price changes
- **Price History**: View historical price data with visual charts
- **Automatic Updates**: Refresh product information to keep prices current
- **Duplicate Prevention**: Intelligent handling of duplicate product URLs
- **Clean Interface**: User-friendly product listings and detailed views

## Project Structure

The application uses Django's MVT (Model-View-Template) architecture:

- **Models**: Product and PriceHistory for data storage
- **Views**: List, detail, add, delete, and update functionality
- **Templates**: Clean HTML templates for displaying product information

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/price-tracker.git
   cd price-tracker
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

### Adding Products

1. Navigate to the "Add Product" page
2. Enter the URL of the product you want to track
3. Submit the form to scrape and save product data

### Viewing Products

- The main page displays a list of all tracked products
- Each product shows its current price and price range
- Click on any product to view its detailed information

### Price History

- The detail page for each product includes a price history chart
- Historical prices are displayed in chronological order
- Visual representation helps identify price trends

### Updating Products

- Use the update function to refresh all product information
- Each update creates a new price history entry

## Technical Details

- **Web Scraping**: Custom utility functions extract product data from websites
- **Data Storage**: Product information and price history are stored in the database
- **Visualization**: Price history is displayed using chart libraries
- **Transaction Management**: Database operations are wrapped in transactions for data integrity

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License



This project is licensed under the [![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
