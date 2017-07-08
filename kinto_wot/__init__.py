import pkg_resources
import logging
import requests
from kinto.core.events import ACTIONS, AfterResourceChanged

logger = logging.getLogger(__name__)

#: Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version


DEFAULT_SETTINGS = {}


def handle_actions(event):
    for change in event.impacted_records:
        previous = change.get('old')
        new = change["new"]
        if new.get('action') and previous and previous['value'] != new['value']:
            resp = requests.post(
                new['action'],
                json={new["metadata"].get("name", "value"): new["value"]})
            try:
                resp.raise_for_status()
            except:
                logger.exception("Failed to call %s" % new["action"])


def includeme(config):
    settings = config.get_settings()

    defaults = {k: v for k, v in DEFAULT_SETTINGS.items() if k not in settings}
    config.add_settings(defaults)

    config.add_api_capability(
        "wot",
        version=__version__,
        description='Handle WoT action URL.',
        url="https://github.com/Natim/kinto-wot")

    config.add_subscriber(
        handle_actions,
        AfterResourceChanged,
        for_actions=(ACTIONS.CREATE, ACTIONS.UPDATE),
        for_resources=('record'))
