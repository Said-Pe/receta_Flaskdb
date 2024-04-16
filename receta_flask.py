from flask import Flask, render_template, request, redirect, url_for
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        # Obtener los datos del formulario
        name = request.form['name']
        ingredients = request.form['ingredients']
        steps = request.form['steps']

        # Crear un nuevo ID de receta
        recipe_id = r.incr('recipe_id')

        # Almacenar los datos de la receta en Redis
        recipe_key = f'recipe:{recipe_id}'
        recipe_data = {
            'name': name,
            'ingredients': ingredients,
            'steps': steps
        }
        for field, value in recipe_data.items():
            r.hset(recipe_key, field, value)

        return redirect(url_for('index'))  # Redireccionar a la página principal
    else:
        return render_template('add_recipe.html')


@app.route('/update_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    if request.method == 'POST':
        # Obtener los datos del formulario
        name = request.form['name']
        ingredients = request.form['ingredients']
        steps = request.form['steps']

        # Actualizar los datos de la receta en Redis
        recipe_key = f'recipe:{recipe_id}'
        recipe_data = {
            'name': name,
            'ingredients': ingredients,
            'steps': steps
        }
        for field, value in recipe_data.items():
            r.hset(recipe_key, field, value)

        # Redireccionar a la página principal
        return redirect(url_for('index'))
    else:
        # Obtener los datos de la receta de Redis
        recipe_key = f'recipe:{recipe_id}'
        recipe_data = r.hgetall(recipe_key)
        recipe = {
            'name': recipe_data[b'name'].decode(),
            'ingredients': recipe_data[b'ingredients'].decode(),
            'steps': recipe_data[b'steps'].decode()
        }
        # Pasar el objeto 'recipe' a la plantilla
        return render_template('update_recipe.html', recipe_id=recipe_id, recipe=recipe)


@app.route('/delete_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    if request.method == 'POST':
        # Eliminar la receta con el ID dado de Redis
        recipe_key = f'recipe:{recipe_id}'
        r.delete(recipe_key)

        # Redireccionar al usuario a la página principal
        return redirect(url_for('index'))
    else:
        # Mostrar la página de confirmación de eliminación
        return render_template('delete_recipe.html', recipe_id=recipe_id)


@app.route('/view_recipes')
def view_recipes():
    recipe_keys = r.keys('recipe:*')
    recipes = []

    for key in recipe_keys:
        recipe_data = r.hgetall(key)
        decoded_recipe = {
            'id': int(key.decode().split(':')[1]),  # Obtener el ID de la clave de Redis
            'name': recipe_data[b'name'].decode(),
            'ingredients': recipe_data[b'ingredients'].decode(),
            'steps': recipe_data[b'steps'].decode()
        }
        recipes.append(decoded_recipe)

    return render_template('view_recipes.html', recipes=recipes)


@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    # Recuperar los detalles de la receta de Redis
    recipe_key = f'recipe:{recipe_id}'
    recipe_data = r.hgetall(recipe_key)
    if recipe_data:
        recipe = {
            'name': recipe_data[b'name'].decode(),
            'ingredients': recipe_data[b'ingredients'].decode(),
            'steps': recipe_data[b'steps'].decode()
        }
        # Pasar los detalles de la receta a la plantilla HTML
        return render_template('view_recipe.html', recipe=recipe)
    else:
        # Manejar el caso en el que no se encuentre la receta
        return 'Receta no encontrada', 404


@app.route('/search_recipes', methods=['GET', 'POST'])
def search_recipes():
    if request.method == 'POST':
        search_term = request.form['search_term']
        # Código para buscar recetas que coincidan con el término de búsqueda
        matched_recipes = []
        recipe_keys = r.keys('recipe:*')
        for key in recipe_keys:
            recipe_data = r.hgetall(key)
            recipe_name = recipe_data[b'name'].decode()
            recipe_ingredients = recipe_data[b'ingredients'].decode()
            recipe_steps = recipe_data[b'steps'].decode()
            if search_term.lower() in recipe_name.lower() or \
               search_term.lower() in recipe_ingredients.lower() or \
               search_term.lower() in recipe_steps.lower():
                recipe_id = int(key.decode().split(':')[1])
                matched_recipes.append({'name': recipe_name, 'id': recipe_id})
        return render_template('search_results.html', recipes=matched_recipes)
    else:
        return render_template('search_recipes.html')


if __name__ == '__main__':
    app.run(debug=True)
