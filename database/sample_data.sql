/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

INSERT INTO `card_details` VALUES
(1,'TEST USERA',1234123412341234,123,'2024-08-31','Debit'),
(2,'TEST USERB',1234567812345678,123,'2025-06-30','Debit');



INSERT INTO `payment_history` VALUES
(1,1,10000.00,'2022-12-25 16:58:49','Credit Card','test payment a'),
(3,1,25000.00,'2022-12-26 06:32:45','Debit Card','test payment b'),
(4,1,250.00,'2022-12-26 06:33:11','Debit Card','test payment c'),
(5,1,250.50,'2022-12-26 06:33:34','Credit Card','test payment d'),
(6,1,1000000.75,'2022-12-26 06:34:08','Credit Card','test payment e'),
(7,2,10000.75,'2022-12-26 06:34:32','Credit Card','test payment a'),
(8,2,1000000.75,'2022-12-26 06:34:44','Debit Card','test payment b'),
(9,2,10.75,'2022-12-26 06:34:57','Debit Card','test payment c'),
(10,2,500000.00,'2022-12-26 06:35:29','Credit Card','test payment d'),
(11,2,5000.25,'2022-12-26 06:35:49','Debit Card','test payment e');

/* Password for both users is 'AAaa..11' */
INSERT INTO `user_details` VALUES
(1,'test','usera',20,'test address a','Male','2022-12-17 08:07:47','testa','$2b$12$aTxQNGInGLiDpyAC2hlPlOfWNKTrItmqD7EPEAIqevmPL1/R12ZCG',1234512345,'someonea@example.com'),
(2,'test','userb',25,'test address b','Unsaid','2022-12-17 08:56:46','testb','$2b$12$HYHei5qd8MTYjR8MihyA6uWEay6YJAwaLrYFiYhicagv4xH1vz/4u',1212121212,'someoneb@exaple.com');
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

