-- MariaDB dump 10.19  Distrib 10.9.4-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: power_corp
-- ------------------------------------------------------
-- Server version	10.9.4-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `card_details`
--

DROP TABLE IF EXISTS `card_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `card_details` (
  `uid` int(11) unsigned NOT NULL,
  `name` varchar(32) NOT NULL,
  `number` decimal(16,0) NOT NULL,
  `cvv` decimal(3,0) NOT NULL,
  `expiry` date NOT NULL,
  `type` varchar(8) NOT NULL CHECK (`type` in ('credit','debit')),
  PRIMARY KEY (`number`),
  KEY `uid` (`uid`),
  CONSTRAINT `card_details_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `consumption`
--

DROP TABLE IF EXISTS `consumption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `consumption` (
  `meter_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `id` int(11) unsigned NOT NULL,
  `last_reading` int(11) unsigned NOT NULL DEFAULT 0,
  `curr_reading` int(11) unsigned NOT NULL DEFAULT 0,
  `due_date` date DEFAULT NULL,
  PRIMARY KEY (`meter_id`),
  KEY `fk_user_id` (`id`),
  CONSTRAINT `fk_user_id` FOREIGN KEY (`id`) REFERENCES `user_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `emp_details`
--

DROP TABLE IF EXISTS `emp_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `emp_details` (
  `id` smallint(11) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` varchar(128) NOT NULL,
  `last_name` varchar(128) NOT NULL,
  `age` int(11) unsigned NOT NULL CHECK (`age` >= 18),
  `address` varchar(256) NOT NULL,
  `gender` varchar(8) NOT NULL CHECK (`gender` in ('male','female','unsaid')),
  `join_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `username` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `email` varchar(128) DEFAULT NULL CHECK (`email` like '%@%.%'),
  `mobile_num` decimal(10,0) NOT NULL,
  `role` varchar(8) NOT NULL CHECK (`role` in ('scout','cashier','admin')),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `password` (`password`),
  UNIQUE KEY `mobile_num` (`mobile_num`),
  UNIQUE KEY `username_2` (`username`),
  UNIQUE KEY `password_2` (`password`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `payment_history`
--

DROP TABLE IF EXISTS `payment_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_history` (
  `trans_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(11) unsigned NOT NULL,
  `amount` decimal(13,2) NOT NULL,
  `tstamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `mode` varchar(10) NOT NULL CHECK ('mode' in ('credit card','debit card')),
  `note` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`trans_id`),
  KEY `uid` (`uid`),
  CONSTRAINT `payment_history_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_details`
--

DROP TABLE IF EXISTS `user_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_details` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `first_name` varchar(128) NOT NULL,
  `last_name` varchar(128) NOT NULL,
  `age` int(11) unsigned NOT NULL CHECK (`age` >= 18),
  `address` varchar(256) NOT NULL,
  `gender` varchar(8) NOT NULL CHECK (`gender` in ('male','female','unsaid')),
  `issue_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `username` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `mobile_num` decimal(10,0) NOT NULL,
  `email` varchar(256) NOT NULL CHECK (`email` like '%@%.%'),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `password` (`password`),
  UNIQUE KEY `mobile_num` (`mobile_num`),
  UNIQUE KEY `password_2` (`password`),
  UNIQUE KEY `username_2` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-15 16:52:26
