/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 50729
 Source Host           : localhost:3306
 Source Schema         : knowschema

 Target Server Type    : MySQL
 Target Server Version : 50729
 File Encoding         : 65001

 Date: 18/03/2020 10:26:19
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for clause
-- ----------------------------
DROP TABLE IF EXISTS `clause`;
CREATE TABLE `clause`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `content` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `level` int(255) NOT NULL,
  `field_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `clause_field`(`field_id`) USING BTREE,
  CONSTRAINT `clause_field` FOREIGN KEY (`field_id`) REFERENCES `field` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 58 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for clause_entity_type_mapping
-- ----------------------------
DROP TABLE IF EXISTS `clause_entity_type_mapping`;
CREATE TABLE `clause_entity_type_mapping`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_type_id` int(11) NOT NULL,
  `clause_id` int(11) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `entity_type`(`entity_type_id`) USING BTREE,
  INDEX `clause`(`clause_id`) USING BTREE,
  CONSTRAINT `clause` FOREIGN KEY (`clause_id`) REFERENCES `clause` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `entity_type` FOREIGN KEY (`entity_type_id`) REFERENCES `entity_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for entity_type
-- ----------------------------
DROP TABLE IF EXISTS `entity_type`;
CREATE TABLE `entity_type`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `display_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `icon` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `father_id` int(11) NULL DEFAULT 0,
  `has_child` tinyint(255) NULL DEFAULT 0,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0),
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `uri`(`uri`) USING BTREE,
  INDEX `father_id`(`father_id`) USING BTREE,
  INDEX `has_child`(`has_child`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for field
-- ----------------------------
DROP TABLE IF EXISTS `field`;
CREATE TABLE `field`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for property_type
-- ----------------------------
DROP TABLE IF EXISTS `property_type`;
CREATE TABLE `property_type`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uri` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `display_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `icon` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `fieldType` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `is_entity` tinyint(4) NULL DEFAULT 0,
  `entity_type_id` int(11) NOT NULL,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0),
  `updated_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `uri`(`uri`) USING BTREE,
  INDEX `entity_type_id`(`entity_type_id`) USING BTREE,
  INDEX `is_entity`(`is_entity`) USING BTREE,
  CONSTRAINT `property_type_ibfk_1` FOREIGN KEY (`entity_type_id`) REFERENCES `entity_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 33 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
