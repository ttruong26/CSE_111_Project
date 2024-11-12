--Moves 

--View Individual Move Stats
SELECT *
FROM moves
WHERE indentifier = '?'


--Filter Moves by Pokemon
SELECT identifier 
FROM moves,pokemon, pokemon_moves
WHERE pokemon_id = p_id
AND move_id = id
AND pokemon = 'Bulbasaur'



--FIlter Moves by Type
Select identifier
From moves
WHERE type_id = 1


--Filter Moves Effective Against Type
Select identifier 
FROM moves,typeChart
WHERE type_id = tc_type
AND tc_effectiveness = 1.5 
AND tc_type_against = '?'


--Filter Moves Ineffective Against Type
Select identifier 
FROM moves,typeChart
WHERE type_id = tc_type
AND tc_effectiveness = 0.5
AND tc_type_against = '?'



--Filter Moves Super Effecitve Against Type 
Select identifier 
FROM moves,typeChart
WHERE type_id = tc_type
AND tc_effectiveness = 2
AND tc_type_against = '?'



--FIlter Moves Super Ineffective Against Type 
Select identifier 
FROM moves,typeChart
WHERE type_id = tc_type
AND tc_effectiveness = 0
AND tc_type_against = '?'