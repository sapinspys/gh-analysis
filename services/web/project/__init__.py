import os
from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource
from peewee import *
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
app.config.from_object(__name__)

api = Api(app)

db = PostgresqlDatabase(os.environ.get("POSTGRES_DB"), user=os.environ.get("POSTGRES_USER"), password=os.environ.get(
    "POSTGRES_PASSWORD"), host=os.environ.get("SQL_HOST"), port=os.environ.get("SQL_PORT"))


class BaseModel(Model):
    class Meta:
        database = db


class Repo(BaseModel):
    name = CharField(255)

    def serialize(self):
        repo_dict = model_to_dict(self)
        return repo_dict


class Pull(BaseModel):
    repo_id = ForeignKeyField(Repo, backref='pulls')
    created_date = DateTimeField()
    is_merged = BooleanField()
    additions = IntegerField()
    deletions = IntegerField()

    def serialize(self):
        pull_dict = model_to_dict(self)
        pull_dict["created_date"] = (
            pull_dict["created_date"].strftime('%Y-%m-%d')
        )

        return pull_dict

# Index
class Index(Resource):
    def get(self):
        return {"message": "Server running OK."}

# RepoList
# shows a list of all repos
class RepoList(Resource):
    def get(self):
        query = db.Repo.select().dicts()
        return [row for row in query], 200


# PullList
# shows a list of all pulls
class PullList(Resource):
    def get(self):
        query = db.Pull.select()
        return jsonify([r.serialize() for r in query])


# PullListByRepo
# shows a list of all pulls for given repo
class PullListByRepo(Resource):
    def get(self, repo_name):
        query = db.Pull.select().join(db.Repo).where(db.Repo.name == repo_name)
        return jsonify([r.serialize() for r in query])


api.add_resource(RepoList, '/github/repo/')
api.add_resource(PullList, '/github/pull/')
api.add_resource(PullListByRepo, '/github/pull/<repo_name>')

if __name__ == '__main__':
    DEBUG = bool(os.environ.get('DEBUG'))
    app.run(debug=DEBUG)

# def abort_if_todo_doesnt_exist(todo_id):
#     if todo_id not in TODOS:
#         abort(404, message="Todo {} doesn't exist".format(todo_id))

# temp_repos = ["kubernetes/kubernetes", "apache/spark"]

# top_repos = ["kubernetes/kubernetes", "apache/spark", "Microsoft/vscode",
#              "nodejs/node", "tensorflow/tensorflow", "freeCodeCamp/freeCodeCamp",
#              "apple/swift", "rust-lang/rust", "openshift/origin", "ansible/ansible"]

# Refresh:
# Clears DB and saves last 3 days of data for given repos
# class Refresh(Resource):
#     def post(self):
#         db.Repo.delete().execute()
#         db.Pull.delete().execute()

#         g = Github("d38d9579d63a4781c295fc499497f5d65714c2ed")
#         repos = [g.get_repo(repo) for repo in temp_repos]
#         pulls_paginatedLists = dict(
#             (repo.name, repo.get_pulls(state="all")) for repo in repos)

#         limit = date.today() - timedelta(3)
#         repo_names = list(pulls_paginatedLists.keys())
#         pulls_pls_3day = dict((name, []) for name in repo_names)

#         for repo in repo_names:
#             for pull in pulls_paginatedLists[repo]:
#                 pull_date = pull.created_at.date()
#                 if pull_date == date.today():
#                     continue
#                 elif pull_date >= limit:
#                     pulls_pls_3day[repo].append(pull)
#                 else:
#                     break

#         repo_data = [{"name": name} for name in repo_names]

#         with db.db.atomic():
#             db.Repo.insert_many(repo_data).execute()

#         pulls_data = []

#         for repo in repo_names:
#             pulls = pulls_pls_3day[repo]
#             for pull in pulls:
#                 pulls_data.append({"repo_id": db.Repo.get(db.Repo.name == repo),
#                                    "created_date": pull.created_at.date(),
#                                    "is_merged": pull.merged,
#                                    "additions": pull.additions,
#                                    "deletions": pull.deletions
#                                    })

#         with db.db.atomic():
#             db.Pull.insert_many(pulls_data).execute()

#         return {"message": "DB Refreshed"}, 201