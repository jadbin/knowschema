# coding=utf-8

# Database URI, example: mysql://username:password@server/db?charset=utf8mb4
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/knowschema?charset=utf8mb4'


# guniflask configuration
guniflask = dict(
    cors=True,
    authorization_server='https://uaa.kdsec.org',
)
