--Abilities

--View Individual Ability Information
SELECT *
FROM ability
WHERE a_name = '?'

--View Abilties By Pokemon
SELECT pa_ability1 
FROM pokemon_to_ability
WHERE pa_pokemon = '?'
UNION ALL
SELECT pa_ability2
FROM pokemon_to_ability
WHERE pa_pokemon = '?'

--View Hidden Abilities By Pokemon

SELECT pa_hidden_ability 
FROM pokemon_to_ability
WHERE pa_pokemon = '?'


--View Abilities By Generation

SELECT a_name
FROM ability
WHERE a_generation = '?' 