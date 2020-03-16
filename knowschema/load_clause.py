import json
import os
import re
import logging

from knowschema.app import db
from knowschema.models import Field, Clause

logger = logging.getLogger(__name__)

clause_dir = "knowschema/clauses/"

def load_clause(app):
    docs = os.listdir(clause_dir)

    pattern = re.compile("_.*\.")
    for doc in docs:
        with app.app_context():
            title = pattern.findall(doc)[0][1:-1]
            logger.debug(f"File name : {doc}, title : {title}")
            field = dict()
            field['uri'] = "education"
            field['title'] = title

            field_item = Field.from_dict(field)
            db.session.add(field_item)
            db.session.commit()

            field_id = Field.query.filter_by(title=title).first().id
            logger.debug(f"Field id : {field_id}")

            clauses = json.load(open(clause_dir + doc, "r"))
            for clause in clauses:
                item = dict()
                item['uri'] = clause['id']
                item['content'] = clause['content']
                item['level'] = clause['meta']['level']
                item['field_id'] = field_id

                clause_item = Clause.from_dict(item)
                db.session.add(clause_item)
                db.session.commit()