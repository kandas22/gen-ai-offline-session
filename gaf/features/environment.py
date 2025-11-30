"""
Behave environment configuration
"""
from config import Config


def before_all(context):
    """Setup before all tests"""
    Config.ensure_directories()
    context.config = Config


def before_scenario(context, scenario):
    """Setup before each scenario"""
    pass


def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    # Cleanup browser if exists
    if hasattr(context, 'automation') and context.automation:
        try:
            context.automation.stop_browser()
        except:
            pass


def after_all(context):
    """Cleanup after all tests"""
    pass
