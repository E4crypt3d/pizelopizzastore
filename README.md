# Pizelo Pizza Store
Pizelo Pizza Store is a web-based pizza ordering system that allows customers to select and order pizzas online. The application has been developed using `Django`, a Python web framework, `Django Channels`, `HTMX`.

## Features
- Users can create an account, log in, and manage their profile.
- Users can browse the menu of available pizzas, choose the size and toppings they want, and add them to their cart.
- Users can view their cart and update the quantity or remove items.
- Users can place an order and receive an email confirmation.
- Admin users can add, edit, and delete pizzas from the menu.

## Installation
To install and run Pizelo Pizza Store on your local machine, follow these steps:

1. Clone the repository: `git clone https://github.com/E4crypt3d/pizelopizzastore.git`
2. Navigate to the project directory: `cd pizelopizzastore`
3. Install the required packages: `pip install -r requirements.txt`
4. Set up the database: `python manage.py migrate`
5. Create an admin user: `python manage.py createsuperuser`
6. Run the development server: `python manage.py runserver`
7. You should now be able to access the application at `http://localhost:8000/`.

## Contributing
*Contributions to Pizelo Pizza Store are welcome and encouraged! To contribute, please follow these steps:*

- Fork the repository.
- Create a new branch for your changes.
- Make your changes and commit them with descriptive commit messages.
- Push your changes to your forked repository.
- Submit a pull request to the main repository with a clear description of your changes.
