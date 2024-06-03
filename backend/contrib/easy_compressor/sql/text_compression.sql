CREATE TABLE `text_compression` (
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`before_size` INT(10) NOT NULL DEFAULT '0',
	`after_size` INT(10) NOT NULL DEFAULT '0',
	`after_text` LONGTEXT NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`ratio` DECIMAL(8,4) NOT NULL DEFAULT '0',
	`algo_type` VARCHAR(50) NOT NULL DEFAULT '8' COLLATE 'utf8mb4_0900_ai_ci',
	`options` VARCHAR(1000) NOT NULL DEFAULT '' COLLATE 'utf8mb4_0900_ai_ci',
	`tb_abbr` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'utf8mb4_0900_ai_ci',
	`pk_val` VARCHAR(500) NOT NULL DEFAULT '' COLLATE 'utf8mb4_0900_ai_ci',
	`col_name` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'utf8mb4_0900_ai_ci',
	`pk_hash` BIGINT(19) NOT NULL DEFAULT '0',
	`sign_hash` BIGINT(19) NOT NULL DEFAULT '0',
	`create_time` DATETIME NOT NULL,
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `idx_sign_hash` (`sign_hash`) USING BTREE
)
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
;
