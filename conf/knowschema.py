# coding=utf-8

# Database URI, example: mysql://username:password@server/db?charset=utf8mb4
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@10.26.24.59:30212/knowschema?charset=utf8mb4'

elastic_graph_base_url = 'http://localhost:6660/api'

JSON_AS_ASCII = False

# guniflask configuration
guniflask = dict(
    cors=True,
)

UPLOAD_DIR = "knowschema/files/"

GRAPH_BACKUP_FILE = "knowschema/files/graph_backup.json"
