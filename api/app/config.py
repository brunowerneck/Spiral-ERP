class BaseConfig:
    BCRYPT_LOG_ROUNDS = 12

    DEBUG = True

    DB_SERVER = 'database'
    DB_USER = 'root'
    DB_PASS = 'root'
    DB_NAME = 'erp_free'

    @property
    def DATABASE_URI(self):  # Note: all caps
        return f'mysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_SERVER}/{self.DB_NAME}'

    SECRET_KEY = 'change me'

    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_RECYCLE = 30
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TOKEN_EXPIRATION_MINUTES = 0


class DevConfig(BaseConfig):
    BCRYPT_LOG_ROUNDS = 4

    SECRET_KEY = 'DEV'

    TOKEN_EXPIRATION_MINUTES = 5


class ProdConfig(BaseConfig):
    BCRYPT_LOG_ROUNDS = 13

    DB_SERVER = '192.168.0.99'

    SECRET_KEY = 'fjkd89sa78u8&#¨%Bvfijds0f9ajs8ia9'

    TOKEN_EXPIRATION_MINUTES = 30
