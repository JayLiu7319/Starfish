from starfish.frame_api.common import hooks

# Pecan Application Configurations
# See https://pecan.readthedocs.org/en/latest/configuration.html#application-configuration # noqa
app = {
    'root': 'starfish.frame_api.root_controller.RootController',
    'modules': ['starfish.frame_api'],
    'hooks': [
        hooks.ContextHook(),
        hooks.QueryParametersHook()
    ],
    'debug': True
}

# WSME Configurations
# See https://wsme.readthedocs.org/en/latest/integrate.html#configuration
wsme = {
    # Provider driver uses 501 if the driver is not installed.
    # Don't dump a stack trace for 501s
    'debug': False
}
