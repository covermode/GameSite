from flask_restful import reqparse


def make_parser(fields):
    parser = reqparse.RequestParser()
    for _field in fields:
        parser.add_argument(_field, required=True, type=fields[_field])
    del _field
    return parser
