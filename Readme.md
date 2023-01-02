# Ecommerce Website

This is an Ecommerce website which has end to end functionalities

## Main features

1. Create User Account.
2. Adding products to cart.
3. Payment gateway.
4. Order Confirmation Email.
5. Product review system.
4. CMS to maintain products,details,Images,stock etc.

## Installation and Usage

First clone the repository from Github and switch to the new directory:

```bash
git clone git@github.com/TOPSinfo/python_ecom_demo.git
```

Activate the virtualenv for your project.

Install project dependencies:
```bash
pip install -r requirements.txt
```

Then simply apply the migrations:

```bash
python manage.py migrate
```

You can now run the development server:

```bash
python manage.py runserver
```