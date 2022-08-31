# limerickation
# limerickation

To set up limerickation, follow the below steps:

1. Clone the repository locally

2. Create a virtual environement:


    Run the following commands from the root folder to create a virtual environment and install all the packages and dependencies needed to run the application:

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt


3. There are seven environment variables that need to be set in the limericks/settings folder:

- In settings.py:

  **SECRET_KEY** – Django secret key. You can run the below code to get a secret key:
  
  from django.core.management.utils import get_random_secret_key
  
  print(get_random_secret_key())

  **DEBUG** – True or False variable to set the environment to Debug (and see error codes) or not
  
  **ALLOWED_HOSTS** – List to represent the domains that the Django site can serve. 
  
  For example, if running locally, can set to “localhost 127.0.0.1”. 
  The list should be a string and each allowed host should be separated by a space.

- In storage.py:

  **AWS_ACCESS_KEY**
  **AWS_SECRET_ACCESS_KEY**
  **AWS_STORAGE_BUCKET_NAME**
  
  This application is set up to store its static files in an AWS S3 bucket for optimisation reasons. 
  If you do not want to use AWS, you do not need to set this environment variables. 
  Simply uncomment line 8 of settings/storage.py and comment out lines 10 onwards.


- In custom.py:

  **WEB_APP_MODELS** – This is a true or false variable that tells the application whether to use GPT-2 pipelines for text generation or GPT-2 with PyTorch features. 
  Setting to True will lead to faster results but the quality of the limericks might be lowered.

  Set your environment variables by running the following commands from the terminal:

  export SECRET_KEY=yourscretkey
  
  export DEBUG=True
  
  export ALLOWED_HOSTS="localhost 127.0.0.1"
  
  export WEB_APP_MODELS=False

4. Run the below commands to create the appropriate tables in the database and create singleton objects needed for the model to work.

    python manage.py makemigrations

    python manage.py migrate

    python manage.py start_up

5. You are now ready to run the server and interact with the application to generate limericks

    python manage.py runserver
    

Note: when cloning the repository, you will see that there is a folder limerines/my_data that contains pickle files. 

These pickle files can be generated from the below repo:

https://github.com/iaron1895/limerickation-set-up
  
