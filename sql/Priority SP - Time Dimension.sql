DROP PROCEDURE IF EXISTS priorities.fill_date_dimension;
CREATE PROCEDURE priorities.`fill_date_dimension`(IN startdate DATE,IN stopdate DATE)
BEGIN
    
    DECLARE currentdate DATE;
    SET currentdate = startdate;
    
    WHILE currentdate < stopdate DO
        INSERT INTO time_dimension VALUES (
                        YEAR(currentdate)*10000+MONTH(currentdate)*100 + DAY(currentdate),
                        currentdate,
                        YEAR(currentdate),
                        MONTH(currentdate),
                        DAY(currentdate),
                        QUARTER(currentdate),
                        WEEKOFYEAR(currentdate),
                        DATE_FORMAT(currentdate,'%W'),
                        DATE_FORMAT(currentdate,'%M'),
                        'F',
                        CASE DAYOFWEEK(currentdate) WHEN 1 THEN 'T' WHEN 7 THEN 'T' ELSE 'F' END,
                        NULL);
        SET currentdate = ADDDATE(currentdate,INTERVAL 1 DAY);
    END WHILE;

END;
