
import json, click, time, sys
from os import path as osp
from snews_pt.snews_pub import SNEWSTiersPublisher, Publisher
fd_mode = True if sys.argv[1].lower() == "true" else False

with open(osp.join(osp.dirname(__file__), "scenarios.json")) as json_file:
    data = json.load(json_file)

try:
    import inquirer
    questions = [
    inquirer.Checkbox('scenarios',
                    message=click.style(" Which scenario(s) would you like to run next?", bg='yellow', bold=True),
                    choices=list(data.keys())+list(["finish & exit"]),
                )
    ]

    while True:
        try:
            answers = inquirer.prompt(questions)
            for scenario in answers['scenarios']:
                if scenario=="finish & exit":
                    click.secho("Terminating.")
                    sys.exit()
                click.secho(f"\n>>> Testing {scenario}", fg='yellow', bold=True)
                messages = data[scenario]
                for msg in messages: # send one by one and sleep in between
                    msg["testing"] = "this is a test"
                    SNEWSTiersPublisher(**msg, firedrill_mode=fd_mode).send_to_snews()
                    time.sleep(1)
                    # clear cache after each scenario
                with Publisher() as pub:
                    pub.send([{'_id': '0_hard-reset_', 'pass':'very1secret2password', 'detector_name':'TEST'}])
                    print('> Cache cleaned\n')

        except KeyboardInterrupt:
            break
except Exception as e:
    print("Something went wrong\n", e, "\nTry manually submitting messages :/")
#