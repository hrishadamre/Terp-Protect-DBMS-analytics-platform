
---Drop tables
DROP TABLE IF EXISTS [TerpProtect.ArrestLog];
DROP TABLE IF EXISTS [TerpProtect.CaseChargeCategory];
DROP TABLE IF EXISTS [TerpProtect.Case];
DROP TABLE IF EXISTS [TerpProtect.Officer];
DROP TABLE IF EXISTS [TerpProtect.Department];
DROP TABLE IF EXISTS [TerpProtect.Arrestee];


--Creating Arestee Table
CREATE TABLE [TerpProtect.Arrestee] (
    arresteeId CHAR(9) NOT NULL,
    arresteeFirstName VARCHAR(20) NOT NULL,
    arresteeLastName VARCHAR(20) NOT NULL,
    arresteeDOB DATE,
    arresteeSex CHAR(1),
    arresteeRace VARCHAR(20),
    CONSTRAINT pk_Arrestee_arresteeId PRIMARY KEY (arresteeId)
);


--Creating Department Table
CREATE TABLE [TerpProtect.Department] (
    departmentId CHAR(9) NOT NULL,
    departmentName VARCHAR(20) NOT NULL,
    departmentType VARCHAR(50),
    departmentLocation VARCHAR(100),
    departmentPhoneNumber CHAR(10),
    officerHeadId CHAR(9) NULL,
    startDate DATE,
    CONSTRAINT pk_Department_departmentId PRIMARY KEY (departmentId)
);


-- Creating Officer Table
CREATE TABLE [TerpProtect.Officer] (
    officerId CHAR(9) NOT NULL,
    officerFirstName VARCHAR(20) NOT NULL,
    officerLastName VARCHAR(20) NOT NULL,
    departmentId CHAR(9) NOT NULL,
    officerLeadId CHAR(9) NULL,
    CONSTRAINT pk_Officer_officerId PRIMARY KEY (officerId),
    CONSTRAINT fk_Officer_departmentId FOREIGN KEY (departmentId)
        REFERENCES [TerpProtect.Department] (departmentId)
        ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT fk_Officer_officerLeadId FOREIGN KEY (officerLeadId)
        REFERENCES [TerpProtect.Officer] (officerId)
        ON DELETE NO ACTION ON UPDATE NO ACTION
);


--We Alter the table 
ALTER TABLE [TerpProtect.Department]
ADD CONSTRAINT fk_Department_officerHeadId 
FOREIGN KEY (officerHeadId)
REFERENCES [TerpProtect.Officer] (officerId)
ON DELETE NO ACTION
ON UPDATE NO ACTION;


--Creating the Case Table
CREATE TABLE [TerpProtect.Case] (
    caseId CHAR(9) NOT NULL,
    caseType VARCHAR(30),
    caseReportedOn DATE,
    caseClosedOn DATE,
    caseDescription VARCHAR(255)
    CONSTRAINT pk_Case_caseId PRIMARY KEY (caseId)
);

--Creating Case Charge
CREATE TABLE [TerpProtect.CaseChargeCategory] (
    caseId CHAR(9) NOT NULL,
    caseChargeCategory VARCHAR(30) NOT NULL,
    CONSTRAINT pk_CaseChargeCategory_caseId_caseChargeCategory PRIMARY KEY (caseId, caseChargeCategory),
    CONSTRAINT fk_CaseChargeCategory_caseId FOREIGN KEY (caseId)
        REFERENCES [TerpProtect.Case] (caseId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

--Creating ArrestLog
CREATE TABLE [TerpProtect.ArrestLog] (
    caseId CHAR(9) NOT NULL,
    arresteeId CHAR(9) NOT NULL,
    officerId CHAR(9) NOT NULL,
    arrestLogId CHAR(9) NOT NULL,
    arrestLogTimeStamp DATETIME,
    arrestLocation VARCHAR(50),
    CONSTRAINT pk_ArrestLog_arrestLogId PRIMARY KEY (arrestLogId),
    CONSTRAINT fk_ArrestLog_caseId FOREIGN KEY (caseId)
        REFERENCES [TerpProtect.Case] (caseId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ArrestLog_arresteeId FOREIGN KEY (arresteeId)
        REFERENCES [TerpProtect.Arrestee] (arresteeId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ArrestLog_officerId FOREIGN KEY (officerId)
        REFERENCES [TerpProtect.Officer] (officerId)
        ON DELETE CASCADE ON UPDATE CASCADE
);


-- Insert into Arrestee
INSERT INTO [TerpProtect.Arrestee]
  (arresteeId, arresteeFirstName, arresteeLastName, arresteeDOB, arresteeSex, arresteeRace)
VALUES
('AR0000001','John','Doe','1990-05-12','M','White'),
('AR0000002','Jane','Smith','1985-07-22','F','Black'),
('AR0000003','Michael','Brown','1992-03-18','M','Hispanic'),
('AR0000004','Emily','Johnson','1998-12-01','F','Asian'),
('AR0000005','Chris','Davis','1987-09-10','M','White'),
('AR0000006','Sarah','Miller','1995-11-15','F','Hispanic'),
('AR0000007','David','Wilson','1980-04-25','M','Black'),
('AR0000008','Laura','Taylor','1993-08-19','F','White'),
('AR0000009','Daniel','Moore','1991-01-29','M','Asian'),
('AR0000010','Sophia','Anderson','1989-06-03','F','Black'),
('AR0000011','Matthew','Thomas','2001-02-27','M','White'),
('AR0000012','Olivia','Jackson','2003-10-12','F','Hispanic'),
('AR0000013','James','White','1982-07-07','M','Asian'),
('AR0000014','Ava','Harris','2000-11-21','F','White'),
('AR0000015','Ethan','Martin','1990-09-15','M','Black'),
('AR0000016','Isabella','Thompson','2002-03-04','F','White'),
('AR0000017','Noah','Garcia','1988-01-10','M','Hispanic'),
('AR0000018','Mia','Martinez','1999-04-23','F','Hispanic'),
('AR0000019','Liam','Robinson','1992-06-17','M','White'),
('AR0000020','Charlotte','Clark','2001-12-30','F','Asian'),
('AR0000021','Benjamin','Rodriguez','1986-02-14','M','Hispanic'),
('AR0000022','Amelia','Lewis','2004-07-28','F','White'),
('AR0000023','Lucas','Lee','1995-05-06','M','Asian'),
('AR0000024','Harper','Walker','2002-08-11','F','White'),
('AR0000025','Mason','Hall','1984-03-19','M','Black'),
('AR0000026','Evelyn','Allen','2000-10-08','F','White'),
('AR0000027','Logan','Young','1993-09-02','M','White'),
('AR0000028','Abigail','Hernandez','1992-11-26','F','Hispanic'),
('AR0000029','Elijah','King','1987-12-05','M','Black'),
('AR0000030','Emily','Wright','1996-01-16','F','White'),
('AR0000031','Oliver','Lopez','1994-02-22','M','Hispanic'),
('AR0000032','Sofia','Hill','2003-05-27','F','White'),
('AR0000033','Aiden','Scott','1991-03-13','M','White'),
('AR0000034','Chloe','Green','2001-07-01','F','Black'),
('AR0000035','Carter','Adams','1983-10-29','M','White'),
('AR0000036','Grace','Baker','1997-06-09','F','White'),
('AR0000037','Jackson','Gonzalez','1990-08-15','M','Hispanic'),
('AR0000038','Avery','Nelson','2000-09-24','F','White'),
('AR0000039','Henry','Carter','1989-04-02','M','Black'),
('AR0000040','Ella','Mitchell','1992-12-20','F','White'),
('AR0000041','Wyatt','Perez','1993-03-31','M','Hispanic'),
('AR0000042','Aria','Roberts','2005-05-19','F','White'),
('AR0000043','Sebastian','Turner','1988-07-12','M','White'),
('AR0000044','Scarlett','Phillips','1997-02-03','F','White'),
('AR0000045','Alexander','Campbell','1985-11-09','M','Black'),
('AR0000046','Victoria','Parker','2002-09-18','F','White'),
('AR0000047','Jack','Evans','1986-06-28','M','White'),
('AR0000048','Lily','Edwards','1994-01-07','F','Asian'),
('AR0000049','Owen','Collins','2001-05-29','M','White'),
('AR0000050','Hannah','Stewart','1993-10-03','F','White'),
('AR0000051','Samuel','Sanchez','1999-09-21','M','Hispanic'),
('AR0000052','Zoe','Morris','2000-03-25','F','White'),
('AR0000053','Julian','Rogers','1988-02-11','M','Black'),
('AR0000054','Penelope','Reed','1996-04-05','F','White'),
('AR0000055','Levi','Cook','1992-06-13','M','White'),
('AR0000056','Layla','Morgan','2003-08-08','F','Black'),
('AR0000057','Daniel','Bell','1979-12-14','M','White'),
('AR0000058','Nora','Murphy','2004-07-05','F','Asian'),
('AR0000059','Gabriel','Bailey','1991-11-23','M','Hispanic'),
('AR0000060','Riley','Rivera','2002-02-02','F','Hispanic'),
('AR0000061','Caleb','Cooper','1987-01-19','M','White'),
('AR0000062','Lillian','Richardson','1995-09-09','F','White'),
('AR0000063','Isaac','Cox','2000-06-17','M','Black'),
('AR0000064','Paisley','Howard','1998-03-28','F','White'),
('AR0000065','Jayden','Ward','1983-05-15','M','Asian'),
('AR0000066','Aubrey','Torres','2001-12-06','F','Hispanic'),
('AR0000067','Matthew','Peterson','1990-07-30','M','White'),
('AR0000068','Addison','Gray','2005-11-11','F','White'),
('AR0000069','Joseph','Ramirez','1993-02-03','M','Hispanic'),
('AR0000070','Natalie','James','1986-10-24','F','Black'),
('AR0000071','Dylan','Watson','1997-01-08','M','White'),
('AR0000072','Brooklyn','Brooks','2002-04-14','F','White'),
('AR0000073','Andrew','Kelly','1994-09-26','M','White'),
('AR0000074','Savannah','Sanders','2000-01-31','F','Asian'),
('AR0000075','Hudson','Price','1981-08-22','M','White'),
('AR0000076','Audrey','Bennett','1999-10-16','F','White'),
('AR0000077','Nathan','Wood','1992-05-04','M','Black'),
('AR0000078','Stella','Barnes','2003-03-13','F','White'),
('AR0000079','Christian','Ross','1989-06-26','M','White'),
('AR0000080','Violet','Henderson','2004-02-21','F','Hispanic'),
('AR0000081','Aaron','Coleman','1985-12-30','M','Asian'),
('AR0000082','Eleanor','Jenkins','1996-08-02','F','White'),
('AR0000083','Hunter','Perry','2001-09-27','M','White'),
('AR0000084','Bella','Powell','1998-11-06','F','Black'),
('AR0000085','Thomas','Long','1987-03-22','M','White'),
('AR0000086','Lucy','Patterson','2005-12-18','F','White'),
('AR0000087','Jonathan','Hughes','1991-07-01','M','Hispanic'),
('AR0000088','Aaliyah','Flores','2000-05-05','F','Hispanic'),
('AR0000089','Isaiah','Washington','1982-09-12','M','Black'),
('AR0000090','Madison','Butler','1997-06-20','F','White'),
('AR0000091','Connor','Simmons','1993-01-03','M','White'),
('AR0000092','Hailey','Foster','2002-07-09','F','Asian'),
('AR0000093','Colton','Gonzales','1995-10-27','M','Hispanic'),
('AR0000094','Scarlet','Bryant','2001-02-18','F','White'),
('AR0000095','Adrian','Alexander','1984-04-11','M','Black'),
('AR0000096','Maya','Russell','1999-09-07','F','White'),
('AR0000097','Jeremiah','Griffin','2003-01-26','M','Hispanic'),
('AR0000098','Camila','Diaz','2004-06-14','F','Hispanic'),
('AR0000099','Brayden','Hayes','1978-10-05','M','White'),
('AR0000100','Kayla','Myers','2005-03-29','F','Black');


--These are done to avoid circular dependencies
INSERT INTO [TerpProtect.Department] (departmentId, departmentName, officerHeadId)
VALUES ('D101', 'Cyber Crimes', NULL);



INSERT INTO [TerpProtect.Officer] (officerId, officerFirstName, officerLastName, departmentId)
VALUES ('O900', 'Jane', 'Doe', 'D101');





--Inserting 10 Departments
INSERT INTO [TerpProtect.Department] 
(departmentId, departmentName, departmentType, departmentLocation, departmentPhoneNumber, officerHeadId, startDate)
VALUES
('D102', 'Homicide Invest.', 'Investigations', 'Los Angeles, CA', '3105552002', NULL, '2019-03-10'),
('D103', 'Financial Crimes', 'Economic Offenses', 'Chicago, IL', '7735553003', NULL, '2021-06-01'),
('D104', 'Narcotics Div.', 'Field Operations', 'Houston, TX', '8325554004', NULL, '2018-09-12'),
('D105', 'Forensic Science', 'Support Services', 'Miami, FL', '3055555005', NULL, '2020-11-05'),
('D106', 'Traffic Control', 'Operations', 'Phoenix, AZ', '6025556006', NULL, '2022-02-14'),
('D107', 'Special Victims', 'Investigations', 'Philadelphia, PA', '2155557007', NULL, '2021-05-20'),
('D108', 'Counter-Terror.', 'Homeland Security', 'Washington, DC', '2025558008', NULL, '2017-07-07'),
('D109', 'Organized Crime', 'Intelligence', 'Las Vegas, NV', '7025559009', NULL, '2023-03-18'),
('D110', 'Comm. Outreach', 'Public Relations', 'Seattle, WA', '2065551010', NULL, '2019-12-01');


UPDATE [TerpProtect.Department]
SET 
    departmentName = 'Cyber Crimes',
    departmentType = 'Law Enforcement',
    departmentLocation = 'Building 5, HQ Campus',
    departmentPhoneNumber = '555-0134',
    officerHeadId = NULL,
    startDate = '2023-05-01'
WHERE departmentId = 'D101';


--INSERTING 100 OFFICERS
INSERT INTO [TerpProtect.Officer]
(officerId, officerFirstName, officerLastName, departmentId, officerLeadId)
VALUES
-- Command / unit leads (no manager)
('OF0000001','Robert','King','D104',NULL),
('OF0000002','Linda','Scott','D105',NULL),
('OF0000003','William','Adams','D103',NULL),
('OF0000004','Barbara','Clark','D106',NULL),
('OF0000005','Richard','Lewis','D107',NULL),
('OF0000006','Susan','Hall','D104',NULL),
('OF0000007','Joseph','Allen','D105',NULL),
('OF0000008','Patricia','Young','D102',NULL),
('OF0000009','Charles','Hernandez','D106',NULL),
('OF0000010','Jennifer','Wright','D108',NULL),

-- Team members (report to one of the first 10)
('OF0000011','Thomas','Lopez','D102','OF0000008'),
('OF0000012','Elizabeth','Hill','D105','OF0000002'),
('OF0000013','Christopher','Green','D103','OF0000003'),
('OF0000014','Karen','Baker','D106','OF0000004'),
('OF0000015','Anthony','Gonzalez','D107','OF0000005'),
('OF0000016','Mark','Nelson','D104','OF0000001'),
('OF0000017','Donna','Carter','D108','OF0000010'),
('OF0000018','Steven','Mitchell','D102','OF0000008'),
('OF0000019','Sarah','Perez','D110','OF0000008'),
('OF0000020','Kevin','Roberts','D109','OF0000008'),

('OF0000021','Brian','Turner','D104','OF0000006'),
('OF0000022','Angela','Phillips','D105','OF0000007'),
('OF0000023','Jason','Campbell','D103','OF0000003'),
('OF0000024','Michelle','Parker','D106','OF0000009'),
('OF0000025','Eric','Evans','D107','OF0000005'),
('OF0000026','Rebecca','Edwards','D108','OF0000010'),
('OF0000027','Sean','Collins','D102','OF0000008'),
('OF0000028','Katherine','Stewart','D110','OF0000008'),
('OF0000029','Alexander','Sanchez','D109','OF0000008'),
('OF0000030','Cynthia','Morris','D104','OF0000001'),

('OF0000031','Patrick','Rogers','D105','OF0000002'),
('OF0000032','Amy','Reed','D103','OF0000003'),
('OF0000033','Justin','Cook','D106','OF0000004'),
('OF0000034','Melissa','Morgan','D107','OF0000005'),
('OF0000035','Brandon','Bell','D108','OF0000010'),
('OF0000036','Deborah','Murphy','D102','OF0000008'),
('OF0000037','Scott','Bailey','D110','OF0000008'),
('OF0000038','Laura','Rivera','D109','OF0000008'),
('OF0000039','Frank','Cooper','D104','OF0000006'),
('OF0000040','Rachel','Richardson','D105','OF0000007');



-- Insert into Case
INSERT INTO [TerpProtect.Case]
  (caseId, caseType, caseReportedOn, caseClosedOn, caseDescription)
VALUES
('CS0000001','Theft','2022-01-05','2022-01-18','Stolen bicycle from campus rack'),
('CS0000002','Assault','2022-01-10','2022-02-01','Altercation outside dormitory'),
('CS0000003','Burglary','2022-01-14',NULL,'Apartment break-in reported'),
('CS0000004','Fraud','2022-01-20','2022-03-02','Credit card skimming incident'),
('CS0000005','DUI','2022-01-25','2022-02-05','Driver suspected of DUI'),
('CS0000006','Narcotics','2022-02-01','2022-02-20','Possession of controlled substance'),
('CS0000007','Cybercrime','2022-02-03',NULL,'Phishing emails targeting staff'),
('CS0000008','Vandalism','2022-02-08','2022-02-15','Graffiti on library wall'),
('CS0000009','Domestic Violence','2022-02-10','2022-03-01','Disturbance in family housing'),
('CS0000010','Homicide','2022-02-12',NULL,'Suspicious death investigation'),
('CS0000011','Robbery','2022-02-16','2022-03-05','Wallet taken at ATM'),
('CS0000012','Arson','2022-02-18','2022-03-12','Trash can fire behind cafeteria'),
('CS0000013','Traffic Accident','2022-02-20','2022-02-21','Two-car collision at Main St'),
('CS0000014','Public Disturbance','2022-02-22','2022-02-23','Noise complaint after midnight'),
('CS0000015','Trespassing','2022-02-24','2022-03-03','Unauthorized entry to lab'),
('CS0000016','Identity Theft','2022-03-01','2022-03-18','Account takeover reported'),
('CS0000017','Stalking','2022-03-04',NULL,'Repeated unwanted following'),
('CS0000018','Kidnapping','2022-03-06','2022-03-20','Custodial interference'),
('CS0000019','Money Laundering','2022-03-08',NULL,'Suspicious wire transfers'),
('CS0000020','Illegal Firearms','2022-03-10','2022-03-19','Unregistered firearm in car'),
('CS0000021','Animal Cruelty','2022-03-12','2022-03-25','Report of harmed stray dog'),
('CS0000022','Hit and Run','2022-03-14','2022-03-30','Vehicle fled scene, minor injury'),
('CS0000023','Shoplifting','2022-03-16','2022-03-18','Items taken from bookstore'),
('CS0000024','Disorderly Conduct','2022-03-18','2022-03-19','Fight at student center'),
('CS0000025','Theft','2022-03-20','2022-04-02','Laptop missing from lab'),
('CS0000026','Assault','2022-03-22',NULL,'Assault during intramural game'),
('CS0000027','Burglary','2022-03-25','2022-04-10','Storage unit lock cut'),
('CS0000028','Fraud','2022-03-27','2022-04-15','Fake check deposit'),
('CS0000029','DUI','2022-03-29','2022-04-01','Field sobriety failure'),
('CS0000030','Narcotics','2022-04-02','2022-04-22','Intent to distribute suspected'),
('CS0000031','Cybercrime','2022-04-05','2022-04-20','Ransomware attempt thwarted'),
('CS0000032','Vandalism','2022-04-07',NULL,'Windows broken at Field House'),
('CS0000033','Domestic Violence','2022-04-09','2022-04-25','911 hang-up, investigation'),
('CS0000034','Homicide','2022-04-12',NULL,'Cold case file reopened'),
('CS0000035','Robbery','2022-04-14','2022-05-01','Phone snatched on walkway'),
('CS0000036','Arson','2022-04-16','2022-05-05','Dumpster fire near dorms'),
('CS0000037','Traffic Accident','2022-04-18','2022-04-19','Bicycle vs car, minor injury'),
('CS0000038','Public Disturbance','2022-04-20','2022-04-21','Off-campus party overflow'),
('CS0000039','Trespassing','2022-04-22','2022-04-28','Fence scaled at stadium'),
('CS0000040','Identity Theft','2022-04-25','2022-05-03','Debit card cloned'),
('CS0000041','Stalking','2022-04-27','2022-05-20','Restraining order filed'),
('CS0000042','Kidnapping','2022-04-29',NULL,'Child custody dispute'),
('CS0000043','Money Laundering','2022-05-02','2022-06-15','Structuring deposits flagged'),
('CS0000044','Illegal Firearms','2022-05-04','2022-05-18','Gun found during stop'),
('CS0000045','Animal Cruelty','2022-05-06','2022-05-12','Neglect case documented'),
('CS0000046','Hit and Run','2022-05-08','2022-05-25','Side-swipe near garage'),
('CS0000047','Shoplifting','2022-05-10','2022-05-11','Cosmetics concealed, detained'),
('CS0000048','Disorderly Conduct','2022-05-12',NULL,'Public intoxication reported'),
('CS0000049','Theft','2022-05-14','2022-05-27','Tool kit missing from van'),
('CS0000050','Assault','2022-05-16','2022-05-29','Bar fight, minor injuries'),

('CS0000051','Burglary','2022-05-18','2022-06-03','Office door pried open'),
('CS0000052','Fraud','2022-05-20','2022-06-01','Payroll scam email'),
('CS0000053','DUI','2022-05-22','2022-05-24','Breath test over limit'),
('CS0000054','Narcotics','2022-05-24','2022-06-10','Paraphernalia recovered'),
('CS0000055','Cybercrime','2022-05-26','2022-06-05','Account brute force attempts'),
('CS0000056','Vandalism','2022-05-28',NULL,'Benches spray-painted'),
('CS0000057','Domestic Violence','2022-05-30','2022-06-08','Witness statements taken'),
('CS0000058','Homicide','2022-06-01',NULL,'Medical examiner review'),
('CS0000059','Robbery','2022-06-03','2022-06-20','Strong-arm robbery report'),
('CS0000060','Arson','2022-06-05','2022-06-25','Grass fire by parking lot'),

('CS0000061','Traffic Accident','2022-06-07','2022-06-07','Rear-end at stoplight'),
('CS0000062','Public Disturbance','2022-06-09','2022-06-09','Protest noise complaint'),
('CS0000063','Trespassing','2022-06-11','2022-06-18','Roof access violation'),
('CS0000064','Identity Theft','2022-06-13','2022-06-22','SSN misuse reported'),
('CS0000065','Stalking','2022-06-15','2022-07-01','Online harassment escalated'),
('CS0000066','Kidnapping','2022-06-17','2022-07-05','Amber alert canceled'),
('CS0000067','Money Laundering','2022-06-19',NULL,'Shell accounts discovered'),
('CS0000068','Illegal Firearms','2022-06-21','2022-07-02','Serial scratched handgun'),
('CS0000069','Animal Cruelty','2022-06-23','2022-06-29','Dog left in hot car'),
('CS0000070','Hit and Run','2022-06-25','2022-07-06','Mirror strike on cyclist'),

('CS0000071','Shoplifting','2022-06-27','2022-06-28','Snacks concealed, confessed'),
('CS0000072','Disorderly Conduct','2022-06-29','2022-07-01','Obstructing foot traffic'),
('CS0000073','Theft','2022-07-01','2022-07-12','Backpack missing from gym'),
('CS0000074','Assault','2022-07-03','2022-07-15','Pushed during argument'),
('CS0000075','Burglary','2022-07-05','2022-07-25','Lab equipment stolen'),
('CS0000076','Fraud','2022-07-07',NULL,'Loan scam via text'),
('CS0000077','DUI','2022-07-09','2022-07-10','Refused breathalyzer'),
('CS0000078','Narcotics','2022-07-11','2022-07-22','Marijuana distribution'),
('CS0000079','Cybercrime','2022-07-13','2022-07-20','Spoofed payroll portal'),
('CS0000080','Vandalism','2022-07-15','2022-07-18','Keyed vehicle in lot'),

('CS0000081','Domestic Violence','2022-07-17','2022-07-27','Verbal dispute escalated'),
('CS0000082','Homicide','2022-07-19',NULL,'Ballistics analysis pending'),
('CS0000083','Robbery','2022-07-21','2022-08-05','Knifepoint theft alley'),
('CS0000084','Arson','2022-07-23','2022-08-08','Locker room fire damage'),
('CS0000085','Traffic Accident','2022-07-25','2022-07-26','Fender bender on 3rd'),
('CS0000086','Public Disturbance','2022-07-27','2022-07-27','Loud music citation'),
('CS0000087','Trespassing','2022-07-29','2022-08-01','Unauthorized roof party'),
('CS0000088','Identity Theft','2022-07-31','2022-08-12','Bank account opened'),
('CS0000089','Stalking','2022-08-02',NULL,'GPS tracker found'),
('CS0000090','Kidnapping','2022-08-04','2022-08-20','False report determined'),

('CS0000091','Money Laundering','2022-08-06','2022-09-10','Cash-intensive business'),
('CS0000092','Illegal Firearms','2022-08-08','2022-08-18','Loaded gun in backpack'),
('CS0000093','Animal Cruelty','2022-08-10','2022-08-14','Cat injured intentionally'),
('CS0000094','Hit and Run','2022-08-12','2022-08-25','Parked car struck'),
('CS0000095','Shoplifting','2022-08-14','2022-08-15','Clothing tags removed'),
('CS0000096','Disorderly Conduct','2022-08-16','2022-08-17','Public urination cited'),
('CS0000097','Theft','2022-08-18','2022-08-28','Tool theft from shed'),
('CS0000098','Assault','2022-08-20','2022-08-31','Punched during dispute'),
('CS0000099','Burglary','2022-08-22',NULL,'Door forced in dorm hall'),
('CS0000100','Fraud','2022-08-24','2022-09-05','Phony raffle collection');

INSERT INTO [TerpProtect.Case]
  (caseId, caseType, caseReportedOn, caseClosedOn, caseDescription)
VALUES
('CS0000101', 'Graffiti Vandalism', '2023-09-01', NULL, 'Graffiti reported on public building'),
  ('CS0000102', 'Noise Complaint', '2023-08-15', '2023-08-16', 'Loud party reported, no suspect identified'),
  ('CS0000103', 'Suspicious Package', '2023-07-05', '2023-07-05', 'Unattended package reported, turned out safe'),
  ('CS0000104', 'Missing Bicycle', '2023-09-10', NULL, 'Bicycle reported stolen but no leads'),
  ('CS0000105', 'Illegal Dumping', '2023-08-20', NULL, 'Trash dumped in restricted area, no witness');







-- Insert into CaseChargeCategory
INSERT INTO [TerpProtect.CaseChargeCategory]
VALUES

('CS0000001','Theft'),
('CS0000001','Possession of Stolen Property'),
('CS0000001','Trespassing'),
('CS0000001','Attempted Theft'),
('CS0000001','Conspiracy'),

('CS0000002','Assault'),
('CS0000002','Battery'),
('CS0000002','Harassment'),
('CS0000002','Disorderly Conduct'),
('CS0000002','Menacing'),

('CS0000003','Burglary'),
('CS0000003','Breaking and Entering'),
('CS0000003','Possession of Burglary Tools'),
('CS0000003','Trespassing'),
('CS0000003','Criminal Mischief'),

('CS0000004','Fraud'),
('CS0000004','Identity Theft'),
('CS0000004','Forgery'),
('CS0000004','False Pretenses'),
('CS0000004','Money Laundering'),

('CS0000005','DUI'),
('CS0000005','Open Container'),
('CS0000005','Reckless Driving'),
('CS0000005','Failure to Maintain Lane'),
('CS0000005','Refusal to Submit Test'),

('CS0000006','Narcotics'),
('CS0000006','Possession'),
('CS0000006','Distribution'),
('CS0000006','Drug Paraphernalia'),
('CS0000006','Intent to Distribute'),

('CS0000007','Cybercrime'),
('CS0000007','Unauthorized Access'),
('CS0000007','Computer Intrusion'),
('CS0000007','Data Theft'),
('CS0000007','Phishing'),

('CS0000008','Vandalism'),
('CS0000008','Graffiti'),
('CS0000008','Property Damage'),
('CS0000008','Criminal Mischief'),
('CS0000008','Trespassing'),

('CS0000009','Domestic Violence'),
('CS0000009','Assault'),
('CS0000009','Interference with 911'),
('CS0000009','Restraining Order Violation'),
('CS0000009','Harassment'),


('CS0000010','Homicide'),
('CS0000010','Illegal Firearms'),
('CS0000010','Tampering with Evidence'),
('CS0000010','Obstruction'),
('CS0000011','Robbery'),
('CS0000011','Aggravated Robbery'),
('CS0000011','Assault'),
('CS0000011','Conspiracy'),
('CS0000012','Arson'),
('CS0000012','Attempted Arson'),
('CS0000012','Criminal Mischief'),
('CS0000012','Reckless Endangerment'),

('CS0000013','Traffic Accident'),
('CS0000013','Failure to Render Aid'),
('CS0000013','Reckless Driving'),
('CS0000013','No Insurance'),

('CS0000014','Public Disturbance'),
('CS0000014','Disorderly Conduct'),
('CS0000014','Unlawful Assembly'),
('CS0000014','Public Intoxication'),

('CS0000015','Trespassing'),
('CS0000015','Loitering'),
('CS0000015','Criminal Trespass at Night'),
('CS0000015','Resisting Detention'),

('CS0000016','Identity Theft'),
('CS0000016','Fraud'),
('CS0000016','Credit Card Abuse'),
('CS0000017','Stalking'),
('CS0000017','Harassment'),
('CS0000017','Violation of Protection Order'),
('CS0000018','Kidnapping'),
('CS0000018','Unlawful Restraint'),
('CS0000018','Custodial Interference'),
('CS0000019','Money Laundering'),
('CS0000019','Structuring'),
('CS0000019','Tax Evasion'),

('CS0000020','Illegal Firearms'),
('CS0000020','Unlawful Possession of Firearm'),
('CS0000020','Carrying Without Permit'),
('CS0000021','Animal Cruelty'),
('CS0000021','Endangering an Animal'),
('CS0000021','Neglect'),
('CS0000022','Hit and Run'),
('CS0000022','Failure to Render Aid'),
('CS0000022','Reckless Driving'),
('CS0000023','Shoplifting'),
('CS0000023','Retail Theft'),
('CS0000023','Possession of Stolen Property'),
('CS0000024','Disorderly Conduct'),
('CS0000024','Public Intoxication'),
('CS0000025','Theft'),
('CS0000025','Receiving Stolen Property'),
('CS0000026','Fraud'),
('CS0000027','Arson'),
('CS0000028','Cybercrime');



INSERT INTO [TerpProtect.Officer]
(officerId, officerFirstName, officerLastName, departmentId, officerLeadId)
VALUES
('OF0000041','Peter','Cox','D103','OF0000003'),
('OF0000042','Victoria','Howard','D106','OF0000004'),
('OF0000043','Edward','Ward','D107','OF0000005'),
('OF0000044','Nicole','Torres','D108','OF0000010'),
('OF0000045','Shawn','Peterson','D102','OF0000008'),
('OF0000046','Brittany','Gray','D110','OF0000008'),
('OF0000047','Jeremy','Ramirez','D109','OF0000008'),
('OF0000048','Diana','James','D104','OF0000001'),
('OF0000049','Larry','Watson','D105','OF0000002'),
('OF0000050','Courtney','Brooks','D103','OF0000003'),

('OF0000051','Jeffrey','Kelly','D106','OF0000004'),
('OF0000052','Kylie','Sanders','D107','OF0000005'),
('OF0000053','Ethan','Price','D108','OF0000010'),
('OF0000054','Allison','Bennett','D102','OF0000008'),
('OF0000055','Shane','Wood','D110','OF0000008'),
('OF0000056','Hannah','Barnes','D109','OF0000008'),
('OF0000057','Trevor','Ross','D104','OF0000006'),
('OF0000058','Kara','Henderson','D105','OF0000007'),
('OF0000059','Phillip','Coleman','D103','OF0000003'),
('OF0000060','Vanessa','Jenkins','D106','OF0000009'),

('OF0000061','Cameron','Perry','D107','OF0000005'),
('OF0000062','Megan','Powell','D108','OF0000010'),
('OF0000063','Derek','Long','D102','OF0000008'),
('OF0000064','Erin','Patterson','D110','OF0000008'),
('OF0000065','Kyle','Hughes','D109','OF0000008'),
('OF0000066','Jared','Flores','D104','OF0000001'),
('OF0000067','Paige','Washington','D105','OF0000002'),
('OF0000068','Ross','Butler','D103','OF0000003'),
('OF0000069','Ariel','Foster','D106','OF0000004'),
('OF0000070','Gavin','Gonzales','D107','OF0000005'),

('OF0000071','Naomi','Bryant','D108','OF0000010'),
('OF0000072','Logan','Alexander','D102','OF0000008'),
('OF0000073','Sabrina','Russell','D110','OF0000008'),
('OF0000074','Colin','Griffin','D109','OF0000008'),
('OF0000075','Tara','Diaz','D104','OF0000006'),
('OF0000076','Owen','Hayes','D105','OF0000007'),
('OF0000077','Jenna','Myers','D103','OF0000003'),
('OF0000078','Riley','Ford','D106','OF0000009'),
('OF0000079','Miles','Hamilton','D107','OF0000005'),
('OF0000080','Erica','Graham','D108','OF0000010'),

('OF0000081','Grant','Sullivan','D102','OF0000008'),
('OF0000082','Kaitlyn','Wallace','D110','OF0000008'),
('OF0000083','Dustin','Cole','D109','OF0000008'),
('OF0000084','Tiffany','West','D104','OF0000001'),
('OF0000085','Mitchell','Jordan','D105','OF0000002'),
('OF0000086','Haley','Owens','D103','OF0000003'),
('OF0000087','Preston','Reynolds','D106','OF0000004'),
('OF0000088','Chelsea','Fisher','D107','OF0000005'),
('OF0000089','Spencer','Ellis','D108','OF0000010'),
('OF0000090','Nicole','Harrison','D102','OF0000008'),

('OF0000091','Conner','Gibson','D110','OF0000008'),
('OF0000092','Bethany','Mcdonald','D109','OF0000008'),
('OF0000093','Ruben','Cruz','D104','OF0000006'),
('OF0000094','Heidi','Marshall','D105','OF0000007'),
('OF0000095','Kendall','Ortiz','D103','OF0000003'),
('OF0000096','Lance','Gomez','D106','OF0000009'),
('OF0000097','Selena','Murray','D107','OF0000005'),
('OF0000098','Troy','Freeman','D108','OF0000010'),
('OF0000099','Elise','Wells','D102','OF0000008'),
('OF0000100','Harold','Shaw','D110','OF0000008')


--Inserting 100 values into ArrestLog

INSERT INTO [TerpProtect.ArrestLog]
  (arrestLogId, caseId, arresteeId, officerId, arrestLogTimeStamp, arrestLocation)
VALUES
('AL0000001','CS0000001','AR0000001','OF0000001','2022-01-05 09:15:22','Main St & 3rd Ave'),
('AL0000002','CS0000002','AR0000002','OF0000002','2022-01-10 22:41:09','Dorm A Lobby'),
('AL0000003','CS0000003','AR0000003','OF0000003','2022-01-14 17:05:44','Library Parking Lot'),
('AL0000004','CS0000004','AR0000004','OF0000004','2022-01-20 11:32:10','Finance Building - Front'),
('AL0000005','CS0000005','AR0000005','OF0000005','2022-01-25 01:12:55','I-75 Exit 24 SB'),
('AL0000006','CS0000006','AR0000006','OF0000006','2022-02-01 20:48:13','Dorm B - Room 210'),
('AL0000007','CS0000007','AR0000007','OF0000007','2022-02-03 08:26:37','IT Annex - Help Desk'),
('AL0000008','CS0000008','AR0000008','OF0000008','2022-02-08 23:59:02','Rec Center - South Wall'),
('AL0000009','CS0000009','AR0000009','OF0000009','2022-02-10 14:11:29','Family Housing Lot C'),
('AL0000010','CS0000010','AR0000010','OF0000010','2022-02-12 03:05:18','Riverside Trail - Mile 1'),

('AL0000011','CS0000011','AR0000011','OF0000011','2022-02-16 19:44:51','ATM Kiosk - Union'),
('AL0000012','CS0000012','AR0000012','OF0000012','2022-02-18 04:22:36','Cafeteria Rear Alley'),
('AL0000013','CS0000013','AR0000013','OF0000013','2022-02-20 12:33:20','Main & College Ave'),
('AL0000014','CS0000014','AR0000014','OF0000014','2022-02-22 00:17:09','Student Center Plaza'),
('AL0000015','CS0000015','AR0000015','OF0000015','2022-02-24 16:55:47','Engineering Lab - East Door'),
('AL0000016','CS0000016','AR0000016','OF0000016','2022-03-01 10:01:04','Registrar Office - Counter'),
('AL0000017','CS0000017','AR0000017','OF0000017','2022-03-04 21:40:23','Lot P3 - Row 7'),
('AL0000018','CS0000018','AR0000018','OF0000018','2022-03-06 07:14:58','City Park - Pavilion 2'),
('AL0000019','CS0000019','AR0000019','OF0000019','2022-03-08 15:26:41','Bank Branch - Lobby'),
('AL0000020','CS0000020','AR0000020','OF0000020','2022-03-10 18:39:12','Maple St & 8th'),

('AL0000021','CS0000021','AR0000021','OF0000021','2022-03-12 13:20:00','Animal Shelter - Intake'),
('AL0000022','CS0000022','AR0000022','OF0000022','2022-03-14 02:05:31','Garage B - Level 4'),
('AL0000023','CS0000023','AR0000023','OF0000023','2022-03-16 11:49:49','Campus Bookstore - Exit'),
('AL0000024','CS0000024','AR0000024','OF0000024','2022-03-18 23:18:22','Student Center - Food Court'),
('AL0000025','CS0000025','AR0000025','OF0000025','2022-03-20 09:07:55','CompSci Lab - Bay 2'),
('AL0000026','CS0000026','AR0000026','OF0000026','2022-03-22 20:54:43','Intramural Field 1'),
('AL0000027','CS0000027','AR0000027','OF0000027','2022-03-25 06:36:14','Storage Facility - Unit 27'),
('AL0000028','CS0000028','AR0000028','OF0000028','2022-03-27 14:28:39','Admin Hall - Payroll'),
('AL0000029','CS0000029','AR0000029','OF0000029','2022-03-29 00:42:02','2nd St & Pine Ave'),
('AL0000030','CS0000030','AR0000030','OF0000030','2022-04-02 18:03:27','Dorm C - Courtyard'),

('AL0000031','CS0000031','AR0000031','OF0000031','2022-04-05 07:57:44','Data Center - Loading Dock'),
('AL0000032','CS0000032','AR0000032','OF0000032','2022-04-07 16:23:59','Field House - West Gate'),
('AL0000033','CS0000033','AR0000033','OF0000033','2022-04-09 21:35:11','Family Services Desk'),
('AL0000034','CS0000034','AR0000034','OF0000034','2022-04-12 05:49:26','Records Archive - B1'),
('AL0000035','CS0000035','AR0000035','OF0000035','2022-04-14 19:12:08','Greenway Path - Bridge'),
('AL0000036','CS0000036','AR0000036','OF0000036','2022-04-16 02:44:31','Service Alley - North'),
('AL0000037','CS0000037','AR0000037','OF0000037','2022-04-18 12:18:15','3rd Ave & Oak St'),
('AL0000038','CS0000038','AR0000038','OF0000038','2022-04-20 23:50:40','8th St - Block Party'),
('AL0000039','CS0000039','AR0000039','OF0000039','2022-04-22 09:33:19','Stadium Gate C'),
('AL0000040','CS0000040','AR0000040','OF0000040','2022-04-25 14:07:03','Union ATM - South'),

('AL0000041','CS0000041','AR0000041','OF0000041','2022-04-27 18:21:45','Campus Mall - Kiosk'),
('AL0000042','CS0000042','AR0000042','OF0000042','2022-04-29 07:05:22','Family Court - Lobby'),
('AL0000043','CS0000043','AR0000043','OF0000043','2022-05-02 10:59:13','Treasury Office - Window'),
('AL0000044','CS0000044','AR0000044','OF0000044','2022-05-04 22:41:50','5th St & River Rd'),
('AL0000045','CS0000045','AR0000045','OF0000045','2022-05-06 13:14:37','Animal Clinic - Rear'),
('AL0000046','CS0000046','AR0000046','OF0000046','2022-05-08 01:48:05','Parking Garage A - L2'),
('AL0000047','CS0000047','AR0000047','OF0000047','2022-05-10 17:03:48','Retail Plaza - Exit 1'),
('AL0000048','CS0000048','AR0000048','OF0000048','2022-05-12 03:36:31','Downtown Square'),
('AL0000049','CS0000049','AR0000049','OF0000049','2022-05-14 11:27:59','Utilities Yard - Bay 3'),
('AL0000050','CS0000050','AR0000050','OF0000050','2022-05-16 20:55:12','6th Ave & Cedar St'),

('AL0000051','CS0000051','AR0000051','OF0000051','2022-05-18 08:39:41','Property Crimes - Office'),
('AL0000052','CS0000052','AR0000052','OF0000052','2022-05-20 15:18:26','Admin Annex - HR'),
('AL0000053','CS0000053','AR0000053','OF0000053','2022-05-22 00:03:07','Broadway & 10th'),
('AL0000054','CS0000054','AR0000054','OF0000054','2022-05-24 19:29:51','Dorm D - Stairwell'),
('AL0000055','CS0000055','AR0000055','OF0000055','2022-05-26 06:12:33','Network Ops - NOC'),
('AL0000056','CS0000056','AR0000056','OF0000056','2022-05-28 23:44:18','Park Benches - East'),
('AL0000057','CS0000057','AR0000057','OF0000057','2022-05-30 12:25:49','Family Services - Intake'),
('AL0000058','CS0000058','AR0000058','OF0000058','2022-06-01 04:57:05','ME Office - Bay 1'),
('AL0000059','CS0000059','AR0000059','OF0000059','2022-06-03 16:31:40','Alley off Walnut St'),
('AL0000060','CS0000060','AR0000060','OF0000060','2022-06-05 02:14:22','Lot C - Grass Median'),

('AL0000061','CS0000061','AR0000061','OF0000061','2022-06-07 07:43:56','Stoplight @ Main'),
('AL0000062','CS0000062','AR0000062','OF0000062','2022-06-09 21:09:18','City Hall - Steps'),
('AL0000063','CS0000063','AR0000063','OF0000063','2022-06-11 18:18:31','Roof Access - Hall E'),
('AL0000064','CS0000064','AR0000064','OF0000064','2022-06-13 09:57:22','Bank Branch - ATM'),
('AL0000065','CS0000065','AR0000065','OF0000065','2022-06-15 23:41:04','Housing - Lot A'),
('AL0000066','CS0000066','AR0000066','OF0000066','2022-06-17 03:29:46','Amber Lot - East Row'),
('AL0000067','CS0000067','AR0000067','OF0000067','2022-06-19 14:52:19','Tech Annex - Lab 4'),
('AL0000068','CS0000068','AR0000068','OF0000068','2022-06-21 12:11:33','Workshop - Bay 6'),
('AL0000069','CS0000069','AR0000069','OF0000069','2022-06-23 20:07:55','Parking Lot D - South'),
('AL0000070','CS0000070','AR0000070','OF0000070','2022-06-25 05:22:41','Bike Lane - 14th'),

('AL0000071','CS0000071','AR0000071','OF0000071','2022-06-27 13:10:09','Bookstore - Register'),
('AL0000072','CS0000072','AR0000072','OF0000072','2022-06-29 22:36:42','Market St - Crosswalk'),
('AL0000073','CS0000073','AR0000073','OF0000073','2022-07-01 08:01:33','Gym - Locker Area'),
('AL0000074','CS0000074','AR0000074','OF0000074','2022-07-03 18:44:57','Bar District - Alley'),
('AL0000075','CS0000075','AR0000075','OF0000075','2022-07-05 02:58:20','Lab 3 - Equipment Bay'),
('AL0000076','CS0000076','AR0000076','OF0000076','2022-07-07 12:22:11','Student Loans Office'),
('AL0000077','CS0000077','AR0000077','OF0000077','2022-07-09 01:39:42','Hwy 12 - MM 47'),
('AL0000078','CS0000078','AR0000078','OF0000078','2022-07-11 15:26:03','Dorm E - Lounge'),
('AL0000079','CS0000079','AR0000079','OF0000079','2022-07-13 20:17:29','Payroll Office - Door'),
('AL0000080','CS0000080','AR0000080','OF0000080','2022-07-15 06:54:55','Lot B - Row 2'),

('AL0000081','CS0000081','AR0000081','OF0000081','2022-07-17 11:33:44','Family Apt - Unit 5'),
('AL0000082','CS0000082','AR0000082','OF0000082','2022-07-19 00:12:21','ME Lab - Ballistics'),
('AL0000083','CS0000083','AR0000083','OF0000083','2022-07-21 19:48:03','Alley off Birch'),
('AL0000084','CS0000084','AR0000084','OF0000084','2022-07-23 03:21:47','Locker Room - West'),
('AL0000085','CS0000085','AR0000085','OF0000085','2022-07-25 10:05:30','3rd St - Shoulder'),
('AL0000086','CS0000086','AR0000086','OF0000086','2022-07-27 21:59:58','Club Row - Patio'),
('AL0000087','CS0000087','AR0000087','OF0000087','2022-07-29 16:18:36','Dorm Roof Access'),
('AL0000088','CS0000088','AR0000088','OF0000088','2022-07-31 08:42:05','Credit Union - Teller'),
('AL0000089','CS0000089','AR0000089','OF0000089','2022-08-02 02:27:41','Lot F - North Exit'),
('AL0000090','CS0000090','AR0000090','OF0000090','2022-08-04 13:34:26','Civic Center - Lobby'),

('AL0000091','CS0000091','AR0000091','OF0000091','2022-08-06 22:07:52','Cash Business - Rear'),
('AL0000092','CS0000092','AR0000092','OF0000092','2022-08-08 05:55:33','Transit Hub - Platform'),
('AL0000093','CS0000093','AR0000093','OF0000093','2022-08-10 18:41:07','Alley off Spruce'),
('AL0000094','CS0000094','AR0000094','OF0000094','2022-08-12 07:23:44','Parking Lot H - East'),
('AL0000095','CS0000095','AR0000095','OF0000095','2022-08-14 12:58:15','Retail Mall - Fitting'),
('AL0000096','CS0000096','AR0000096','OF0000096','2022-08-16 23:47:59','Public Restroom - Plaza'),
('AL0000097','CS0000097','AR0000097','OF0000097','2022-08-18 09:31:22','Tool Shed - Yard'),
('AL0000098','CS0000098','AR0000098','OF0000098','2022-08-20 20:19:11','Dorm F - Corridor'),
('AL0000099','CS0000099','AR0000099','OF0000099','2022-08-22 04:06:45','Dorm Hall - Level 1'),
('AL0000100','CS0000100','AR0000100','OF0000100','2022-08-24 15:44:38','Charity Booth - Quad');


UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000040'
WHERE departmentId = 'D101';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000001'
WHERE departmentId = 'D102';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000002'
WHERE departmentId = 'D103';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000003'
WHERE departmentId = 'D104';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000004'
WHERE departmentId = 'D105';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000005'
WHERE departmentId = 'D106';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000006'
WHERE departmentId = 'D107';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000007'
WHERE departmentId = 'D108';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000008'
WHERE departmentId = 'D109';

UPDATE [TerpProtect.Department]
SET officerHeadId = 'OF0000009'
WHERE departmentId = 'D110';

--q1  1. Which age and sex groups have the highest number of arrests?

SELECT
  CASE
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) < 18 THEN '<18'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 18 AND 24 THEN '18-24'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 25 AND 34 THEN '25-34'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 35 AND 44 THEN '35-44'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 45 AND 54 THEN '45-54'
    ELSE '55+'
  END AS ageGroup,
  COALESCE(a.arresteeSex, 'Unknown') AS arresteeSex,
  COUNT(*) AS arrests
FROM [TerpProtect.ArrestLog] al
JOIN [TerpProtect.Arrestee] a ON a.arresteeId = al.arresteeId
GROUP BY
  CASE
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) < 18 THEN '<18'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 18 AND 24 THEN '18-24'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 25 AND 34 THEN '25-34'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 35 AND 44 THEN '35-44'
    WHEN DATEDIFF(year, a.arresteeDOB, al.arrestLogTimeStamp) BETWEEN 45 AND 54 THEN '45-54'
    ELSE '55+'
  END,
  COALESCE(a.arresteeSex, 'Unknown')
ORDER BY arrests DESC, ageGroup, arresteeSex;







--q2 Determine the most common charge categories leading to arrests and how they vary over time.(by month)
SELECT
  CAST(DATEFROMPARTS(YEAR(al.arrestLogTimeStamp), MONTH(al.arrestLogTimeStamp), 1) AS DATE) AS arrestMonth,
  COALESCE(ccc.caseChargeCategory, 'Unknown') AS caseChargeCategory,
  COUNT(*) AS arrestsWithCategory
FROM [TerpProtect.ArrestLog] al
JOIN [TerpProtect.CaseChargeCategory] ccc ON ccc.caseId = al.caseId
GROUP BY
  CAST(DATEFROMPARTS(YEAR(al.arrestLogTimeStamp), MONTH(al.arrestLogTimeStamp), 1) AS DATE),
  COALESCE(ccc.caseChargeCategory, 'Unknown')
ORDER BY arrestMonth, arrestsWithCategory DESC, caseChargeCategory;




--q3  Calculate the number and proportion of reported cases that did not result in any arrest.

  SELECT
  COALESCE(SUM(CASE WHEN al.caseId IS NULL THEN 1 ELSE 0 END), 0) AS casesWithNoArrest,
  COALESCE(COUNT(*), 0) AS totalCases,
  COALESCE(
    CAST(
      1.0 * SUM(CASE WHEN al.caseId IS NULL THEN 1 ELSE 0 END) 
      / NULLIF(COUNT(*), 0) AS DECIMAL(5,2)
    ), 0.00
  ) AS proportionNoArrest
FROM [TerpProtect.Case] c
LEFT JOIN (
  SELECT DISTINCT caseId 
  FROM [TerpProtect.ArrestLog]
) al ON al.caseId = c.caseId;




--q4 Compute and compare the average case duration across departments to identify performance differences.



WITH FirstArrest AS (
  SELECT caseId, MIN(arrestLogTimeStamp) AS firstTs
  FROM [TerpProtect.ArrestLog]
  GROUP BY caseId
),
OwnerDept AS (
  SELECT fa.caseId, MIN(o.departmentId) AS departmentId
  FROM FirstArrest fa
  JOIN [TerpProtect.ArrestLog] al
    ON al.caseId = fa.caseId AND al.arrestLogTimeStamp = fa.firstTs
  JOIN [TerpProtect.Officer] o ON o.officerId = al.officerId
  GROUP BY fa.caseId
),
LastArrest AS (
  SELECT caseId, MAX(arrestLogTimeStamp) AS lastTs
  FROM [TerpProtect.ArrestLog]
  GROUP BY caseId
),
CaseDur AS (
  SELECT
    od.departmentId,
    c.caseId,
    CASE
      WHEN c.caseClosedOn IS NOT NULL
        THEN DATEDIFF(day, c.caseReportedOn, c.caseClosedOn)
      WHEN la.lastTs IS NOT NULL
        THEN DATEDIFF(day, c.caseReportedOn, la.lastTs)
      ELSE NULL
    END AS durationDays
  FROM [TerpProtect.Case] c
  JOIN OwnerDept od ON od.caseId = c.caseId
  LEFT JOIN LastArrest la ON la.caseId = c.caseId
)
SELECT
  COALESCE(d.departmentId, 'UNKNOWN') AS departmentId,
  COALESCE(d.departmentName, 'Unknown Department') AS departmentName,
  AVG(CAST(cd.durationDays AS FLOAT)) AS avgCaseDurationDays,
  COUNT(*) AS casesCounted
FROM CaseDur cd
JOIN [TerpProtect.Department] d ON d.departmentId = cd.departmentId
WHERE cd.durationDays IS NOT NULL
GROUP BY d.departmentId, d.departmentName
ORDER BY avgCaseDurationDays;



--q5  Identify which departments and department heads have recorded the highest number of arrests and handled the most cases.
SELECT
  COALESCE(d.departmentId, 'Unknown') AS departmentId,
  COALESCE(d.departmentName, 'Unknown Department') AS departmentName,
  COALESCE(d.officerHeadId, 'Unassigned') AS officerHeadId,
  COALESCE(head.officerFirstName + ' ' + head.officerLastName, 'No Head Assigned') AS departmentHead,
  COUNT(al.arrestLogId) AS totalArrests,
  COUNT(DISTINCT al.caseId) AS distinctCasesHandled
FROM [TerpProtect.Department] d
LEFT JOIN [TerpProtect.Officer] head ON head.officerId = d.officerHeadId
LEFT JOIN [TerpProtect.Officer] o ON o.departmentId = d.departmentId
LEFT JOIN [TerpProtect.ArrestLog] al ON al.officerId = o.officerId
GROUP BY
  d.departmentId,
  d.departmentName,
  d.officerHeadId,
  head.officerFirstName,
  head.officerLastName
ORDER BY
  totalArrests DESC,
  distinctCasesHandled DESC,
  d.departmentName;



--q6 Most frequently handled case types by each department (top 1 per department)
WITH DeptCase AS (
  SELECT
    COALESCE(d.departmentId, 'Unknown') AS departmentId,
    COALESCE(d.departmentName, 'Unknown Department') AS departmentName,
    COALESCE(c.caseType, 'Unknown Case Type') AS caseType,
    COUNT(*) AS handledCount
  FROM [TerpProtect.ArrestLog] al
  JOIN [TerpProtect.Officer] o ON o.officerId = al.officerId
  JOIN [TerpProtect.Department] d ON d.departmentId = o.departmentId
  JOIN [TerpProtect.Case] c ON c.caseId = al.caseId
  GROUP BY d.departmentId, d.departmentName, c.caseType
),
Ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY departmentId 
           ORDER BY handledCount DESC, caseType
         ) AS rn
  FROM DeptCase
)
SELECT departmentId, departmentName, caseType, handledCount
FROM Ranked
WHERE rn = 1
ORDER BY departmentName;


































select * from [TerpProtect.Department]

select * from [TerpProtect.Officer]

select * from [TerpProtect.CaseChargeCategory]



select * from [TerpProtect.Arrestee]

select * from [TerpProtect.ArrestLog]