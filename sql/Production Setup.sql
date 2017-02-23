##################
## SCHEMA SETUP ##
##################

CREATE SCHEMA IF NOT EXISTS priorities
CHARACTER SET latin1 
COLLATE latin1_general_ci;

USE priorities;
-- -------------------------------------------------------
-- -------------------------------------------------------

#################
## TABLE SETUP ##
#################

CREATE TABLE IF NOT EXISTS `process_history` (
  `PROCESS_DATE` date NOT NULL,
  `TIME_CALLED` datetime NOT NULL,
  PRIMARY KEY (`PROCESS_DATE`, `TIME_CALLED`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
-- ------------
-- ------------

CREATE TABLE IF NOT EXISTS `processing_status` (
  `PROCESS_DATE` date DEFAULT NULL,
  `STATUS` varchar(256) COLLATE latin1_general_ci NOT NULL DEFAULT '',
  `TIME_PROCESSED` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
-- ------------
-- ------------

CREATE TABLE IF NOT EXISTS `category` (
  `CATEGORY` varchar(20) COLLATE latin1_general_ci NOT NULL,
  `CATEGORY_ID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`CATEGORY_ID`),
  UNIQUE KEY (`CATEGORY`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

    INSERT IGNORE INTO category (CATEGORY)
    VALUES ('Career'), ('Finance'), ('Projects'), ('Misc');
-- ------------
-- ------------

CREATE TABLE IF NOT EXISTS `status` (
  `STATUS` varchar(25) COLLATE latin1_general_ci NOT NULL,
  `STATUS_ID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`STATUS_ID`),
  UNIQUE KEY (`STATUS`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;

    INSERT IGNORE INTO status (STATUS) 
    VALUES ('Active'), ('Overdue'), ('Archived'), ('Completed'), ('Deleted');
-- ------------
-- ------------

CREATE TABLE IF NOT EXISTS `history` (
  `COMMENT` varchar(256) COLLATE latin1_general_ci NOT NULL DEFAULT '',
  `DT_MODIFIED` datetime DEFAULT NULL,
  `CATEGORY_ID` tinyint(3) unsigned NOT NULL,
  `STATUS_ID` tinyint(3) unsigned NOT NULL,
  `PRIORITY_ID` int(11) unsigned NOT NULL,
  `HIST_ID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`HIST_ID`),
  KEY `idx_priority_id` (`PRIORITY_ID`),
  KEY `idx_fk_category_id` (`CATEGORY_ID`),
  KEY `idx_fk_status_id` (`STATUS_ID`),
  CONSTRAINT `fk_history_category` FOREIGN KEY (`CATEGORY_ID`) REFERENCES `category` (`CATEGORY_ID`),
  CONSTRAINT `fk_history_status` FOREIGN KEY (`STATUS_ID`) REFERENCES `status` (`STATUS_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
-- ------------
-- ------------

CREATE TABLE IF NOT EXISTS `priority` (
  `TASK` varchar(50) COLLATE latin1_general_ci NOT NULL,
  `WEIGHT` tinyint(3) DEFAULT NULL COMMENT 'Weighted priority',
  `CATEGORY_ID` tinyint(3) unsigned NOT NULL DEFAULT 1,
  `DESCRIPTION` varchar(256) COLLATE latin1_general_ci NOT NULL DEFAULT '',
  `IMPORTANCE` tinyint(2) DEFAULT NULL COMMENT 'Assign value 1-10',
  `URGENCY` tinyint(2) DEFAULT NULL COMMENT 'Assign value 1-10',
  `DIFFICULTY` tinyint(2) DEFAULT NULL COMMENT 'Estimate required time/effort from 1-10',
  `DT_ADDED` datetime DEFAULT NULL,
  `DATE_DUE` date DEFAULT NULL,
  `DT_COMPLETE` datetime DEFAULT NULL,
  `STATUS_ID` tinyint(3) unsigned NOT NULL DEFAULT 1,
  `HIST_ID` int(11) unsigned NOT NULL DEFAULT 0,
  `PRIORITY_ID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`PRIORITY_ID`),
  KEY `idx_fk_category_id` (`CATEGORY_ID`),
  KEY `idx_fk_status_id` (`STATUS_ID`),
  KEY `idx_fk_history_id` (`HIST_ID`),
  CONSTRAINT `fk_priority_category` FOREIGN KEY (`CATEGORY_ID`) REFERENCES `category` (`CATEGORY_ID`),
  CONSTRAINT `fk_priority_status` FOREIGN KEY (`STATUS_ID`) REFERENCES `status` (`STATUS_ID`),
  CONSTRAINT `fk_priority_history` FOREIGN KEY (`HIST_ID`) REFERENCES `history` (`HIST_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
-- -------------------------------------------------------
-- -------------------------------------------------------

###################
## TRIGGER SETUP ##
###################

### BEFORE PRIORITY INSERT ###
DROP TRIGGER IF EXISTS before_priority_insert;
CREATE TRIGGER before_priority_insert
  BEFORE INSERT ON priority FOR EACH ROW
BEGIN

  INSERT INTO processing_status VALUES (CURDATE(), 'Enter TRIGGER: before_priority_insert', NOW()); 
    SET NEW.DESCRIPTION = IFNULL(NEW.DESCRIPTION, '');
    SET NEW.STATUS_ID = IFNULL(NEW.STATUS_ID, 1);
    SET NEW.CATEGORY_ID = IFNULL(NEW.CATEGORY_ID, 4);
    
  INSERT INTO processing_status VALUES (CURDATE(), CONCAT('Before Insert: New.STATUS_ID = ', NEW.STATUS_ID), NOW());  
    IF NEW.DT_ADDED IS NULL 
      THEN 
          SET NEW.DT_ADDED = NOW();
    
          INSERT INTO history (COMMENT, DT_MODIFIED, CATEGORY_ID, STATUS_ID, PRIORITY_ID)
          VALUES (CONCAT("Added: '", NEW.TASK, "'"), NOW(), NEW.CATEGORY_ID, NEW.STATUS_ID, NEW.PRIORITY_ID);
        
      ELSE    
          INSERT INTO history (COMMENT, DT_MODIFIED, CATEGORY_ID, STATUS_ID, PRIORITY_ID)
          VALUES (CONCAT("Repopulated: '", NEW.TASK, "'"), NOW(), NEW.CATEGORY_ID, NEW.STATUS_ID, NEW.PRIORITY_ID);

    END IF;
    
    SET @HIST_ID = (SELECT MAX(HIST_ID) FROM history);
    SET NEW.HIST_ID = @HIST_ID;

END;
-- ------------
-- ------------

### AFTER PRIORITY INSERT ###
DROP TRIGGER IF EXISTS after_priority_insert;
CREATE TRIGGER after_priority_insert
  AFTER INSERT ON priority FOR EACH ROW
BEGIN
  INSERT INTO processing_status VALUES (CURDATE(), 'Enter TRIGGER: after_priority_insert', NOW());

    UPDATE history SET PRIORITY_ID = NEW.PRIORITY_ID
    WHERE HIST_ID = NEW.HIST_ID
    AND PRIORITY_ID = 0;

END;
-- ------------
-- ------------

### BEFORE PRIORITY DELETE ###
DROP TRIGGER IF EXISTS before_priority_delete;
CREATE TRIGGER before_priority_delete
  BEFORE DELETE ON priority FOR EACH ROW
BEGIN
  INSERT INTO processing_status VALUES (CURDATE(), 'Enter TRIGGER: before_priority_delete', NOW());
    
    INSERT INTO history (COMMENT, DT_MODIFIED, CATEGORY_ID, STATUS_ID, PRIORITY_ID)
    VALUES (CONCAT("DELETED: '", OLD.TASK,"'"), NOW(), OLD.CATEGORY_ID, '5', OLD.PRIORITY_ID);
    
END;
-- ------------
-- ------------

### BEFORE PRIORITY UPDATE ###
DROP TRIGGER IF EXISTS before_priority_update;
CREATE TRIGGER before_priority_update
  BEFORE UPDATE ON priority FOR EACH ROW
BEGIN
  INSERT INTO processing_status VALUES (CURDATE(), 'Enter TRIGGER: before_priority_update', NOW());
    #Outer IF
    IF !(NEW.TASK <=> OLD.TASK AND NEW.WEIGHT <=> OLD.WEIGHT AND NEW.CATEGORY_ID <=> OLD.CATEGORY_ID
          AND NEW.DESCRIPTION <=> OLD.DESCRIPTION AND NEW.IMPORTANCE <=> OLD.IMPORTANCE 
          AND NEW.URGENCY <=> OLD.URGENCY AND NEW.DIFFICULTY <=> OLD.DIFFICULTY 
          AND NEW.DT_ADDED <=> OLD.DT_ADDED AND NEW.DATE_DUE <=> OLD.DATE_DUE 
          AND NEW.DT_COMPLETE <=> OLD.DT_COMPLETE AND NEW.STATUS_ID <=> OLD.STATUS_ID) 
      THEN
        INSERT INTO processing_status VALUES (CURDATE(), 'In TRIGGER: before_priority_update - Within First IF', NOW());        
          
          IF !(NEW.STATUS_ID <=> OLD.STATUS_ID) #Middle IF
            THEN
              INSERT INTO processing_status VALUES (CURDATE(), 'In TRIGGER: before_priority_update - Within Second IF - New STATUS_ID', NOW());
              
              INSERT INTO history (COMMENT, DT_MODIFIED, CATEGORY_ID, STATUS_ID, PRIORITY_ID)
              VALUES (CONCAT(CASE
                              WHEN NEW.STATUS_ID = 4 THEN "Completed: '"
                              WHEN NEW.STATUS_ID = 3 THEN "Archived: '"
                              WHEN NEW.STATUS_ID = 2 THEN "Overdue: '"
                              WHEN NEW.STATUS_ID = 1 THEN "Re-Activated: '" END, NEW.TASK, "'")
                      , NOW(), NEW.CATEGORY_ID, NEW.STATUS_ID, OLD.PRIORITY_ID);

                IF NEW.STATUS_ID = 4 #Inner IF        
                  THEN 
                    INSERT INTO processing_status VALUES (CURDATE(), 'In TRIGGER: before_priority_update - Within Third IF', NOW());   
                    
                      SET NEW.DT_COMPLETE = NOW();
                END IF;
          
          ELSEIF !(NEW.DATE_DUE <=> OLD.DATE_DUE) AND NEW.DATE_DUE >= CURDATE() AND OLD.STATUS_ID = 2
            THEN
              INSERT INTO processing_status VALUES (CURDATE(), 'In TRIGGER: before_priority_update - Within Second IF - ELSEIF', NOW());  
                SET NEW.STATUS_ID = 1;
                
                INSERT INTO history (COMMENT, DT_MODIFIED, CATEGORY_ID, STATUS_ID, PRIORITY_ID)
                VALUES (CONCAT("Overdue->Active; New Due-date ", NEW.DATE_DUE, ": '", NEW.TASK, "'")
                        , NOW() , NEW.CATEGORY_ID, NEW.STATUS_ID, OLD.PRIORITY_ID);
            
          ELSE
              INSERT INTO history (COMMENT, DT_MODIFIED, CATEGORY_ID, STATUS_ID, PRIORITY_ID)
              VALUES (CONCAT("Updated: '", NEW.TASK, "'"), NOW(), NEW.CATEGORY_ID, NEW.STATUS_ID, OLD.PRIORITY_ID);
          
          END IF; #Middle

      SET @HIST_ID = (SELECT MAX(HIST_ID) FROM history);
      SET NEW.HIST_ID = @HIST_ID;

    END IF; #Outer

END;
-- -------------------------------------------------------
-- -------------------------------------------------------