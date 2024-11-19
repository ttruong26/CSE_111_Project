--TRAINER SQL

--Individual Trainer Information

SELECT * 
FROM trainers
WHERE t_name = ''

--Trainer By Region

Select t_name as Trainer
From trianers,region
WHERE t_region = r_region_name

--Trainer By Type

Select t_name as Trainer
FROM trainers
WHERE t_type = 'Fire'

--Trainer By Pokemon

SELECT t_name as Trainer
From trainers,pokemon,trainers_to_pokemon
WHERE tp_trainer = t_name
AND tp_pokemon = p_name





