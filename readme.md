## Talk to Table

Talk to Table lets you upload a data table (in CSV format) and interact with it by "talking" to it in natural language (currently by typing in a text box).  It uses AI on the back-end (using the OpenAI rest api) to convert your natural language into a SQL statement that can extract and make changes to the data table.

This GitHub project is the backend python server code that handles the upload file and talk input requests.  The front-end code will be published separately at a later date.

URL for this app is: [link](https://olhpeters.github.io/talktotable)


### Quick Start

First start up your virtual environment

    pipenv shell

Show your dependencies

    pip list

Once the dependencies are loaded, you will need to add in the configuration using environment variables.  The project is bundled with the python-dotenv library that lets you use a ".env" file in the root directory to place your key-value pairs.  Take the sample.env file and rename it to ".env" and make your configuration modifications there.

The main configuration is the OpenAI api token used to communicate with their service (for the text to SQL conversion).

You can now start the app using uvicorn:

Start up server

    uvicorn main:app --reload


### Future Improvements

- Support for XLS files
- speech to text input
- Authentication
