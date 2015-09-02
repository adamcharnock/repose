from repose import fields
from repose.api import Api
from repose.resources import Resource


class User(Resource):
    id = fields.Integer()
    login = fields.String()
    avatar_url = fields.String()

    class Meta:
        endpoint = '/users/{user_login}'


class Repository(Resource):
    name = fields.String()
    description = fields.String()
    homepage = fields.String()
    has_issues = fields.Boolean()
    has_wiki = fields.Boolean()
    has_downloads = fields.Boolean()

    owner = fields.Embedded(User)

    class Meta:
        endpoint_list = '/repos/{user_login}/repos'
        endpoint = '/repos/{user_login}/{repository_name}'


if __name__ == '__main__':
    github_api = Api(base_url='https://api.github.com/')
    github_api.register_resource(User)
    github_api.register_resource(Repository)

    repo = Repository.objects.get(user_login='adamcharnock', repository_name='repose')
    print("{} - {}".format(repo.name, repo.description))
    print("Homepage: {}".format(repo.homepage))
    print("Owner avatar: {}".format(repo.owner.avatar_url))
