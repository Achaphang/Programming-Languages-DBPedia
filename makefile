FLASK=/home/evan/.local/bin/flask

run:
	env FLASK_APP=backend/main.py FLASK_ENV=development $(FLASK) run

prod:
	env FLASK_APP=backend/main.py FLASK_ENV=product $(FLASK) run
