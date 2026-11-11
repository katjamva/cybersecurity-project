# Cybersecurity Base project I

Submission for Cybersecurity Base project I: https://cybersecuritybase.mooc.fi/module-3.1

Starter website created following Django's "Writing your first Django app" tutorial:
https://docs.djangoproject.com/en/6.1/intro/

Project report with detailed flaw descriptions and fixing instruction:
[REPORT.md](REPORT.md)

Screenshots of flaws before and after applying fixes:
[screenshots/](screenshots/)

## About

Simple polls app with the following features:

- User registration and login
- Users can create and delete polls
- Anyone can view polls, vote on them and see the vote results
- Search bar to search polls


## Installation instructions

1. Make sure Python 3.12.3 or newer is installed.
2. Clone the repository to your chosen location.
3. Go to the `src/` folder, where `manage.py` and `requirements.txt` are.
4. Install the dependencies (Django and django-axes) with `pip install -r requirements.txt`.
5. Run `python manage.py migrate` to create the database.
6. Start the server by running `python manage.py runserver`.
   - If `python` or `pip` doesn't work, try `python3` or `pip3`.
7. Navigate to the server's address in your browser (http://127.0.0.1:8000/ by default).
8. The app is ready!
