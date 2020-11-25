CREATE TABLE IF NOT EXISTS `notes` (
	`id` INT(11) NOT NULL,
	`data` LONGTEXT NOT NULL DEFAULT '' COLLATE 'utf8mb4_general_ci',
	PRIMARY KEY (`id`) USING BTREE
)
COLLATE='utf8mb4_general_ci'
ENGINE=InnoDB
;