import os


def load_config():
    mode = os.environ.get("MODE")
    try:
        if mode == "PRODUCTION":
            from config.production import ProductionConfig

            return ProductionConfig
        elif mode == 'TEST':
           from config.test import TestConfig
           return TestConfig
        else:
            from config.development import DevelopmentConfig

            return DevelopmentConfig
    except ImportError as e:
        raise e
