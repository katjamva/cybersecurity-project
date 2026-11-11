# Cybersecurity project report

Link to the repository: https://github.com/katjamva/cybersecurity-project

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

This report uses the 2021 OWASP top ten list: https://owasp.org/Top10/

---

## FLAW 1: A01:2021 – Broken Access Control

OWASP 2021 flaw 1 description:
https://top10.owasp.org/2021/A01_2021-Broken_Access_Control/

Flaw source link:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/polls/views.py#L45

### 1.1 Description

The `delete_poll` view only requires the user to be logged in (`@login_required`), but never checks that the user owns the poll. A signed-in user can delete any other user's poll by navigating to, for example, `polls/6/delete` in the URL. This takes them to the form where the poll can be deleted, and they can successfully delete any user's polls. A user should only be able to delete their own polls.

### 1.2 How to fix

Uncomment the whole commented block that starts at the flaw source link. Now the backend checks that the person trying to delete the poll is the owner of that poll. The view will then return 403 Forbidden to anyone trying to view the delete form or delete a poll that isn't theirs.

---

## FLAW 2: A02:2021 – Cryptographic Failures

OWASP 2021 flaw 2 description:
https://top10.owasp.org/2021/A02_2021-Cryptographic_Failures/

Flaw source link:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/config/settings.py#L123

### 2.1 Description

The `PASSWORD_HASHERS` setting in `settings.py` uses `MD5PasswordHasher`, which is based on the MD5 cryptographic hash function. MD5 is considered insecure: in 2004, researchers demonstrated a practical method for generating MD5 collisions [1]. MD5 is very fast, and because of that modern hardware can brute-force MD5 hashes quickly. If an attacker obtains the application's database, they can test guesses from lists of previously leaked passwords against the stored hashes and recover many users' passwords in a short time.

### 2.2 How to fix

Comment out the `PASSWORD_HASHERS` setting provided in the flaw source link. Uncomment the block starting on line 132:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/config/settings.py#L132

The `PASSWORD_HASHERS` setting now lists PBKDF2 first, so it is used to hash new users' passwords. PBKDF2 is salted and deliberately slow, so brute-force attacks become slow and expensive [2]. MD5 is left in the settings so that existing users can log in after the change. Django re-hashes a user's password with PBKDF2 at their next successful login.

---

## FLAW 3: A03:2021 – Injection

OWASP 2021 flaw description:
https://top10.owasp.org/2021/A03_2021-Injection/

Flaw source link:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/polls/views.py#L129

### 3.1 Description

User input from the search is pasted directly into a raw SQL string instead of being sent as a parameter. In the screenshots of flaw 3, we can see that a user can inject raw SQL into the search box. Typing `' UNION SELECT id, password, username, id FROM auth_user --` into the search will show the password hashes, because UNION combines the results of two queries by column position, not by column name. The injected `password` value ends up in the `question_text` column, which is the one the index template displays.


### 3.2 How to fix

Comment out the whole block starting from the flaw source link to line 135:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/polls/views.py#L135

Uncomment the whole block starting from line 142:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/polls/views.py#L142

Now the user input in the search bar is sent to the database as a parameter instead of as raw SQL.

---

## FLAW 4: A07:2021 – Identification and Authentication Failures

OWASP 2021 flaw description:
https://top10.owasp.org/2021/A07_2021-Identification_and_Authentication_Failures/

Flaw source link:
https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/config/settings.py#L184

### 4.1 Description

Login attempts do not have a limit. This makes brute-force attacks possible because of unlimited login attempts.

### 4.2 How to fix

Uncomment the `AUTHENTICATION_BACKENDS` block starting at the flaw source link, and the four `AXES_` settings below it, to enable rate limiting. Axes is already installed. Now the user can try to log in 5 times, and if the 5th try fails, the cool-off time is 1 hour. Further login attempts are blocked for 1 hour, even with the correct password.

---

## FLAW 5: A09:2021 – Security Logging and Monitoring Failures

OWASP 2021 flaw description:
https://top10.owasp.org/2021/A09_2021-Security_Logging_and_Monitoring_Failures/

Flaw source links:

- 1/2: https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/config/settings.py#L65
- 2/2: https://github.com/katjamva/cybersecurity-project/blob/8cf855b94f4192a6d26502b0364e525bbb24bd0c/src/polls/views.py#L26

### 5.1 Description

Nothing logs successful or failed login attempts. Logging and monitoring make it possible to notice suspicious activity and attacks. When the logging and monitoring data is stored, investigations of successful attacks are possible.

### 5.2 How to fix

- Fix 1/2: uncomment the commented block starting from the 1/2 flaw source link.
- Fix 2/2: uncomment the commented block starting from the 2/2 flaw source link.

Now Django's built-in logging module is able to perform system logging. Depending on the developer's needs, different log levels can be configured, along with what exactly needs to be logged. This fix logs successful and failed login attempts, so there is a record of who logged in, when, and from where (IP address).

---

## Sources

[1] https://www.hakatemia.fi/en/courses/cryptography/md5-hash-a-broken-classic

[2] https://www.hakatemia.fi/courses/kryptografia/pbkdf2-bcrypt-scrypt-ja-argon2 (in Finnish)