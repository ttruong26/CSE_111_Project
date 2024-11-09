
-- View all trainers that belong to " " region. 
SELECT t_name 
FROM trainers
WHERE t_region = 'Kanto';

-- View all the abilities of " " pokemon
SELECT pa_ability1, pa_ability2, pa_hidden_ability 
FROM pokemon_to_abilities
WHERE pa_pokemon == 'Charmander';

--List all region information
SELECT * 
FROM region;

--List all the pokemon that belong to the " " trainer
SELECT DISTINCT t1.tp_pokemon
FROM trainer_to_pokemon t1
WHERE t1.tp_trainer == 'Blaine';

--List all of the pokemon in the evolution chain of pikachu
SELECT p2.p_name
FROM pokemon p1, pokemon p2 
WHERE p1.p_name == 'Pikachu' AND 
p1.p_evo_species = p2.p_evo_species
ORDER BY p2.p_evolution_stage ASC

--Select all trainers that are weak against a single type from a pokemon
SELECT t_name, t_type
from pokemon, typeChart, trainers
WHERE p_name = 'Bulbasaur' AND
        p_type1 = tc_type AND 
            tc_effectiveness > 1 AND 
                tc_type_against = t_type AND 
                    p_gen = t_gen;

