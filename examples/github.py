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
    # Will contain a User resource
    owner = fields.Embedded(User)

    class Meta:
        endpoint_list = '/repos/{user_login}/repos'
        endpoint = '/repos/{user_login}/{repository_name}'


if __name__ == '__main__':
    # Create the api and register our resources
    github_api = Api(base_url='https://api.github.com/')
    github_api.register_resource(User)
    github_api.register_resource(Repository)

    # Get a specific repository. The keys correspond to the
    # placeholders in the endpoints specified above.
    repo = Repository.objects.get(user_login='adamcharnock', repository_name='repose')
    # Print some information about it
    print("{} - {}".format(repo.name, repo.description))
    print("Homepage: {}".format(repo.homepage))
    print("Owner avatar: {}".format(repo.owner.avatar_url))
