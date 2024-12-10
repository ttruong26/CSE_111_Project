from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import json
import sqlite3
from sqlite3 import Error
import glob


#Configure Flask app
app = Flask(__name__)
CORS(app)

#Configure DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite" 

#set db variable as a SQLAlchemy obj tied to flask app "app"
db = SQLAlchemy(app) 

database = r"data/pokeData.db"

def openConnection(_dbFile):
    print("Open database: ", _dbFile)

    conn = None
    try:
        conn = sqlite3.connect(_dbFile)
        print("success")
    except Error as e:
        print(e)

    return conn

def closeConnection(_conn, _dbFile):
    print("Close database: ", _dbFile)

    try:
        _conn.close()
        print("success")
    except Error as e:
        print(e)


    # create a database connection


#Default Route "Landing page"
@app.route('/')
def renderIndex():
        #We use the render_template command to render an html page
        return render_template('homePage.html')

@app.route('/viewAllRegions')
def viewAllRegions():
        
        #Perfrom the query based on code from lab 7 
        sql = """SELECT * 
                 FROM region """
        
        #Connect to DB **Necessary before each query 
        conn = openConnection(database)
        cur = conn.cursor()

        #Execute query and save all rows to a variable
        cur.execute(sql)
        _regions = cur.fetchall()

        # print(type(_regions))

        #We can pass the obj lists as arguments to an html page using render_template.
            #We can parse through the list in the html page with Jinja2 
        return render_template('viewAllRegions.html', regions = _regions)

@app.route("/viewIndRegion/<regionName>")
def viewIndRegion(regionName):

    conn = openConnection(database)
    cur = conn.cursor()

    sql = """SELECT * 
                FROM region 
                WHERE r_region_name = ?"""
    
    cur.execute(sql, (regionName, ))
    _regionInfo = cur.fetchall()
    
    trainerQuery = """SELECT t_name 
                        FROM trainers
                        WHERE t_region = ? """
    cur.execute(trainerQuery, (regionName, ))
    _regionTrainers = cur.fetchall()

    print (_regionTrainers)

    return render_template("viewIndRegion.html", regionInfo = _regionInfo, regionTrainers = _regionTrainers)
    

@app.route('/viewIndPokemon/<pokemonName>')
def viewIndPokemon(pokemonName):

    #Any query we want to diplay on the page, we fetch it as a list before passing all lists to the html page render

    sql = """SELECT * 
                 FROM pokemon
                  WHERE p_name = ? """
    
    #Second query we will display on viewIndPokemon Page
    evoQuery = """SELECT p2.p_name
                    FROM pokemon p1, pokemon p2 
                        WHERE p1.p_name == ? AND 
                        p1.p_evo_species = p2.p_evo_species
                        ORDER BY p2.p_evolution_stage ASC"""
    
    #Third query displayed. Lists all of the types in alpha order. Also lists the given effectiveness multiplier of the type on the current pokemon. 
    weaknessQuery = """SELECT tc_type, MAX(tc_effectiveness) * MIN(tc_effectiveness) AS effectiveness_multiplier
                        FROM (
                            SELECT tc1.tc_type, tc1.tc_effectiveness
                            FROM pokemon p
                            JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against
                            WHERE p.p_name = ?
                            UNION ALL

                            SELECT tc2.tc_type, tc2.tc_effectiveness
                            FROM pokemon p
                            JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against
                            WHERE p.p_name = ?
                        ) AS combined
                        GROUP BY tc_type
                        HAVING MAX(tc_effectiveness) * MIN(tc_effectiveness) >= 0;
                    """
    
    ### Queries to display all pokemon weak to a given type. 
    # Type1 will be type of current pokemon.
    strongType1Query = """
                            SELECT p.p_name
                            FROM pokemon p
                            JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against
                            LEFT JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against
                            WHERE (tc1.tc_type = (SELECT p_type1 FROM pokemon WHERE p_name = ?) AND tc1.tc_effectiveness > 1)
                            AND (p.p_type2 IS NULL OR tc2.tc_type = (SELECT p_type1 FROM pokemon WHERE p_name = ?) AND tc2.tc_effectiveness >= 1)
                            GROUP BY p.p_name;
                    """

    # If type2 != NULL then we display all pokemon weak to type2 of current pokemon
    strongType2Query = """
                           SELECT p.p_name
                            FROM pokemon p
                            JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against AND tc1.tc_type = (SELECT p_type2 FROM pokemon WHERE p_name = ?)
                            LEFT JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against AND tc2.tc_type = (SELECT p_type2 FROM pokemon WHERE p_name = ?)
                            WHERE (tc1.tc_effectiveness > 1 AND (p.p_type2 IS NULL OR (tc2.tc_effectiveness IS NULL OR tc2.tc_effectiveness >= 1)))
                            OR (p.p_type2 IS NOT NULL AND tc2.tc_effectiveness > 1 AND tc1.tc_effectiveness >= 1)
                            GROUP BY p.p_name;
                        """
    
    # Query that grabs all of the stats of a pokemon from the pokemon table
    pokeStatsQuery = """SELECT p_hp, p_attack, p_defense, p_sp_attack, p_sp_defense, p_speed, p_base_total
                        FROM pokemon
                        WHERE p_name = ?;
                    """
    
    abilitiesQuery = """SELECT pa_ability1, pa_ability2, pa_hidden_ability 
                        FROM pokemon_to_abilities
                        WHERE pa_pokemon == ? """
        
    conn = openConnection(database)
    cur = conn.cursor()

     #Need to execute seperate queries separately to obtain different list vars we can pass to the HTML page
    cur.execute(sql, (pokemonName, ))
    _pokeInfo = cur.fetchall()

    cur.execute(evoQuery, (pokemonName, ))
    _evoGroup = cur.fetchall()

    cur.execute(weaknessQuery, (pokemonName, pokemonName))
    _pokeWeakness = cur.fetchall()

    cur.execute(strongType1Query, (pokemonName, pokemonName))
    _strongType1 = cur.fetchall()

    cur.execute(strongType2Query, (pokemonName, pokemonName))
    _strongType2 = cur.fetchall()

    cur.execute(pokeStatsQuery, (pokemonName, ))
    _pokeStats = cur.fetchall()

    cur.execute(abilitiesQuery, (pokemonName, ))
    _pokemonAbilities = cur.fetchall()
     
     #Pass both vars to html page
    return render_template('viewIndPokemon.html', pokeInfo = _pokeInfo, evoGroup = _evoGroup, pokeWeakness = _pokeWeakness, strongType1 = _strongType1, strongType2 = _strongType2, pokeStats = _pokeStats, pokemonAbilities = _pokemonAbilities)

@app.route('/viewAllPokemon')
def viewAllPokemon():

    #Any query we want to diplay on the page, we fetch it as a list before passing all lists to the html page render

    sql = """SELECT * 
                 FROM pokemon"""
    
        
    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql)
    _allPokemon = cur.fetchall()
     
    return render_template('viewAllPokemon.html', allPokemon = _allPokemon)

@app.route('/viewIndType/<pokeType>')
def viewIndType(pokeType):

    query = """
                SELECT *, ? as Type
                FROM pokemon
                WHERE p_type1 = ? OR p_type2 = ?
                GROUP BY p_name;
                """

    conn = openConnection(database)
    cur = conn.cursor()

    cur .execute(query, (pokeType, pokeType, pokeType))
    _allPokemonType = cur.fetchall()

    return render_template('viewIndType.html', allPokemonType = _allPokemonType)

@app.route('/viewAllTrainers')
def viewAllTrainers():
    sql = """SELECT * 
                 FROM trainers"""
     
    conn = openConnection(database)
    cur = conn.cursor()
    cur.execute(sql)
    _allTrainers = cur.fetchall()
     
    return render_template('viewAllTrainers.html', allTrainers = _allTrainers)

@app.route('/viewIndTrainer/<trainerName>')
def viewIndTrainer(trainerName):
    sql = """ SELECT *
                FROM trainers
                WHERE t_name == ?"""
    
    pokeQuery = """ SELECT DISTINCT t1.tp_pokemon
                    FROM trainer_to_pokemon t1
                    WHERE t1.tp_trainer == ?;"""
     
    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql, (trainerName, ))
    _trainerInfo = cur.fetchall()

    cur.execute(pokeQuery, (trainerName, ))
    _trainerPokemon = cur.fetchall()



    return render_template("viewIndTrainer.html", trainerInfo = _trainerInfo, trainerPokemon = _trainerPokemon)

@app.route('/viewAllAbilities')
def viewAllAbilities():
    sql = """ SELECT * 
                FROM abilities"""
     
    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql)
    _allAbilities = cur.fetchall()
     
    return render_template("viewAllAbilities.html", allAbilities = _allAbilities)

@app.route('/viewIndAbility/<abilityName>')
def viewAllAbility(abilityName):
    sql = """ SELECT * 
                FROM abilities 
                WHERE a_name == ?"""
    
    pokeQuery = """SELECT DISTINCT pa_pokemon
                FROM abilities, pokemon_to_abilities
                WHERE a_name = ? AND 
                        (a_name = pa_ability1 OR 
                            a_name = pa_ability2 OR 
                                a_name = pa_hidden_ability)"""
     
    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql, (abilityName,))
    _allAbilities = cur.fetchall()

    cur.execute(pokeQuery, (abilityName, ))
    _pokemonWithAbility = cur.fetchall()

    print (_pokemonWithAbility)
     
    return render_template("viewIndAbility.html", allAbilities = _allAbilities, pokemonWithAbility = _pokemonWithAbility)

@app.route('/viewEggGroups')
def viewEggGroups():
    sql = """SELECT *
                FROM egg_groups"""

    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql)
    _allEggGroups = cur.fetchall()


    return render_template("viewEggGroups.html", allEggGroups = _allEggGroups) 

@app.route('/viewIndEggGroup/<eggGroup>')
def viewIndEggGroup(eggGroup):
    sql = """SELECT *
                FROM egg_groups
                    WHERE e_egg_group_1 == ? OR 
                            e_egg_group_2 == ? """

    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql, (eggGroup, eggGroup,))
    _pokemonInEggGroup = cur.fetchall()


    return render_template("viewIndEggGroup.html", pokemonInEggGroup = _pokemonInEggGroup, eggGroup = eggGroup) 

@app.route("/test")
def test():
    sql = """SELECT *
                FROM region """

    conn = openConnection(database)
    cur = conn.cursor()

    cur.execute(sql)
    _regionInfo = cur.fetchall()

    return render_template("test.html", regionInfo=json.dumps(_regionInfo))

@app.route('/validateType', methods=['GET'])
def validateType():
    type_name = request.args.get('type', '').strip().lower()  # Convert to lowercase
    if not type_name:
        return jsonify({'isValid': False})
    
    conn = openConnection(database)
    cur = conn.cursor()
    
    query = """SELECT COUNT(*)
               FROM typeChart
               WHERE LOWER(tc_type) = ?"""  # Use LOWER() in SQL to ensure case-insensitive comparison
    
    cur.execute(query, (type_name,))
    result = cur.fetchone()
    
    closeConnection(conn, database)
    
    return jsonify({'isValid': result[0] > 0})

@app.route('/validateRegion', methods=['GET'])
def validateRegion():
    region_name = request.args.get('region', '').strip().lower()  # Convert to lowercase
    if not region_name:
        return jsonify({'isValid': False})
    
    conn = openConnection(database)
    cur = conn.cursor()
    
    query = """SELECT COUNT(*)
               FROM region
               WHERE LOWER(r_region_name) = ?"""  # Use LOWER() in SQL to ensure case-insensitive comparison
    
    cur.execute(query, (region_name,))
    result = cur.fetchone()
    print(result[0] > 0)
    closeConnection(conn, database)
    
    return jsonify({'isValid': result[0] > 0})

@app.route('/validatePokemon', methods=['GET'])
def validatePokemon():
    pokemon = request.args.get('pokemon', '').strip().lower()  # Convert to lowercase
    if not pokemon:
        return jsonify({'isValid': False})
    
    conn = openConnection(database)
    cur = conn.cursor()
    
    query = """SELECT COUNT(*)
               FROM pokemon
               WHERE LOWER(p_name) = ?"""  # Use LOWER() in SQL to ensure case-insensitive comparison
    
    cur.execute(query, (pokemon,))
    result = cur.fetchone()
    print(result[0] > 0)
    closeConnection(conn, database)
    
    return jsonify({'isValid': result[0] > 0})

@app.route('/validateTrainerName', methods=['GET'])
def validateTrainer():
    trainer = request.args.get('trainerName', '').strip().lower()  # Convert to lowercase
    if not trainer:
        return jsonify({'isValid': False})
    
    conn = openConnection(database)
    cur = conn.cursor()
    
    query = """SELECT COUNT(*)
               FROM trainers
               WHERE LOWER(t_name) = ?"""  # Use LOWER() in SQL to ensure case-insensitive comparison
    
    cur.execute(query, (trainer,))
    result = cur.fetchone()
    print(result[0] > 0)
    closeConnection(conn, database)
    
    return jsonify({'isValid': result[0] == 0})

@app.route('/searchPokemon', methods=['GET'])
def searchPokemon():
    query = request.args.get('query', '').strip().lower()
    image_folder = './static/images/pokemon'
    
    try:
        conn = openConnection(database)
        cur = conn.cursor()

        # Query Pokémon names matching the search term
        search_query = """
            SELECT p_name AS name
            FROM pokemon
            WHERE LOWER(p_name) LIKE ?
            LIMIT 10
        """
        cur.execute(search_query, (f'%{query}%',))
        results = [{'name': row[0], 'image': f'{row[0]}.png'} for row in cur.fetchall()]
        # Verify if the image exists in the folder
        

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        closeConnection(conn, database)
    print(results)
    return jsonify(results)

@app.route('/populateCustomTrainer', methods=['POST'])
def populateCustomTrainer():
    trainer_name = request.form.get('trainerName')
    region = request.form.get('region')
    trainer_type = request.form.get('type').lower() 
    generation = request.form.get('generation')
    pokemon_team = request.form.getlist('pokemon[]')
    image = request.files['image']

    # Handle optional image upload
    if image and image.filename != '':
        # Save the uploaded image to the static/images/trainers folder
        image_path = f'static/images/trainers/{trainer_name}.png'
        image.save(image_path)
        print("Custom image uploaded and saved.")
    else:
        # Use a default image if no image is uploaded
        default_image_path = 'static/images/trainers/default.png'
        image_path = f'static/images/trainers/{trainer_name}.png'

        # Open the default image and write it to the new path
        with open(default_image_path, 'rb') as default_file:
            with open(image_path, 'wb') as new_file:
                new_file.write(default_file.read())
        print("Default image used and saved.")


    try:
        generation = int(request.form.get('generation', 0))  # Default to 0 if not provided
    except ValueError:
        return jsonify({'error': 'Invalid generation value. Must be an integer.'}), 400
    try:
        conn = openConnection(database)
        cur = conn.cursor()

        query = """
                Select MAX(t_id)
                    FROM trainers
                """
        cur.execute(query)
        newID = cur.fetchone()[0]

        # Insert trainer into the database
        trainer_query = """
            INSERT INTO trainers (t_id,t_region,t_gen,t_name,t_type,t_role)
            VALUES (?, ?, ?, ?, ?,"Custom")
        """
        cur.execute(trainer_query, (newID,region,generation,trainer_name,trainer_type))

        # Insert Pokémon team into trainer_to_pokemon table
        for pokemon in pokemon_team:
            team_query = """
                INSERT INTO trainer_to_pokemon (tp_trainer, tp_pokemon)
                VALUES (?, ?)
            """
            cur.execute(team_query, (trainer_name, pokemon))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        closeConnection(conn, database)

    return redirect('/customTrainers')
    
    



@app.route('/customTrainers', methods=['GET'])
def getCustomTrainers():

    sql = """SELECT * 
                 FROM trainers
                 Where t_role = "Custom"
            """
     
    conn = openConnection(database)
    cur = conn.cursor()
    cur.execute(sql)
    _allTrainers = cur.fetchall()
     
    return render_template('customTrainer.html', allTrainers = _allTrainers)

@app.route('/deleteTrainerByName/<trainer_name>', methods=['DELETE'])
def deleteTrainerByName(trainer_name):
    try:
        conn = openConnection(database)
        cur = conn.cursor()

        # Delete the trainer's Pokémon team
        delete_team_query = """
            DELETE FROM trainer_to_pokemon WHERE tp_trainer = ?
        """
        cur.execute(delete_team_query, (trainer_name,))

        # Delete the trainer
        delete_trainer_query = "DELETE FROM trainers WHERE t_name = ?"
        cur.execute(delete_trainer_query, (trainer_name,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        closeConnection(conn, database)

    return jsonify({'success': True}), 200


if __name__ == '__main__':

    app.run()