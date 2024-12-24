SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for food_nutrition
-- ----------------------------
DROP TABLE IF EXISTS `food_nutrition`;
CREATE TABLE `food_nutrition` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `food_id` int(11) NOT NULL,
  `nutrient_name` varchar(255) NOT NULL,
  `amount_per_100g` decimal(10,2) DEFAULT NULL,
  `nutrient_type` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_food_nutrition_food_id` (`food_id`),
  KEY `idx_food_id` (`food_id`),
  CONSTRAINT `fk_food_nutrition_food_id` FOREIGN KEY (`food_id`) REFERENCES `foods_info` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13215 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for foods_info
-- ----------------------------
DROP TABLE IF EXISTS `foods_info`;
CREATE TABLE `foods_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category` varchar(255) NOT NULL,
  `category_type` int(11) NOT NULL,
  `calories_per_100g` decimal(10,2) NOT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `alias_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_food_name` (`name`),
  KEY `idx_category_type` (`category_type`)
) ENGINE=InnoDB AUTO_INCREMENT=2769 DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
