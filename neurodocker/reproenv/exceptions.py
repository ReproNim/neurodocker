"""Exceptions for ReproEnv."""


class ReproEnvError(Exception):
    """Base class for all ReproEnv exceptions."""


class RendererError(ReproEnvError):
    pass


class RequirementsError(ReproEnvError):
    pass


class TemplateError(ReproEnvError):
    pass


class TemplateKeywordArgumentError(TemplateError):
    """Invalid keyword argument passed to template, or required argument not
    provided.
    """

    pass


class TemplateNotFound(ReproEnvError):
    pass
