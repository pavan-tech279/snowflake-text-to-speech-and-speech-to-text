# Text to Speech & Speech to Text in Snowflake
This demo repository explains how to deploy text-to-speech and speech-to-text capabilities in Snowflake using Snowflake's model registry.
Afterwards you can use them in Snowflake Notebooks and Streamlit.
The app, notebooks and all model artifacts are entirely hosted in Snowflake, fulfilling the highest security and governance standards.

![Cortex Agents](resources/header.jpg)

## Streamlit App
The app let's you explore the deployed text-to-speech and speech-to-text capabilities in an interactive way.
It also allows you to have a conversation with an LLM by actually talking to it and listen to its responses.

Here's a short demo video of the app:  
<DEMO VIDEO>

## Text to Speech Models
The text-to-speech functionality is powered by models from Facebook's [Massive Multilingual Speech project](https://research.facebook.com/publications/scaling-speech-technology-to-1000-languages/).
These model's either run locally inside of the Streamlit App or they connect to inference services that were setup earlier.

The following models are available inside SiS:
| Model | Language |
|:--------------------:|:----------:|
| facebook/mms-tts-eng | English    |
| facebook/mms-tts-deu | German     |
| facebook/mms-tts-fra | French     |
| facebook/mms-tts-nld | Dutch      |
| facebook/mms-tts-hin | Hindi      |
| facebook/mms-tts-kor | Korean     |
| facebook/mms-tts-pol | Polish     |
| facebook/mms-tts-por | Portuguese |
| facebook/mms-tts-rus | Russian    |
| facebook/mms-tts-spa | Spanish    |
| facebook/mms-tts-swe | Swedish    |

## Speech to Text Models
The speech-to-text functionality is powered by Whisper models.
These model's either run locally inside of the Streamlit App or they connect to inference services that were setup earlier.

The following models are available inside SiS:
| Size           | Parameters | English-only | Multilingual |
|:--------------:|:----------:|:------------:|:------------:|
| tiny           | 39 M       | ✓            | ✓            |
| base           | 74 M       | ✓            | ✓            |
| small          | 244 M      | ✓            | ✓            |
| medium         | 769 M      | ✓            | ✓            |
| large-v3-turbo | 809 M      | x            | ✓            |

## Requirements
* A Snowflake account  

Here you can get a free [Snowflake Trial Account](https://signup.snowflake.com/).

> [!IMPORTANT]
> If you want to deploy the text-to-speech and speech-to-text models as inference services in Snowpark Container Services, you need a non-trial Snowflake account.

## Setup
```sql

USE ROLE ACCOUNTADMIN;

-- Create warehouse
CREATE OR REPLACE WAREHOUSE AUDIO_INTERFACE_WH WITH WAREHOUSE_SIZE='MEDIUM' WAREHOUSE_TYPE = 'SNOWPARK-OPTIMIZED';

-- Create fresh database
CREATE OR REPLACE DATABASE AUDIO_INTERFACING_DEMO;

-- Create the API integration with Github
CREATE OR REPLACE API INTEGRATION GITHUB_INTEGRATION_MICHAEL_GORKOW
    api_provider = git_https_api
    api_allowed_prefixes = ('https://github.com/michaelgorkow/')
    enabled = true
    comment='Git integration with Michael Gorkows Github Repository.';

-- Create the integration with the Github demo repository
CREATE GIT REPOSITORY GITHUB_REPO_AUDIO_INTERFACES
	ORIGIN = 'https://github.com/michaelgorkow/snowflake-text-to-speech-and-speech-to-text' 
	API_INTEGRATION = 'GITHUB_INTEGRATION_MICHAEL_GORKOW' 
	COMMENT = 'Github Repository from Michael Gorkow with a demo for text-to-speech and speech-to-text';


-- Run the installation of the demo assets
-- If you want to automatically run the notebooks to deploy the models, set EXECUTE_NOTEBOOKS => TRUE
EXECUTE IMMEDIATE FROM @AUDIO_INTERFACING_DEMO.PUBLIC.GITHUB_REPO_AUDIO_INTERFACES/branches/main/setup.sql
  USING (EXECUTE_NOTEBOOKS => FALSE) DRY_RUN = FALSE;
```

## Objects created in your Snowflake Account
You will find a new database in your account called `AUDIO_INTERFACING_DEMO` that contains all demo artifacts:
 
| Object                          | Description                                                |
|----------------------------------|------------------------------------------------------------|
| AUDIO_INTERFACES_APP         | Streamlit App that lets you play with the deployed models  |
| [TEXT_TO_SPEECH_NOTEBOOK](notebooks/TEXT_TO_SPEECH_NOTEBOOK.ipynb)      | Notebook for deploying the text-to-speech models           |
| [SPEECH_TO_TEXT_NOTEBOOK](notebooks/SPEECH_TO_TEXT_NOTEBOOK.ipynb)      | Notebook for deploying the speech-to-text models           |
| MODEL_REGISTRY                 | Schema that stores your models                             |