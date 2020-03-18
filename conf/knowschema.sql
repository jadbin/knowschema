/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50721
 Source Host           : localhost
 Source Database       : knowschema

 Target Server Type    : MySQL
 Target Server Version : 50721
 File Encoding         : utf-8

 Date: 03/18/2020 13:30:02 PM
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `clause`
-- ----------------------------
DROP TABLE IF EXISTS `clause`;
CREATE TABLE `clause` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) NOT NULL,
  `content` varchar(255) DEFAULT NULL,
  `level` int(255) DEFAULT NULL,
  `field_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uri` (`uri`),
  KEY `clause_field` (`field_id`) USING BTREE,
  CONSTRAINT `clause_field` FOREIGN KEY (`field_id`) REFERENCES `field` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=496 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- ----------------------------
--  Table structure for `clause_entity_type_mapping`
-- ----------------------------
DROP TABLE IF EXISTS `clause_entity_type_mapping`;
CREATE TABLE `clause_entity_type_mapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_type_id` int(11) NOT NULL,
  `clause_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `entity_type` (`entity_type_id`) USING BTREE,
  KEY `clause` (`clause_id`) USING BTREE,
  CONSTRAINT `clause` FOREIGN KEY (`clause_id`) REFERENCES `clause` (`id`),
  CONSTRAINT `entity_type` FOREIGN KEY (`entity_type_id`) REFERENCES `entity_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=487 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- ----------------------------
--  Table structure for `entity_type`
-- ----------------------------
DROP TABLE IF EXISTS `entity_type`;
CREATE TABLE `entity_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) NOT NULL,
  `display_name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `father_id` int(11) DEFAULT '0',
  `has_child` tinyint(255) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `uri` (`uri`) USING BTREE,
  KEY `father_id` (`father_id`) USING BTREE,
  KEY `has_child` (`has_child`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2012 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

-- ----------------------------
--  Table structure for `field`
-- ----------------------------
DROP TABLE IF EXISTS `field`;
CREATE TABLE `field` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;

-- ----------------------------
--  Table structure for `property_type`
-- ----------------------------
DROP TABLE IF EXISTS `property_type`;
CREATE TABLE `property_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) NOT NULL,
  `display_name` varchar(255) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `field_type` varchar(255) DEFAULT NULL,
  `is_entity` tinyint(4) DEFAULT '0',
  `entity_type_id` int(11) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `uri` (`uri`) USING BTREE,
  KEY `entity_type_id` (`entity_type_id`) USING BTREE,
  KEY `is_entity` (`is_entity`) USING BTREE,
  CONSTRAINT `property_type_ibfk_1` FOREIGN KEY (`entity_type_id`) REFERENCES `entity_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=267 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
