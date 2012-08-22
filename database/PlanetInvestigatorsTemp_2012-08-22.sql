# ************************************************************
# Sequel Pro SQL dump
# Version 3408
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: 127.0.0.1 (MySQL 5.5.9)
# Database: PlanetInvestigatorsTemp
# Generation Time: 2012-08-22 11:41:26 -0500
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table finders
# ------------------------------------------------------------

DROP TABLE IF EXISTS `finders`;

CREATE TABLE `finders` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `sub_image_id` int(11) DEFAULT NULL,
  `x` float DEFAULT NULL,
  `y` float DEFAULT NULL,
  `diameter` float DEFAULT NULL,
  `object_name` text,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table master_images
# ------------------------------------------------------------

DROP TABLE IF EXISTS `master_images`;

CREATE TABLE `master_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) DEFAULT NULL,
  `name` text,
  `object_name` text,
  `set_id` int(11) DEFAULT NULL,
  `set_index` int(11) DEFAULT NULL,
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `minimum_ra` float DEFAULT NULL,
  `minimum_dec` float DEFAULT NULL,
  `maximum_ra` float DEFAULT NULL,
  `maximum_dec` float DEFAULT NULL,
  `pixel_resolution` float DEFAULT NULL,
  `priority` float DEFAULT '1',
  `description` text,
  `file_location` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table sets
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sets`;

CREATE TABLE `sets` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `proposal_id` int(11) DEFAULT NULL,
  `object_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table sets_master_images
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sets_master_images`;

CREATE TABLE `sets_master_images` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `set_id` int(11) DEFAULT NULL,
  `master_image_id` int(11) DEFAULT NULL,
  `set_index` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



# Dump of table sub_images
# ------------------------------------------------------------

DROP TABLE IF EXISTS `sub_images`;

CREATE TABLE `sub_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) DEFAULT NULL,
  `master_image_id` int(11) DEFAULT NULL,
  `master_image_name` text,
  `name` text NOT NULL,
  `x` int(11) NOT NULL DEFAULT '0',
  `y` int(11) NOT NULL DEFAULT '0',
  `width` int(11) NOT NULL DEFAULT '450',
  `height` int(11) NOT NULL DEFAULT '450',
  `image_width` int(11) NOT NULL DEFAULT '450',
  `image_height` int(11) NOT NULL DEFAULT '450',
  `scale_level` int(11) NOT NULL DEFAULT '1',
  `scale` float NOT NULL DEFAULT '1',
  `file_location` text NOT NULL,
  `thumbnail_location` text,
  `active` tinyint(1) DEFAULT '1',
  `confirmed` tinyint(1) DEFAULT '0',
  `description` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `priority` float DEFAULT NULL,
  `done` tinyint(1) NOT NULL DEFAULT '0',
  `view_count` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `sub_images_on_priority` (`priority`),
  KEY `sub_images_on_project_id` (`project_id`),
  KEY `sub_images_on_active` (`active`),
  KEY `sub_images_on_done` (`done`),
  KEY `sub_images_on_view_count` (`view_count`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
