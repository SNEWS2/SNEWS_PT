"""
Easy handle remote commands


Melih Kara, kara@kit.edu
"""
import os
import time
from datetime import UTC, datetime

import click
from hop import Stream
from hop.io import StartPosition
from hop.models import JSONBlob


def test_connection(firedrill=True, start_at="LATEST", patience=8):
    """ test the server connection
        It should prompt your whether the
        coincidence script is running in the server

        Parameters
        ----------
        start_at : str
            Where hop starts looking for messages can either be  "LATEST" or "EARLIEST"
        patience : int
            Seconds to wait before the check

        Returns
        -------
            None

    """

    default_connection_topic = "kafka://kafka.scimma.org/snews.connection-testing"
    connection_broker = os.getenv("CONNECTION_TEST_TOPIC", default_connection_topic)
    stamp_time = datetime.now(UTC).isoformat()
    message = {'_id': '0_test-connection',

               'time': stamp_time,
               'status': 'sending',
               'meta':{}}
    if firedrill:
        topic = os.getenv("FIREDRILL_OBSERVATION_TOPIC")
    else:
        topic = os.getenv("OBSERVATION_TOPIC")

    _start_at = StartPosition.LATEST if start_at == "LATEST" else StartPosition.EARLIEST
    substream = Stream(until_eos=True, auth=True, start_at=_start_at)
    pubstream = Stream(until_eos=True, auth=True)
    click.secho(f"\n> Testing your connection.\n> Sending to {topic}\n"
                f"> Expecting from {connection_broker}. \n"
                f"> Going to wait {patience} seconds before checking for confirmation...\n")

    # start_time = datetime.utcnow()
    confirmed = False
    message_expected = message.copy()
    message_expected["status"] = "received"

    with pubstream.open(topic, "w") as ps, substream.open(connection_broker, "r") as ss:
        ps.write(JSONBlob(message))
        # while (datetime.utcnow() - start_time) < timedelta(seconds=wait):
        time.sleep(patience)
        for read in ss:
            read = read.content
            if read == message_expected:
                read_time = click.style(read['time'], fg='green', bold=True)
                click.echo(f"You have a connection to the server at {read_time}")
                confirmed=True
                break
            else: # if there is no else: continue statement, it does not work
                continue
    if not confirmed:
        click.secho(f"\tWaited for {patience} sec and checked from {start_at},"
                    f" couldn't get a confirmation"
                    f"\n\tMaybe increase timeout and try again.", fg='red', bold=True)
        return False
    return True


def write_hb_logs(detector_name=None, admin_pass=None, firedrill=True):
    """ Ask server to print the heartbeat logs on the server as standard output
        later admins can see them remotely. Requires admin password

        Parameters
        ----------
        detector_name : str
            Name of the detector requesting the write operation
        admin_pass : str
            Simple password as a string
        firedrill : bool
            Whether to use the firedrill broker

    """
    passw = admin_pass or os.getenv("ADMIN_PASS", "NO_AUTH")
    detector_name = detector_name or os.getenv("DETECTOR_NAME")
    message = {'_id': '0_display-heartbeats',
               'pass': passw,
               'detector_name':detector_name,
               'meta':{}}
    topic = os.getenv("FIREDRILL_OBSERVATION_TOPIC") if firedrill else os.getenv("OBSERVATION_TOPIC")
    pubstream = Stream(until_eos=True, auth=True)

    with pubstream.open(topic, "w") as ps:
        ps.write(message)
    logslink = "> https://www.physics.purdue.edu/snews/logs/"
    click.secho(f"> Requested logs. If you have rights, go to remote Purdue server logs\n{logslink}\n",
                fg='blue', bold=True)


def reset_cache(detector_name=None, admin_pass=None, firedrill=True, is_test=True):
    """ If authorized, drop the current cache at the server

        Parameters
        ----------
        detector_name : str
            Name of the detector
        admin_pass : str
            Simple password as a string
        firedrill : bool
            Whether to use the firedrill broker

    """
    passw = admin_pass or os.getenv("ADMIN_PASS", "NO_AUTH")
    detector_name = detector_name or os.getenv("DETECTOR_NAME")
    message = {'_id': '0_hard-reset',
               'pass': passw,
               'detector_name':detector_name,
               'is_test': is_test,
               'meta':{}}

    topic = os.getenv("FIREDRILL_OBSERVATION_TOPIC") if firedrill else os.getenv("OBSERVATION_TOPIC")
    pubstream = Stream(until_eos=True, auth=True)

    with pubstream.open(topic, "w") as ps:
        ps.write(message)
        click.secho(f"> Requesting to Reset the cache. If you have rights, cache will be reset", fg='blue', bold=True)


def change_broker(brokername, detector_name=None, admin_pass=None, firedrill=True):
    """ If authorized, server changes the broker
        === Not implemented yet ===
        brokername : str
            name of the broker to replace
        detector_name : str
            Name of the detector
        admin_pass : str
            Simple password as a string
        firedrill : bool
            Whether to use the firedrill broker

    """
    passw = admin_pass or os.getenv("ADMIN_PASS", "NO_AUTH")
    detector_name = detector_name or os.getenv("DETECTOR_NAME")
    message = {'_id': '0_broker-change',
               'pass': passw,
               'detector_name': detector_name,
               'new_broker':brokername,
               'meta':{}}

    current_topic = os.getenv("FIREDRILL_OBSERVATION_TOPIC") if firedrill else os.getenv("OBSERVATION_TOPIC")
    pubstream = Stream(until_eos=True, auth=True)

    with pubstream.open(current_topic, "w") as ps:
        ps.write(message)
        click.secho(f"> Requesting to change the broker. If you have rights, broker will be changed", fg='blue', bold=True)


def get_feedback(detector_name=None, email_address=None, firedrill=True):
    """ Get heartbeat feedback by email
        For a given detector, if your email is registered
        We are going to send that email address(es) an email with feedback from last 24hours.
        multiple email addresses are allowed with a semicolon delimiter (;)

        Parameters
        ----------
        detector_name : str
            Name of your detector
        email_address : str or list
            Registered e-mail adress(es)
        firedrill : bool
            Whether to use firedrill broker or not

    """
    detector_name = detector_name or os.getenv("DETECTOR_NAME")
    email_address = email_address or input("\t> Your registered email address: ")
    message = {'_id': '0_Get-Feedback',
               'email': email_address,
               'detector_name': detector_name,
               'meta': {}}
    topic = os.getenv("FIREDRILL_OBSERVATION_TOPIC") if firedrill else os.getenv("OBSERVATION_TOPIC")
    pubstream = Stream(until_eos=True, auth=True)
    with pubstream.open(topic, "w") as ps:
        ps.write(message)

    click.secho(f"Heartbeat Feedback is requested! Expect an email from us!")
