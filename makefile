.PHONY: runserver

runserver:
	source venv/Scripts/activate && cd homeservice && python manage.py runserver
