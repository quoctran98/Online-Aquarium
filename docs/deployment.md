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
    2.2 Add the run command: `gunicorn --workers 4 --threads 6 --preload --worker-tmp-dir /dev/shm appserver:gunicorn_app`
    2.3 Add enviroment variables described in `helper.py`. These should include:
        - `ENVIRONMENT` : str
        - `FLASK_SECRET_KEY` : str
        - `SESSION_FILE_DIR` : str

        - `MONGODB_CONNECTION_STRING` : str
        - `USERS_DATABASE` : str

        - `S3_AQUARIUM_SAVE_DIR` : str
        - `S3_STORE_SAVE_DIR` : str
        - `S3_BUCKET_NAME` : str
        - `S3_ACCESS_KEY` : str
        - `S3_SECRET_KEY` : str

        - `APP_WIDTH` : int
        - `APP_HEIGHT` : int