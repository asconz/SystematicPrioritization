DROP PROCEDURE IF EXISTS priorities.process_routine;
CREATE PROCEDURE priorities.`process_routine`(in processDate_in date)
BEGIN

insert into processing_status values (processDate_in, 'START - Process Routine', now());

-- Monday - Thursday, reprocess rolling 5 days -- Friday nights reprocess rolling month
SET @days_to_process =
	CASE dayofweek(processDate_in)
		WHEN 6 THEN 30
		ELSE 5
	END;

insert into processing_status values (processDate_in, 'Step 1 - START sp_part1', now());
call sp_part1(processDate_in,date_sub(processDate_in, INTERVAL @days_to_process DAY));
insert into processing_status values (processDate_in, 'Step 1.X - END sp_part1', now());
-- 
-- insert into processing_status values (processDate_in, 'Step 2 - START sp_part2', now());
-- call sp_part2(processDate_in,date_sub(processDate_in, INTERVAL @days_to_process DAY));
-- insert into processing_status values (processDate_in, 'Step 2.X - END sp_part2', now());

insert into processing_status values (processDate_in, 'End Process Routine', now());

END;
