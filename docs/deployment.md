## Local deployment with `flask run`

1. Navigate to the main directory of the project (`/Online-Aquarium`).
2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```
3. Set the `FLASK_APP` environment variable:

    ```bash
    export FLASK_APP=server
    ```
4. Run the application:

    ```bash
    flask run
    ```

## DigitialOcean App Platform deployment with `gunicorn`

1. Make a `requirements.txt` file of the environment:

    ```bash
    pip list --format=freeze > requirements.txt
    ```
    We have to do it this way because of this thing I found on [StackOverflow](https://stackoverflow.com/questions/62885911/pip-freeze-creates-some-weird-path-instead-of-the-package-version).
2. Set up a new "App Platform" resource on DigitalOcean.
    2.1. I set it up to autodeploy from the main branch of the quoctran98/Online-Aquarium repository.
