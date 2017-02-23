DROP PROCEDURE IF EXISTS priorities.sp_part2;
CREATE PROCEDURE priorities.`sp_part2`(in processDate_in date, in process_from_date date)
BEGIN

    SELECT NOW() as `BEGIN sp_part2`;

      INSERT INTO processing_status VALUES (processDate_in, 'SP_Part2 - Step 1 - Building time_dimension', NOW());


DROP TABLE IF EXISTS time_dimension;
CREATE TABLE time_dimension (
        `ID`                      INTEGER PRIMARY KEY,  -- year*10000+month*100+day
        `DB_DATE`                 DATE NOT NULL,
        `YEAR`                    INTEGER NOT NULL,
        `MONTH`                   INTEGER NOT NULL, -- 1 to 12
        `DAY`                     INTEGER NOT NULL, -- 1 to 31
        `QUARTER`                 INTEGER NOT NULL, -- 1 to 4
        `WEEK`                    INTEGER NOT NULL, -- 1 to 52/53
        `DAY_NAME`                VARCHAR(9) NOT NULL, -- 'Monday', 'Tuesday'...
        `MONTH_NAME`              VARCHAR(9) NOT NULL, -- 'January', 'February'...
        `HOLIDAY_FLAG`            CHAR(1) DEFAULT 'F' CHECK (holiday_flag IN ('T', 'F')),
        `WEEKEND_FLAG`            CHAR(1) DEFAULT 'F' CHECK (weekday_flag IN ('T', 'F')),
        `EVENT`                   VARCHAR(50),
        `PRIORITY_ID`             int(11) unsigned DEFAULT NULL, ## need to link to fill_date_dimension from priority/history
        UNIQUE td_ymd_idx (`YEAR`,`MONTH`,`DAY`),
        UNIQUE td_dbdate_idx (`DB_DATE`)
) ENGINE=MyISAM;

      INSERT INTO processing_status VALUES (processDate_in, 'SP_Part2 - Step 2 - Populate time_dimension from history', NOW());


-- CALL fill_date_dimension('1991-07-09',curdate());  # Populate calendar table with historical priorities/events/accomplishments


END;
