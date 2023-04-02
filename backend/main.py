from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from config import DevConfig
from models import Recipe, User
from exts import db
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)

migrate = Migrate(app, db)

api = Api(app, doc='/docs')

#model (serializer)
recipe_model = api.model(
    "Recipe", {
        "id": fields.Integer(),
        "title": fields.String(),
        "description": fields.String()
    })

signup_model = api.model(
    "SignUp", {
        "username": fields.String(),
        "email": fields.String(),
        "password": fields.String(),
    })


@api.route('/hello')
class HelloResource(Resource):

    def get(self):
        return {"message": "Hello World"}


@api.route('/signup')
class SignUp(Resource):

    @api.expect(signup_model)
    def post(self):
        """SignUp New User"""
        data = request.get_json()

        username = data.get('username')

        db_user = User.query.filter_by(username=username).first()

        if db_user is not None:
            return jsonify(
                {"message": f"User with username {username} already exist"})

        new_user = User(username=data.get('username'),
                        email=data.get('email'),
                        password=generate_password_hash(data.get('password')))

        new_user.save()

        return jsonify({"message": "User created successfuly"})


@api.route('/login')
class Login(Resource):

    def post(self):
        pass


@api.route('/recipes')
class RecipesResource(Resource):

    @api.marshal_list_with(recipe_model)
    def get(self):
        """Get all recipes"""

        recipes = Recipe.query.all()

        return recipes

    @api.marshal_with(recipe_model)
    @api.expect(recipe_model)
    def post(self):
        """Create a new recipe"""

        data = request.get_json()

        new_recipe = Recipe(title=data.get('title'),
                            description=data.get('description'))

        new_recipe.save()

        return new_recipe, 201


@api.route('/recipe/<int:id>')
class RecipeResource(Resource):

    @api.marshal_with(recipe_model)
    def get(self, id):
        """Get recipe by id"""
        recipe = Recipe.query.get_or_404(id)

        return recipe

    @api.marshal_with(recipe_model)
    def put(self, id):
        """update recipe by id"""

        recipe_to_update = Recipe.query.get_or_404(id)

        data = request.get_json()

        recipe_to_update.update(data.get('title'), data.get('description'))

        return recipe_to_update

    @api.marshal_with(recipe_model)
    def delete(self, id):
        """delete recipe by id"""

        recipe_to_delete = Recipe.query.get_or_404(id)

        recipe_to_delete.delete()

        return recipe_to_delete


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "Recipe": Recipe}


if __name__ == '__main__':
    app.run()
