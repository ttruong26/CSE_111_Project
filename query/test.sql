
-- View all trainers that belong to " " region. 
SELECT t_name 
FROM trainers
WHERE t_region = 'Kanto';

-- View all the abilities of " " pokemon
SELECT pa_ability1, pa_ability2, pa_hidden_ability 
FROM pokemon_to_abilities
WHERE pa_pokemon == ?;

--List all region information
SELECT * 
FROM region;

--List all the pokemon that belong to the " " trainer
SELECT DISTINCT t1.tp_pokemon
FROM trainer_to_pokemon t1
WHERE t1.tp_trainer == ?;

--List all of the pokemon in the evolution chain of pikachu
SELECT p2.p_name
FROM pokemon p1, pokemon p2 
WHERE p1.p_name == 'Pikachu' AND 
p1.p_evo_species = p2.p_evo_species
ORDER BY p2.p_evolution_stage ASC


-- List all of the ingame stats of pikachu
SELECT p_hp, p_attack, p_defense, p_sp_attack, p_sp_defense, p_speed, p_base_total
FROM pokemon
WHERE p_name = 'Pikachu';

--Lists all of the types in alpha order. Also lists the given effectiveness multiplier of the type on the current pokemon.
SELECT tc_type, MAX(tc_effectiveness) * MIN(tc_effectiveness) AS effectiveness_multiplier
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

--Find the name of all pokemon that are weak against a single type from bulbasaur
SELECT p.p_name
FROM pokemon p
JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against
LEFT JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against
WHERE (tc1.tc_type = (SELECT p_type1 FROM pokemon WHERE p_name = 'Bulbasaur') AND tc1.tc_effectiveness > 1)
AND (p.p_type2 IS NULL OR tc2.tc_type = (SELECT p_type1 FROM pokemon WHERE p_name = 'Bulbasaur') AND tc2.tc_effectiveness >= 1)
GROUP BY p.p_name;

--Find the name of all pokemon that are weak against the second type of bulbasaur
SELECT p.p_name
FROM pokemon p
JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against AND tc1.tc_type = (SELECT p_type2 FROM pokemon WHERE p_name = 'Bulbasaur')
LEFT JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against AND tc2.tc_type = (SELECT p_type2 FROM pokemon WHERE p_name = 'Bulbasaur')
WHERE (tc1.tc_effectiveness > 1 AND (p.p_type2 IS NULL OR (tc2.tc_effectiveness IS NULL OR tc2.tc_effectiveness >= 1)))
OR (p.p_type2 IS NOT NULL AND tc2.tc_effectiveness > 1 AND tc1.tc_effectiveness >= 1)
GROUP BY p.p_name;

--Select all trainers that are weak against a single type from a pokemon
SELECT t_name, t_type
from pokemon, typeChart, trainers
WHERE p_name = 'Bulbasaur' AND
        p_type1 = tc_type AND 
            tc_effectiveness > 1 AND 
                tc_type_against = t_type AND 
                    p_gen = t_gen;

