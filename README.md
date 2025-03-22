# Home Service Django App

A simple Django-based web application that connects users with home service providers (electricians, plumbers, carpenters, etc.).

## Features

- 🏠 **Home Page**: Users can explore available services.
- 🔧 **Service Providers**: View a list of professionals.
- 📅 **Booking System**: Users can book services.
- 🔄 **Server-Side Rendering**: All pages are rendered with Django templates.

## Installation Guide

### 1️⃣ Prerequisites

Make sure you have installed:

- Python (latest version recommended)
- Git
- Virtual environment (optional but recommended)

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/jeanclaudegeagea/HomeServiceDjango.git
cd HomeServiceDjango
```

### 3️⃣ Set Up a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 4️⃣ Install Dependencies

```bash
pip install django
```

### 5️⃣ Move into the homeservice folder

```bash
cd homeservice
```

### 6️⃣ Apply Migrations

```bash
python manage.py migrate
```

### 7️⃣ Run the Development Server

```bash
python manage.py runserver
```

Now, open your browser and go to:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Project Structure

```
HomeServiceDjango/
│── homeservice/  # Main Django project
│   │── settings.py  # Project settings
│   │── urls.py  # URL configurations
│   │── wsgi.py  # WSGI entry point
│
│── core/  # Main app
│   │── migrations/  # Database migrations
│   │── templates/core/  # HTML templates
│   │── views.py  # Views logic
│   │── urls.py  # Routes for the app
│
│── manage.py  # Django management script
│── README.md  # Project documentation
```

## Contributing

1. Fork the repository 🍴
2. Create a new branch 🔧
3. Commit your changes ✅
4. Push to GitHub 🚀
5. Open a pull request 📩

## License

This project is **open-source** and free to use.

---

📩 For any issues, feel free to open an issue on GitHub!
