
----------------------------------------------------------------------------------------------------------------------------
------------------------------------------DELETE TABLES AND SEQUENCES-------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
DROP TABLE IF EXISTS href_routing_model CASCADE;
DROP TABLE IF EXISTS href_routing_cell CASCADE;
DROP TABLE IF EXISTS href_cell_line CASCADE;
DROP TABLE IF EXISTS his_proc_item CASCADE;
DROP TABLE IF EXISTS tb_items CASCADE;
DROP TABLE IF EXISTS tb_status CASCADE;
DROP TABLE IF EXISTS tb_models CASCADE;
DROP TABLE IF EXISTS tb_routings CASCADE;
DROP TABLE IF EXISTS tb_cells CASCADE;
DROP TABLE IF EXISTS tb_lines CASCADE;


DROP SEQUENCE IF EXISTS sec_href_cell_line_id_row CASCADE; 
DROP SEQUENCE IF EXISTS sec_href_routing_cell_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_href_cell_line_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_his_proc_item_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_tb_items_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_tb_status_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_tb_models_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_tb_routings_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_tb_cells_id_row CASCADE;
DROP SEQUENCE IF EXISTS sec_tb_lines_id_row CASCADE;
 


----------------------------------------------------------------------------------------------------------------------------
------------------------------------------CREATE TABLES AND SEQUENCES-------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------
--Sequence: sec_tb_lines_id_row
DROP SEQUENCE IF EXISTS sec_tb_lines_id_row CASCADE;   
CREATE SEQUENCE sec_tb_lines_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_lines_id_row
  OWNER TO rupasgon;
  
--Create table: tb_lines
DROP TABLE IF EXISTS tb_lines CASCADE;
CREATE TABLE tb_lines(
	id_row integer DEFAULT NEXTVAL('sec_tb_lines_id_row'),
	line_id varchar(50) UNIQUE NOT NULL,
	description_line varchar(50) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
CONSTRAINT primary_key_lines PRIMARY KEY (line_id)
);
---------------------------------------------------------------------------------------------------------------------------- 
--Sequence: sec_tb_cells_id_row
DROP SEQUENCE IF EXISTS sec_tb_cells_id_row CASCADE;   
CREATE SEQUENCE sec_tb_cells_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_cells_id_row
  OWNER TO rupasgon;
    
--Create table: tb_cells
DROP TABLE IF EXISTS tb_cells CASCADE;
CREATE TABLE tb_cells(
	id_row integer DEFAULT NEXTVAL('sec_tb_cells_id_row'),
	cell_id varchar(50) UNIQUE NOT NULL,
	description_cell varchar(50) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
CONSTRAINT primary_key_cells PRIMARY KEY (cell_id)
);

----------------------------------------------------------------------------------------------------------------------------
--Sequence: sec_tb_routings_id_row
DROP SEQUENCE IF EXISTS sec_tb_routings_id_row CASCADE;   
CREATE SEQUENCE sec_tb_routings_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_routings_id_row
  OWNER TO rupasgon;
  
-- Create table: tb_routings
DROP TABLE IF EXISTS tb_routings CASCADE;
CREATE TABLE tb_routings(
	id_row integer DEFAULT NEXTVAL('sec_tb_routings_id_row') NOT NULL,
	routing_id varchar(50) UNIQUE NOT NULL,
	description_routing varchar(50) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
CONSTRAINT primary_key_routings PRIMARY KEY (routing_id)
);

----------------------------------------------------------------------------------------------------------------------------
--Sequence: sec_tb_models_id_row
DROP SEQUENCE IF EXISTS sec_tb_models_id_row CASCADE;   
CREATE SEQUENCE sec_tb_models_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_models_id_row
  OWNER TO rupasgon;
  
-- Create table: tb_models
DROP TABLE IF EXISTS tb_models CASCADE;
CREATE TABLE tb_models(
	id_row integer DEFAULT NEXTVAL('sec_tb_models_id_row') NOT NULL,
	model_id varchar(50) UNIQUE NOT NULL,
	description_model varchar(50) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
CONSTRAINT primary_key_models PRIMARY KEY (model_id)
);

----------------------------------------------------------------------------------------------------------------------------
--Sequence: sec_tb_status_id_row
DROP SEQUENCE IF EXISTS sec_tb_status_id_row CASCADE;   
CREATE SEQUENCE sec_tb_status_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_status_id_row
  OWNER TO rupasgon;
  
--Create table: tb_status
DROP TABLE IF EXISTS tb_status CASCADE;
CREATE TABLE tb_status(
	id_row integer DEFAULT NEXTVAL('sec_tb_status_id_row'),
	status_id varchar(50) NOT NULL,
	description_status varchar(50) NOT NULL,
CONSTRAINT primary_key_status PRIMARY KEY (status_id)
);

---------------------------------------------------------------------------------------------------------------------------
--Sequence: sec_tb_items_id_row
DROP SEQUENCE IF EXISTS sec_tb_items_id_row CASCADE;
CREATE SEQUENCE sec_tb_items_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_items_id_row
  OWNER TO rupasgon;

-- Create table: tb_items
DROP TABLE IF EXISTS tb_items CASCADE;
CREATE TABLE tb_items(
	id_row integer DEFAULT NEXTVAL('sec_tb_items_id_row') NOT NULL,
	item_id varchar(50) NOT NULL,
	model_id varchar(50) NOT NULL,
	line_id varchar(50) NOT NULL,
	location_id smallint NOT NULL,
	cell_id varchar(50) NOT NULL,
	id_user varchar(50) DEFAULT 'machine' NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
	last_test_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
	status_id varchar(50) NOT NULL,
	value1_int integer,
	value2_int integer,
	value3_int integer,
	value4_int integer,
	value5_int integer,
	value1_str varchar(50),
	value2_str varchar(50),
	value3_str varchar(50),
	value4_str varchar(50),
	value5_str varchar(50),
CONSTRAINT primary_key_items PRIMARY KEY (item_id),
CONSTRAINT foreign_key_item_to_model FOREIGN KEY (model_id) REFERENCES tb_models (model_id),
CONSTRAINT foreign_key_item_to_line FOREIGN KEY (line_id) REFERENCES tb_lines (line_id),
CONSTRAINT foreign_key_item_to_status FOREIGN KEY (status_id) REFERENCES tb_status (status_id),
CONSTRAINT foreign_key_item_to_cells FOREIGN KEY (cell_id) REFERENCES tb_cells (cell_id),
CONSTRAINT foreign_key_item_to_users FOREIGN KEY (id_user) REFERENCES tb_users (id_user)
);
-----------------------------------------------------------------------------------------------------
--Sequence: sec_tb_items_id_row
DROP SEQUENCE IF EXISTS sec_his_proc_item_id_row CASCADE;
CREATE SEQUENCE sec_his_proc_item_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_his_proc_item_id_row
  OWNER TO rupasgon;

-- Create table: his_proc_item
DROP TABLE IF EXISTS his_proc_item CASCADE;
CREATE TABLE his_proc_item(
	id_row integer DEFAULT NEXTVAL('sec_his_proc_item_id_row') NOT NULL,
	item_id varchar(50) NOT NULL,
	model_id varchar(50) NOT NULL,
	line_id varchar(50) NOT NULL,
	location_id smallint NOT NULL,
	cell_id varchar(50) NOT NULL,
	id_user varchar(50) DEFAULT 'machine' NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
	last_test_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
	status_id varchar(50) NOT NULL,
	value1_int integer,
	value2_int integer,
	value3_int integer,
	value4_int integer,
	value5_int integer,
	value1_str varchar(50),
	value2_str varchar(50),
	value3_str varchar(50),
	value4_str varchar(50),
	value5_str varchar(50)
);

------------------------------------------------------------------------------------------------------------------
----------------------------CREATE REFERENCES TABLES AND THEIR SEQUENCES------------------------------------------
------------------------------------------------------------------------------------------------------------------
--Sequence: sec_href_cell_line_id_row
DROP SEQUENCE IF EXISTS sec_href_cell_line_id_row CASCADE;   
CREATE SEQUENCE sec_href_cell_line_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_href_cell_line_id_row
  OWNER TO rupasgon;
  
-- Create table: href_cell_line
DROP TABLE IF EXISTS href_cell_line CASCADE;
CREATE TABLE href_cell_line(
	id_row integer DEFAULT NEXTVAL('sec_href_cell_line_id_row'),
	cell_id varchar(50) NOT NULL,
	line_id varchar(50) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
CONSTRAINT foreign_key_href_cell_to_cell FOREIGN KEY (cell_id) REFERENCES tb_cells(cell_id),
CONSTRAINT foreign_key_href_line_to_line FOREIGN KEY (line_id) REFERENCES tb_lines(line_id)
);
------------------------------------------------------------------------------------------------------------------
--Sequence: sec_href_routing_cell_id_row
DROP SEQUENCE IF EXISTS sec_href_routing_cell_id_row CASCADE;   
CREATE SEQUENCE sec_href_routing_cell_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_href_routing_cell_id_row
  OWNER TO rupasgon;
  
--Create table: href_routing_cell
DROP TABLE IF EXISTS href_routing_cell CASCADE;
CREATE TABLE href_routing_cell(
	id_row integer DEFAULT NEXTVAL('sec_href_routing_cell_id_row') NOT NULL,
	routing_id varchar(50) NOT NULL,
	cell_id varchar(50) NOT NULL,
	id_location smallint NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0),
CONSTRAINT foreign_key_href_cell_to_cell FOREIGN KEY (cell_id) REFERENCES tb_cells(cell_id)
);
-------------------------------------------------------------------------------------------------------------------
--Sequence: sec_href_model_routing_id_row
DROP SEQUENCE IF EXISTS sec_href_model_routing_id_row CASCADE;   
CREATE SEQUENCE sec_href_model_routing_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_href_model_routing_id_row
  OWNER TO rupasgon;
  
--Create table: href_model_routing
DROP TABLE IF EXISTS href_routing_model CASCADE;
CREATE TABLE href_routing_model(
	id_row integer DEFAULT NEXTVAL('sec_href_model_routing_id_row') NOT NULL,
	routing_id varchar(50) NOT NULL,
	model_id varchar(50) NOT NULL,
	location_id smallint NOT NULL,
CONSTRAINT foreign_key_href_routing_to_routing FOREIGN KEY (routing_id) REFERENCES tb_routings (routing_id),
CONSTRAINT foreign_key_href_routing_to_model FOREIGN KEY (model_id) REFERENCES tb_models (model_id)
);

-------------------------------------------------------------------------------------------------------------------
------------------------INSERTS DEFAULTS VALUES INTO TABLES--------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'PASS','Item in PASS status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'FAIL','Item in PASS status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'OK','Item in PASS status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'NOK','Item in FAIL status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'SCRAPPED','Item in SCRAPPED status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'REWORK','Item in REWORK status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'PACKED','Item in PACKED status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'QUARANTINED','Item in QUARANTINED status');
INSERT INTO tb_status(id_row, status_id, description_status) VALUES (DEFAULT,'WAITING CHECK','Item WAINTING a CHECK status');
