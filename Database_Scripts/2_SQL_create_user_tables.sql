
--Sequence: sec_tb_groups_id_row

DROP SEQUENCE IF EXISTS sec_tb_groups_id_row CASCADE;

CREATE SEQUENCE sec_tb_groups_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_groups_id_row
  OWNER TO dbadmin;

-- Sequence: sec_tb_users_id_row

DROP SEQUENCE IF EXISTS sec_tb_users_id_row CASCADE;

CREATE SEQUENCE sec_tb_users_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_users_id_row
  OWNER TO dbadmin;

-- Sequence: sec_tb_users_id_row

DROP SEQUENCE IF EXISTS sec_tb_user_status_id_row CASCADE;

CREATE SEQUENCE sec_tb_user_status_id_row
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE sec_tb_user_status_id_row
  OWNER TO dbadmin;
  
-- Create table: tb_groups
-- ADM --> User with administrative rights
-- USR --> User with read only rights
DROP TABLE IF EXISTS tb_groups CASCADE;
CREATE TABLE tb_groups(
	id_row integer DEFAULT NEXTVAL('sec_tb_groups_id_row') NOT NULL,
	id_group VARCHAR(10) UNIQUE NOT NULL,
	name_group VARCHAR(50) NOT NULL,
	level_group smallint NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
CONSTRAINT primary_key_groups PRIMARY KEY (id_group)
);

-- Create table: tb_status
-- ENB --> Enabled user
-- DIS --> Disabled user

DROP TABLE IF EXISTS tb_user_status CASCADE;
CREATE TABLE tb_user_status(
	id_row integer DEFAULT NEXTVAL('sec_tb_status_id_row') NOT NULL,
	status_user VARCHAR(3) UNIQUE NOT NULL,
	description_status VARCHAR(50) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
CONSTRAINT primary_key_user_status PRIMARY KEY (status_user)
);

-- Create table: tb_users
-- Admin --> User administrator
DROP TABLE IF EXISTS tb_users CASCADE;
CREATE TABLE tb_users(
	id_row integer DEFAULT NEXTVAL('sec_tb_users_id_row') NOT NULL, 
	id_user VARCHAR(10) UNIQUE NOT NULL,
	name_user VARCHAR(50) NOT NULL,
	mail_user VARCHAR(50) NOT NULL,
	id_group VARCHAR(10) NOT NULL,
	status_user VARCHAR(3) NOT NULL,
	pass_user VARCHAR(10) NOT NULL,
	create_date timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
CONSTRAINT primary_key_users PRIMARY KEY (id_user),
CONSTRAINT foreing_key_user_to_group FOREIGN KEY (id_group) REFERENCES tb_groups (id_group),
CONSTRAINT foreing_key_user_to_status FOREIGN KEY (status_user) REFERENCES tb_user_status (status_user)
);
--Default groups insert into tb_grop table
INSERT INTO tb_groups(id_row, id_group, name_group, level_group, create_date) VALUES (DEFAULT, 'ADM','Administrator',10,DEFAULT);
INSERT INTO tb_groups(id_row, id_group, name_group, level_group, create_date) VALUES (DEFAULT, 'USR','User',1,DEFAULT);
--Default status insert into tb_status table
INSERT INTO tb_user_status(id_row, status_user, description_status, create_date)VALUES (DEFAULT,'ENB','Enabled',DEFAULT);
INSERT INTO tb_user_status(id_row, status_user, description_status, create_date)VALUES (DEFAULT,'DIS','Disabled',DEFAULT);
--Default user insert into tb_users table
INSERT INTO tb_users(id_row, id_user, name_user, mail_user, id_group, status_user, pass_user, create_date) VALUES (DEFAULT,'admin','administrator','admin@admin.local','ADM','ENB','admin',DEFAULT);
INSERT INTO tb_users(id_row, id_user, name_user, mail_user, id_group, status_user, pass_user, create_date) VALUES (DEFAULT,'machine','default machine','machine@machine.local','USR','ENB','machine',DEFAULT);


