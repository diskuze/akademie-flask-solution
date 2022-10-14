from flask_env import MetaFlaskEnv


class Config(metaclass=MetaFlaskEnv):
    DB_HOST = "temp-it-akademie.cms8yp1jph9y.eu-central-1.rds.amazonaws.com"
    DB_USER = "temp_it_akademie"
    DB_PASS = "itAkadem1e"
    DB_NAME = "temp_it_akademie"


def get_config():
    return Config()


config = get_config()
