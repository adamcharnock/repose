from repose import fields
from repose.api import Api
from repose.resources import Resource

class User(Resource):
    id = fields.Integer()
    login = fields.String()
    avatar_url = fields.String()
    location = fields.String()
    site_admin = fields.Boolean()

    class Meta:
        # Endpoint for getting a single specific user
        endpoint = '/users/{login}'
        # Endpoint for listing all users
        endpoint_list = '/users'

class Repository(Resource):
    id = fields.Integer()
    name = fields.String()
    full_name = fields.String()
    description = fields.String()
    owner = fields.Embedded(User)

    class Meta:
        # Endpoint for getting a single specific repository
        endpoint = '/repos/{full_name}'
        # Endpoint for listing all repositories
        endpoint_list = '/repositories'


if __name__ == '__main__':
    # Create the api and register our resources
    github_api = Api(base_url='https://api.github.com/')
    github_api.register_resource(User)
    github_api.register_resource(Repository)

    repo = User.objects.get(login='adamcharnock')
    import pdb; pdb.set_trace()
