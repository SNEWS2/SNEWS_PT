"""Test publishing coincidence tier messages."""
from snews import messages

from snews_pt.messages import Publisher


def test_publisher_add_message():
    publisher = Publisher('kafka://kafka.scimma.org/snews.experiments-test')

    publisher.add_message(
        messages.HeartbeatMessage(
            detector_name='XENONnT',
            machine_time='2012-06-09T15:30:00.000501',
            detector_status='ON',
            firedrill_mode=False,
            is_test=True
        )
    )

    assert len(publisher.message_queue) == 1


def test_publisher_send_message():
    publisher = Publisher('kafka://kafka.scimma.org/snews.experiments-test')

    publisher.add_message(
        messages.HeartbeatMessage(
            detector_name='XENONnT',
            machine_time='2012-06-09T15:30:00.000501',
            detector_status='ON',
            firedrill_mode=False,
            is_test=True
        )
    )

    publisher.send()

    assert True


def test_messages_main_function():
    from snews_pt.messages import test

    test()

    assert True


def test_heartbeat_message():
    messages.HeartbeatMessage(
        detector_name='XENONnT',
        machine_time='2012-06-09T15:30:00.000501',
        detector_status='ON',
        firedrill_mode=False,
        is_test=True
    )

    assert True


def test_retraction_message():
    assert True


def test_significance_tier_message():
    messages.SignificanceTierMessage(
        detector_name='DS-20K',
        machine_time_utc='2012-06-09T15:30:00.000501',
        neutrino_time_utc='2012-06-09T15:31:08.109876',
        p_values=[0.4, 0.5],
        t_bin_width_sec=0.8,
        is_firedrill=False,
        is_test=True,
    )

    assert True


def test_timing_tier_message():
    messages.TimingTierMessage(
        detector_name='XENONnT',
        neutrino_time='2012-06-09T15:31:08.109876',
        timing_series=[
            '2012-06-09T15:31:08.109876',
            '2012-06-09T15:33:07.891011',
            '2012-06-09T15:33:07.9910110',
            '2012-06-09T15:34:07.891011000',
            '2012-06-09T15:35:17.0',
        ],
        machine_time_utc='2012-06-09T15:30:00.009876',
        is_firedrill=False,
        is_test=True,
    )

    assert True


def test_coincidence_tier_message():
    """Test with example of expected message type."""

    messages.CoincidenceTierMessage(
        detector_name='KamLAND',
        machine_time_utc='2012-06-09T15:30:00.000501',
        neutrino_time_utc='2012-06-09T15:31:08.891011',
        is_firedrill=False,
        is_test=True
    )

    assert True
