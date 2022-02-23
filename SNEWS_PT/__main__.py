""" CLI for snews_pt
    Right now publish method does not allow extra arguments.
    While this might be the desired use. I think it should not fail to publish, rather
    - either mark the extra columns and publish, or
    - split these columns, publish the fixed template, and report back to user.
    Manipulations in the publish class can be made see
    https://stackoverflow.com/questions/55099243/python3-dataclass-with-kwargsasterisk
"""

from . import __version__
from . import snews_pt_utils
from .snews_pub import Publisher
from .snews_sub import Subscriber
from .message_schema import Message_Schema as msg_schema
import click
import os, sys

@click.group(invoke_without_command=True)
@click.version_option(__version__)
@click.option('--env', type=str,
    default='/auxiliary/test-config.env',
    show_default='auxiliary/test-config.env',
    help='environment file containing the configurations')
@click.pass_context
def main(ctx, env):
    """ User interface for snews_pt tools
    """
    base = os.path.dirname(os.path.realpath(__file__))
    env_path = base + env
    ctx.ensure_object(dict)
    snews_pt_utils.set_env(env_path)
    ctx.obj['env'] = env
    ctx.obj['DETECTOR_NAME'] = os.getenv("DETECTOR_NAME")

@main.command()
@click.option('--verbose','-v', type=bool, default=True)
@click.argument('file', nargs=-1)
@click.pass_context
def publish(ctx, file, verbose):
    """ Publish a message using snews_pub, multiple files are allowed
    Examples
    --------
    $: snews_pt publish my_json_message.json

    Notes
    -----
    The topics are read from the defaults i.e. from auxiliary/test-config.env
    If no file is given it can still submit dummy messages with default values
    """
    click.clear()
    for f in file:
        if f.endswith('.json'):
            data = snews_pt_utils._parse_file(f)
        else:
            click.secho(f"Expected json file with .json format! Got {f}", fg='red', bold=True)
            sys.exit()

        messages, names_list = snews_pt_utils._tier_decider(data)
        pub = ctx.with_resource(Publisher(ctx.obj['env'], verbose=verbose))
        pub.send(messages)


@main.command()
@click.pass_context
def subscribe(ctx):
    """ Subscribe to Alert topic
    """
    sub = Subscriber(ctx.obj['env'])
    try:
        sub.subscribe()
    except KeyboardInterrupt:
        pass


@main.command()
@click.argument('status', nargs=1)
@click.option('--machine_time','-mt', type=str, default=None, help='`str`, optional  Time when the status was fetched')
@click.option('--verbose','-v', type=bool, default=True, help='Whether to display the output, default is True')
@click.pass_context
# def heartbeat(ctx, status, machine_time, verbose):
#     """
#     Publish heartbeat messages. Recommended frequency is
#     every 3 minutes.
#     machine_time is optional, and each message is appended with a `sent_time`
#     passing machine_time allows for latency studies.

#     USAGE: snews_pt heartbeat ON -mt '22/01/01 19:16:14'

#     """
#     click.secho(f'\nPublishing to Heartbeat; ', bold=True, fg='bright_cyan')
#     message = Heartbeat(detector_name=ctx.obj['DETECTOR_NAME'], status=status, machine_time=machine_time).message()
#     pub = ctx.with_resource(Publisher(ctx.obj['env'], verbose=verbose))
#     pub.send(message)


# TODO: add retraction
# @main.command()
# @click.option('--tier','-t', nargs=1, help='Name of tier you want to retract from')
# @click.option('--number','-n', type=int, default=1, help='Number of most recent message you want to retract')
# @click.option('--reason','-r', type=str, default='', help='Retraction reason')
# @click.option('--false_id', type=str, default='', help='Specific message ID to retract')
# @click.option('--verbose','-v', type=bool, default=True)
# @click.pass_context
# def retract(ctx, tier, number, reason, false_id, verbose):
#     """ Retract N latest message
#     """
#     _, name = snews_pt_utils._check_cli_request(tier)
#     tier = name[0]
#     click.secho(f'\nRetracting from {tier}; ', bold=True, fg='bright_magenta')
#     message = Retraction(detector_name=ctx.obj['DETECTOR_NAME'],
#                          which_tier=tier,
#                          n_retract_latest=number,
#                          false_mgs_id=false_id,
#                          retraction_reason=reason).message()
#     pub = ctx.with_resource(Publisher(ctx.obj['env'], verbose=verbose))
#     pub.send(message)

@main.command()
@click.argument('tier', nargs=1, default='all')
def message_schema(tier):
    """ Display the message format for `tier`, default 'all'

    Notes
    TODO: For some reason, the displayed keys are missing
    """
    tier_data_pairs = {'CoincidenceTier': snews_pt_utils.coincidence_tier_data(),
                       'SigTier':snews_pt_utils.sig_tier_data(),
                       'TimeTier':snews_pt_utils.time_tier_data(),
                       'FalseOBS':snews_pt_utils.retraction_data(),
                       'Heartbeat':snews_pt_utils.heartbeat_data()}

    if tier.lower()=='all':
        # display all formats
        tier = list(tier_data_pairs.keys())
    else:
        # check for aliases e.g. coinc = coincidence = CoinCideNceTier
        tier = snews_pt_utils._check_aliases(tier)

    # get message format for given tier(s)
    msg = msg_schema()
    for t in tier:
        data = tier_data_pairs[t]
        all_data = msg.get_schema(t, data)
        click.secho(f'\t >The Message Schema for {t}', bg='white', fg='blue')
        for k, v in all_data.items():
            if k not in data.keys():
                click.secho(f'{k:<20s}:(SNEWS SETS)', fg='bright_red')
            else:
                click.secho(f'{k:<20s}:(User Input)', fg='bright_cyan')
        click.echo()

@main.command()
def run_scenarios():
    """
    """
    base = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(base, 'test/test_scenarios.py')
    os.system(f'python3 {path}')

if __name__ == "__main__":
    main()
