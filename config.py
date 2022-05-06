from environs import Env
env = Env()
env.read_env()

class Config:
    SECRET_KEY = env.str("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = env.str("SQLALCHEMY_DATABASE_URI")