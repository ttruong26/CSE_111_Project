--SUPER EFFECTIVE AGAINST(DOUBLE TYPE POKEMON): Double type advantage, CAN ONLY USE ON POKEMON WHERE p_type2 IS NOT NULL


SELECT DISTINCT p2.p_name
FROM pokemon p1, typeChart, pokemon p2
WHERE p1.p_name == 'Emboar' AND
            p1.p_type1 = tc_type AND
            tc_effectiveness > 1 AND
                (tc_type_against = p2.p_type1 OR
                    tc_type_against = p2.p_type2)

INTERSECT

SELECT DISTINCT p2.p_name
    FROM pokemon p1, typeChart, pokemon p2
    WHERE p1.p_name == 'Emboar' AND
                p1.p_type2 = tc_type AND
                tc_effectiveness > 1 AND
                    (tc_type_against = p2.p_type1 OR
                        tc_type_against = p2.p_type2);

--EFFECTIVE AGAINST(SINGLE TYPE POKEMON): Single type advantage
SELECT DISTINCT p2.p_name
FROM pokemon p1, typeChart, pokemon p2
WHERE p1.p_name == 'Charmander' AND
            p1.p_type1 = tc_type AND
            tc_effectiveness > 1 AND
                (tc_type_against = p2.p_type1 OR
                    tc_type_against = p2.p_type2);

--EFFECTIVE AGAINST (DOUBLE TYPE POKEMON): Single Type Advantage
SELECT DISTINCT p2.p_name
FROM pokemon p1, typeChart t1, typeChart t2, pokemon p2
WHERE p1.p_name == 'Emboar' AND
            p1.p_type1 = t1.tc_type AND
                p1.p_type2 = t2.tc_type AND
                    t1.tc_effectiveness > 1 AND
                    t2.tc_effectiveness > 1 AND 
                    (t1.tc_type_against = p2.p_type1 OR
                        t1.tc_type_against = p2.p_type2 OR
                            t2.tc_type_against = p2.p_type1 OR
                                t2.tc_type_against = p2.p_type2);

--NOT VERY EFFECTIVE AGAINST (DOUBLE TYPE POKEMON): Single Type disadvantage
SELECT DISTINCT p2.p_name
FROM pokemon p1, typeChart t1, typeChart t2, pokemon p2
WHERE p1.p_name == 'Emboar' AND
            p1.p_type1 = t1.tc_type AND
                p1.p_type2 = t2.tc_type AND
                    t1.tc_effectiveness < 1 AND
                    t2.tc_effectiveness < 1 AND 
                    (t1.tc_type_against = p2.p_type1 OR
                        t1.tc_type_against = p2.p_type2 OR
                            t2.tc_type_against = p2.p_type1 OR
                                t2.tc_type_against = p2.p_type2);

--NO EFFECT (SINGLE TYPE POKEMON): Has no effect on pokemon type
SELECT DISTINCT p2.p_name
FROM pokemon p1, typeChart, pokemon p2
WHERE p1.p_name == 'Pikachu' AND
            p1.p_type1 = tc_type AND
            tc_effectiveness = 0 AND
                (tc_type_against = p2.p_type1 OR
                    tc_type_against = p2.p_type2);

--NO EFFECT (DOUBLE TYPE POKEMON): Has no effect on pokemon type
SELECT DISTINCT p2.p_name
FROM pokemon p1, typeChart, pokemon p2
WHERE p1.p_name == 'Emboar' AND
            p1.p_type1 = tc_type AND
            tc_effectiveness == 0 AND
                (tc_type_against = p2.p_type1 OR
                    tc_type_against = p2.p_type2)

UNION

SELECT DISTINCT p2.p_name
    FROM pokemon p1, typeChart, pokemon p2
    WHERE p1.p_name == 'Emboar' AND
                p1.p_type2 = tc_type AND
                tc_effectiveness == 0 AND
                    (tc_type_against = p2.p_type1 OR
                        tc_type_against = p2.p_type2);

--- List out all of the possible types in alphabetical order and there effectiveness on a given pokemon
--- Takes into account dual types of a pokemon and will list effectiveness accordingly (ie. grass | 4.0 for swampert[ground, water])
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

--- Given a certain type (ie. 'fire'), list all of the pokemon that have a weakness to that type. 
--- Takes into consideration the dual typing of pokemon. (ie. ice is weak to fire, and dragon is not. So a dragon/ice pokemon is neutral against fire)

SELECT p.p_name
FROM pokemon p
JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against AND tc1.tc_type = 'fire'
LEFT JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against AND tc2.tc_type = 'fire'
WHERE (tc1.tc_effectiveness > 1 AND (p.p_type2 IS NULL OR tc2.tc_effectiveness >= 1))
   OR (p.p_type2 IS NOT NULL AND tc1.tc_effectiveness >= 1 AND tc2.tc_effectiveness > 1)
GROUP BY p.p_name;


-- MODIFIED VERSION: Takes the name of a given pokemon and finds the same result. 
SELECT p.p_name
FROM pokemon p
JOIN typeChart tc1 ON p.p_type1 = tc1.tc_type_against
LEFT JOIN typeChart tc2 ON p.p_type2 = tc2.tc_type_against
WHERE (tc1.tc_type = (SELECT p_type1 FROM pokemon WHERE p_name = 'Charmander') AND tc1.tc_effectiveness > 1)
  AND (p.p_type2 IS NULL OR tc2.tc_type = (SELECT p_type1 FROM pokemon WHERE p_name = 'Charmander') AND tc2.tc_effectiveness >= 1)
GROUP BY p.p_name;


