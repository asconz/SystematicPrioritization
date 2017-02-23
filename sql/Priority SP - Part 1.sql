DROP PROCEDURE IF EXISTS priorities.sp_part1;
CREATE PROCEDURE priorities.`sp_part1`(in processDate_in date, in process_from_date date)
BEGIN
    SELECT NOW() as `BEGIN sp_part1`;


      INSERT INTO processing_status VALUES (processDate_in, 'SP Step 1 - Check if already processed on date', NOW());


SET @last_processed = (SELECT IFNULL(MAX(PROCESS_DATE), '2099-12-31') FROM priorities.process_history);


IF processDate_in != @last_processed
  THEN
      INSERT INTO process_history VALUES (processDate_in, NOW());      
      INSERT INTO processing_status VALUES (processDate_in, 'SP Step 2 - Building daily_weight_recalc', NOW());

    DROP TABLE IF EXISTS daily_weight_recalc;
    CREATE TABLE `daily_weight_recalc` (
      `TASK` varchar(50) COLLATE latin1_general_ci NOT NULL,
      `WEIGHT` tinyint(3) DEFAULT NULL COMMENT 'Weighted priority',
      `NEW_WEIGHT` tinyint(3) DEFAULT NULL COMMENT 'Weighted priority',
      `IMPORTANCE` tinyint(2) DEFAULT NULL COMMENT 'Assign value 1-10',
      `URGENCY` tinyint(2) DEFAULT NULL COMMENT 'Assign value 1-10',
      `NEW_URGENCY` tinyint(2) DEFAULT NULL COMMENT 'Assign value 1-10',
      `DIFFICULTY` tinyint(2) DEFAULT NULL COMMENT 'Assign value 1-10',
      `DT_ADDED` datetime DEFAULT NULL,
      `CURRENT_DATE` date DEFAULT NULL,
      `DATE_DUE` date DEFAULT NULL,
      `PROXIMITY` int(11) NOT NULL,
      `SINCE_ADDED` int(11) NOT NULL,
      `STATUS` varchar(50) COLLATE latin1_general_ci NOT NULL,
      `NEW_STATUS` varchar(50) COLLATE latin1_general_ci NOT NULL,
      `STATUS_ID` int(2) unsigned NOT NULL,
      `PRIORITY_ID` int(11) unsigned NOT NULL,
      PRIMARY KEY (`PRIORITY_ID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

    INSERT INTO daily_weight_recalc (
       `TASK`,
       `WEIGHT`,
       `NEW_WEIGHT`,
       `IMPORTANCE`,
       `URGENCY`,
       `DIFFICULTY`,
       `DT_ADDED`,
       `CURRENT_DATE`,
       `DATE_DUE`,
       `PROXIMITY`,
       `SINCE_ADDED`,
       `STATUS`,
       `NEW_STATUS`,
       `STATUS_ID`,
       `PRIORITY_ID`
    )  
    SELECT 
        TASK,
        WEIGHT,
        WEIGHT,
        IMPORTANCE,
        URGENCY,
        DIFFICULTY,
        DT_ADDED,
        CURDATE(),
        DATE_DUE,
        DATEDIFF(DATE_DUE, CURDATE()),
        DATEDIFF(DATE_DUE, DT_ADDED),
        s.STATUS,
        s.STATUS,
        p.STATUS_ID,
        PRIORITY_ID  
    FROM 
        priority p JOIN status s
    ON
        p.STATUS_ID = s.STATUS_ID
    WHERE
        s.STATUS IN ('Active', 'Overdue', 'Archived') AND p.DATE_DUE IS NOT NULL;  

      INSERT INTO processing_status VALUES (processDate_in, 'SP Step 2 - Update Urgency & Status by Date', NOW());

    UPDATE daily_weight_recalc
    SET 
      NEW_STATUS = 
                  CASE
                    WHEN STATUS = 'Active' AND PROXIMITY < 0 
                      THEN 'Overdue' ELSE STATUS
                  END;


    UPDATE daily_weight_recalc w, status s
    SET w.STATUS_ID = s.STATUS_ID
    WHERE w.NEW_STATUS = s.STATUS;


    UPDATE daily_weight_recalc
    SET 
      NEW_URGENCY = CASE
                  WHEN NEW_STATUS = 'Overdue' THEN 10
                  WHEN PROXIMITY < 1  AND STATUS != 'Archived' THEN 10 
                  WHEN PROXIMITY < 10 AND URGENCY < 7 THEN URGENCY + 1
                  WHEN PROXIMITY < 5  AND URGENCY < 8 THEN URGENCY + 1
                  WHEN PROXIMITY < 3  AND URGENCY < 9 THEN URGENCY + 1
                  ELSE URGENCY
               END;              

      INSERT INTO processing_status VALUES (processDate_in, 'SP Step 3 - Recalculate Priority Weights', NOW());

    UPDATE daily_weight_recalc
    SET NEW_WEIGHT = IMPORTANCE 
                      * (10 - DIFFICULTY) 
                      *  NEW_URGENCY / 5;

      INSERT INTO processing_status VALUES (processDate_in, 'SP Step 4 - Update `priority` Weight/Urgency/Status from `daily_weight_recalc`', NOW());

    UPDATE priority p, daily_weight_recalc w
    SET p.URGENCY = w.NEW_URGENCY,
        p.WEIGHT = w.NEW_WEIGHT,
        p.STATUS_ID = w.STATUS_ID
    WHERE 
        p.PRIORITY_ID = w.PRIORITY_ID;

  END IF;
  
END;
