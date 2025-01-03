
import json
import os
import sys
import time
from pathlib import Path

import click
import inquirer
from snews.models.messages import CoincidenceTierMessage

from snews_pt.messages import Publisher
from snews_pt.remote_commands import reset_cache


def try_scenarios(fd_mode: bool = False, is_test: bool = False):
    topic = os.getenv("OBSERVATION_TOPIC")
    if fd_mode:
        topic = os.getenv("FIREDRILL_OBSERVATION_TOPIC")

    if not is_test:
        click.secho("This script is only for testing purposes, and uses past neutrino times.\n"
                    "We are running the scenarios in test mode", fg='red', bold=True)
        is_test = True

    with open(Path(__file__).parent / "scenarios.json") as json_file:
        coincidence_scenarios = json.load(json_file)

    scenarios_labels = list(coincidence_scenarios.keys())

    try:
        questions = [
            inquirer.Checkbox(
                'scenarios',
                message=click.style(
                    " Which scenario(s) would you like to run next?",
                    bg='yellow',
                    bold=True
                ),
                choices=scenarios_labels + ["finish & exit", "restart cache"],
            )
        ]

        while True:
            try:
                answers = inquirer.prompt(questions)
                for scenario in answers['scenarios']:
                    if scenario == "finish & exit":
                        click.secho("Terminating.")
                        sys.exit()
                    elif scenario == "restart cache":
                        reset_cache(firedrill=fd_mode, is_test=is_test)
                        print('> Cache cleaned\n')
                    else:
                        click.secho(f"\n>>> Testing {scenario}", fg='yellow', bold=True)

                        pub = Publisher(kafka_topic=topic, auth=True)
                        for evt in coincidence_scenarios[scenario]:  # send one by one and sleep in between
                            print(evt, "\n\n")
                            msg = CoincidenceTierMessage(
                                detector_name=evt['detector_name'],
                                neutrino_time_utc=evt['neutrino_time_utc'],
                                p_val=evt['p_val'],
                                is_test=True)  # allow future timestamps

                            pub.add_message(msg)
                            time.sleep(1)

                        pub.send()
                        print(f'> {len(coincidence_scenarios[scenario])} messages sent.')

                        # clear cache after each scenario
                        reset_cache(firedrill=fd_mode, is_test=is_test)
                        print('> Cache cleaned\n')

            except KeyboardInterrupt:
                break
    except Exception as e:
        print("Something went wrong\n", e, "\nTry manually submitting messages :/")
