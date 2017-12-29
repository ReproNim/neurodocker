"""Package utility functions."""


def _count_key_occurence_list_of_tuples(list_of_tuples, key):
    """Return the number of times `key` occurs as a key in `list_of_tuples`."""
    return sum(1 for i, _ in list_of_tuples if i == key)


def is_url(string):
    from urllib.parse import urlparse

    result = urlparse(string)
    return (result.scheme and result.netloc)


def load_json(filepath, **kwargs):
    """Load JSON file `filepath` as dictionary. `kwargs` are keyword arguments
    for `json.load()`.
    """
    import json

    with open(filepath, 'r') as fp:
        return json.load(fp, **kwargs)


def load_yaml(filepath, **kwargs):
    """Return dictionary from YAML file."""
    import yaml

    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import Loader

    with open(filepath) as fp:
        return yaml.load(fp, Loader=Loader, **kwargs)


def save_json(obj, filepath, indent=4, **kwargs):
    """Save `obj` to JSON file `filepath`. `kwargs` are keyword arguments for
    `json.dump()`.
    """
    import json

    with open(filepath, 'w') as fp:
        json.dump(obj, fp, indent=indent, **kwargs)
        fp.write('\n')


def create_logger():
    """Return Neurodocker logger."""
    import logging

    logger = logging.getLogger('neurodocker')
    ch = logging.StreamHandler()
    format_ = '[NEURODOCKER %(asctime)s %(levelname)s]: %(message)s'
    formatter = logging.Formatter(format_)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


logger = create_logger()


def set_log_level(level):
    """Set logger verbosity.

    Parameters
    ----------
    level: {'debug', 'info', 'warning', 'error', 'critical}
        The level at which to print messages. Case-insensitive.
    """
    import logging

    logging_levels = {'DEBUG': logging.DEBUG,
                      'INFO': logging.INFO,
                      'WARNING': logging.WARNING,
                      'ERROR': logging.ERROR,
                      'CRITICAL': logging.CRITICAL}
    try:
        level = logging_levels[level.upper()]
        logger.setLevel(level)
    except KeyError:
        raise ValueError("invalid level '{}'".format(level))
