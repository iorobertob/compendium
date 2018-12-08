
create database compendium;
use compendium;

DELIMITER ;;
CREATE TABLE `user_info` (
  `user_id`           bigint(20)    NOT NULL AUTO_INCREMENT,
  `user_name`         varchar(45)   COLLATE utf8_bin DEFAULT NULL,
  `user_email`        varchar(45)   COLLATE utf8_bin DEFAULT NULL,
  `user_password`     varchar(127)  COLLATE utf8_bin DEFAULT NULL,
  `notificaciones`    char(8)       COLLATE utf8_bin DEFAULT NULL,
  `android_token`     char(255)     COLLATE utf8_bin DEFAULT NULL,
  `location`          char(64)      COLLATE utf8_bin DEFAULT NULL,
  `birthday`          char(32)      COLLATE utf8_bin DEFAULT NULL,
  `activity`          varchar(64)   COLLATE utf8_bin DEFAULT NULL,
  `description`      varchar(256)  COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DELIMITER ;;
CREATE TABLE `img_info` (
  `user_id`           bigint(20)    NOT NULL AUTO_INCREMENT,
  `img_url`           varchar(256)   COLLATE utf8_bin DEFAULT NULL,
  `description`       varchar(256)   COLLATE utf8_bin DEFAULT NULL,
  `type`              varchar(127)  COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
DELIMITER ;;


-- ==========================================
-- PROCEDURES
-- ==========================================
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_create_user_compendium`(
    IN p_name VARCHAR(45),
    IN p_useremail VARCHAR(45),
    IN p_password VARCHAR(127),
    IN p_description VARCHAR(256)
)
BEGIN
    if (( select exists (select 1 from user_info where user_email = p_useremail) ) OR ( select exists (select 1 from user_info where user_name = p_name) )) THEN
        select 'User Exists!';
    ELSE
        insert into user_info
        (
            user_name,
            user_email,
            user_password,
            description
        )
        values
        (
            p_name,
            p_useremail,
            p_password,
            p_description
        );
    END IF;             
END ;;
DELIMITER ;