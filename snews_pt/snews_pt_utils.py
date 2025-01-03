"""
Utility tools for snews_pt
"""
import json
import os
from collections import namedtuple

import click
import dotenv
from dotenv import load_dotenv

from .core.logging import getLogger

log = getLogger(__name__)
default_detector_file = os.path.dirname(__file__) + "/auxiliary/detector_properties.json"


def set_env(env_path=None):
    """ Set environment parameters

    Parameters
    ----------
    env_path : str, (optional)
        path for the environment file.
        Use default settings if not given

    """
    dirname = os.path.dirname(__file__)
    default_env_path = dirname + '/auxiliary/test-config.env'
    env = env_path or default_env_path
    load_dotenv(env)


def retrieve_detectors(detectors_path=default_detector_file):
    """ Retrieve the name-ID-location of the participating detectors.

        Parameters
        ----------
        detectors_path : str, optional
            path to detector properties. File needs to be in JSON format

        Returns
        -------
        None

    """
    if not os.path.isfile(detectors_path):
        os.system(f'python {os.path.dirname(__file__)}/auxiliary/make_detector_file.py')

    with open(detectors_path) as json_file:
        detectors = json.load(json_file)

    # make a namedtuple
    Detector = namedtuple("Detector", ["name", "id", "location"])
    for k, v in detectors.items():
        detectors[k] = Detector(v[0], v[1], v[2])
    return detectors


def isnotebook():
    """ Tell if the script is running on a notebook

    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def display_gif():
    """ Some fun method to display an alert gif
        If running on notebook.

    """
    if isnotebook():
        from IPython.display import HTML, display
        giphy_snews = "https://raw.githubusercontent.com/SNEWS2/hop-SNalert-app/snews2_dev/hop_comms/auxiliary/snalert.gif"
        display(HTML(f'<img src={giphy_snews}>'))


def set_name(detector_name='TEST', _return=False):
    """ set your detector's name.
    Messages sent with detector_name="TEST" will be ignored at the server
    Alerts can still be subscribed and listened as "TEST"

    """

    envpath = os.path.join(os.path.dirname(__file__), 'auxiliary/test-config.env')
    load_dotenv(envpath)
    detectors = list(retrieve_detectors().keys())
    if detector_name=="TEST":
        if int(os.getenv("HAS_NAME_CHANGED")) == 0:
            for i,d in enumerate(detectors):
                click.secho(f"[{i:2d}] {d}")
            inp = input(click.secho("Please put select your detector's index\n", bold=True))
            detector_name = detectors[int(inp)]
            os.environ["DETECTOR_NAME"] = detector_name
            os.environ["HAS_NAME_CHANGED"] = "1"
            dotenv.set_key(envpath, "DETECTOR_NAME", os.environ["DETECTOR_NAME"])
            dotenv.set_key(envpath, "HAS_NAME_CHANGED", os.environ["HAS_NAME_CHANGED"])
        else:
            detector_name = os.environ["DETECTOR_NAME"]
    else:
        if not detector_name in detectors:
            raise KeyError(f"{detector_name} is not a valid detector. \nChoose from {detectors}")
        os.environ["DETECTOR_NAME"] = detector_name
        os.environ["HAS_NAME_CHANGED"] = "1"
        dotenv.set_key(envpath, "DETECTOR_NAME", os.environ["DETECTOR_NAME"])
        dotenv.set_key(envpath, "HAS_NAME_CHANGED", os.environ["HAS_NAME_CHANGED"])
    if _return:
        return detector_name
    else:
        click.secho(f'You are {os.environ["DETECTOR_NAME"]}')

