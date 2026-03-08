-- ============================================================
-- SPACE RESEARCH ORGANIZATION DATABASE
-- PostgreSQL Schema (for Neon.tech cloud database)
-- ============================================================

-- Drop tables in reverse order
DROP TABLE IF EXISTS CONDUCTS CASCADE;
DROP TABLE IF EXISTS CREWED_BY CASCADE;
DROP TABLE IF EXISTS TELEMETRY_DATA CASCADE;
DROP TABLE IF EXISTS EXP_EQUIP CASCADE;
DROP TABLE IF EXISTS ASTRONAUT_SKILLS CASCADE;
DROP TABLE IF EXISTS MISSION CASCADE;
DROP TABLE IF EXISTS EXPERIMENT CASCADE;
DROP TABLE IF EXISTS ASTRONAUT CASCADE;
DROP TABLE IF EXISTS SPACECRAFT CASCADE;
DROP TABLE IF EXISTS CONTROL_CENTER CASCADE;

-- Table 1: SPACECRAFT
CREATE TABLE SPACECRAFT (
    CraftID      VARCHAR(10)  PRIMARY KEY,
    CName        VARCHAR(50)  NOT NULL,
    Manufacturer VARCHAR(50)  NOT NULL,
    FuelType     VARCHAR(30)  NOT NULL,
    Length       NUMERIC(6,2),
    Width        NUMERIC(6,2),
    Height       NUMERIC(6,2)
);

-- Table 2: CONTROL_CENTER
CREATE TABLE CONTROL_CENTER (
    CenterID     VARCHAR(10)  PRIMARY KEY,
    CenterName   VARCHAR(100) NOT NULL,
    City         VARCHAR(50)  NOT NULL,
    Country      VARCHAR(50)  NOT NULL
);

-- Table 3: MISSION
CREATE TABLE MISSION (
    MissionID       VARCHAR(10)  PRIMARY KEY,
    MName           VARCHAR(100) NOT NULL,
    MStatus         VARCHAR(20)  NOT NULL CHECK (MStatus IN ('Planned','Active','Completed','Aborted')),
    LaunchDate      DATE         NOT NULL,
    CraftID         VARCHAR(10)  REFERENCES SPACECRAFT(CraftID),
    CenterID        VARCHAR(10)  REFERENCES CONTROL_CENTER(CenterID),
    MonitoringShift VARCHAR(20)
);

-- Table 4: ASTRONAUT
CREATE TABLE ASTRONAUT (
    AstronautID  VARCHAR(10)  PRIMARY KEY,
    FirstName    VARCHAR(50)  NOT NULL,
    LastName     VARCHAR(50)  NOT NULL,
    DOB          DATE         NOT NULL,
    Nationality  VARCHAR(50)  NOT NULL
);

-- Table 5: ASTRONAUT_SKILLS (multivalued attribute — 1NF fix)
CREATE TABLE ASTRONAUT_SKILLS (
    AstronautID  VARCHAR(10)  REFERENCES ASTRONAUT(AstronautID) ON DELETE CASCADE,
    Skill        VARCHAR(50)  NOT NULL,
    PRIMARY KEY (AstronautID, Skill)
);

-- Table 6: EXPERIMENT
CREATE TABLE EXPERIMENT (
    ExpID    VARCHAR(10)  PRIMARY KEY,
    ExpName  VARCHAR(100) NOT NULL,
    Domain   VARCHAR(50)  NOT NULL
);

-- Table 7: EXP_EQUIP (multivalued attribute — 1NF fix)
CREATE TABLE EXP_EQUIP (
    ExpID      VARCHAR(10)  REFERENCES EXPERIMENT(ExpID) ON DELETE CASCADE,
    Equipment  VARCHAR(50)  NOT NULL,
    PRIMARY KEY (ExpID, Equipment)
);

-- Table 8: TELEMETRY_DATA (weak entity)
CREATE TABLE TELEMETRY_DATA (
    TelemetryID      VARCHAR(10)  PRIMARY KEY,
    SignalStrength   NUMERIC(5,2) NOT NULL,
    TransmissionTime TIMESTAMP    NOT NULL,
    Temperature      NUMERIC(6,2) NOT NULL,
    MissionID        VARCHAR(10)  NOT NULL REFERENCES MISSION(MissionID) ON DELETE CASCADE
);

-- Table 9: CREWED_BY (M:N relationship)
CREATE TABLE CREWED_BY (
    MissionID    VARCHAR(10) REFERENCES MISSION(MissionID) ON DELETE CASCADE,
    AstronautID  VARCHAR(10) REFERENCES ASTRONAUT(AstronautID) ON DELETE CASCADE,
    PRIMARY KEY (MissionID, AstronautID)
);

-- Table 10: CONDUCTS (ternary relationship)
CREATE TABLE CONDUCTS (
    MissionID    VARCHAR(10) REFERENCES MISSION(MissionID) ON DELETE CASCADE,
    ExpID        VARCHAR(10) REFERENCES EXPERIMENT(ExpID) ON DELETE CASCADE,
    AstronautID  VARCHAR(10) REFERENCES ASTRONAUT(AstronautID) ON DELETE CASCADE,
    ExpStart     DATE,
    ExpEnd       DATE,
    PRIMARY KEY (MissionID, ExpID, AstronautID)
);

-- ── Seed Data ─────────────────────────────────────────────────────────────────

INSERT INTO SPACECRAFT VALUES
    ('SC001','Artemis-1','NASA/Lockheed','LH2/LOX',98.0,8.4,8.4),
    ('SC002','Falcon Heavy','SpaceX','RP-1/LOX',70.0,12.2,12.2),
    ('SC003','Orion MK II','ESA/Airbus','LH2/LOX',5.02,5.02,3.3);

INSERT INTO CONTROL_CENTER VALUES
    ('CC001','Kennedy Space Center','Cape Canaveral','USA'),
    ('CC002','Johnson Space Center','Houston','USA'),
    ('CC003','European Space Operations Centre','Darmstadt','Germany');

INSERT INTO MISSION VALUES
    ('M001','Artemis Lunar Gateway','Active','2024-11-16','SC001','CC001','Day'),
    ('M002','Mars Reconnaissance Alpha','Planned','2026-03-01','SC002','CC002','Night'),
    ('M003','Deep Space Biology','Completed','2023-06-12','SC003','CC003','Swing');

INSERT INTO ASTRONAUT VALUES
    ('A001','Neil','Armstrong Jr.','1980-05-14','American'),
    ('A002','Yuki','Tanaka','1985-09-22','Japanese'),
    ('A003','Sofia','Martinez','1990-02-08','Spanish'),
    ('A004','Raj','Patel','1983-11-30','Indian');

INSERT INTO ASTRONAUT_SKILLS VALUES
    ('A001','EVA'),('A001','Navigation'),
    ('A002','Robotics'),('A002','Medical'),
    ('A003','Biology'),('A003','Chemistry'),
    ('A004','Engineering'),('A004','Navigation');

INSERT INTO EXPERIMENT VALUES
    ('E001','Protein Crystallization','Biology'),
    ('E002','Cosmic Ray Detection','Physics'),
    ('E003','Plant Growth in Microgravity','Botany');

INSERT INTO EXP_EQUIP VALUES
    ('E001','Centrifuge'),('E001','Microscope'),
    ('E002','Geiger Counter'),('E002','Spectrometer'),
    ('E003','Growth Chamber'),('E003','UV Lamp');

INSERT INTO TELEMETRY_DATA VALUES
    ('T001',87.4,'2024-11-17 14:32:00',22.1,'M001'),
    ('T002',91.2,'2024-11-18 09:15:00',-10.5,'M001'),
    ('T003',45.8,'2024-11-19 22:00:00',18.3,'M001');

INSERT INTO CREWED_BY VALUES
    ('M001','A001'),('M001','A002'),
    ('M002','A003'),('M002','A004'),
    ('M003','A001'),('M003','A003');

INSERT INTO CONDUCTS VALUES
    ('M001','E001','A002','2024-11-18','2024-11-20'),
    ('M001','E002','A001','2024-11-17','2024-11-19'),
    ('M003','E003','A003','2023-06-13','2023-06-18');
