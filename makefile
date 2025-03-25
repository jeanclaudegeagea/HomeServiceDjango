.PHONY: runserver

runserver:
	venv\Scripts\Activate && cd homeservice && python manage.py runserver
