import os

from dotenv import load_dotenv

envpath = os.path.join(os.path.dirname(__file__), 'auxiliary/test-config.env')
load_dotenv(envpath)
