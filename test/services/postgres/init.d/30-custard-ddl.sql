DROP TABLE IF EXISTS docma.custard CASCADE;

CREATE TABLE docma.custard
(
    ID               INTEGER,
    CustardClubNo    INTEGER,
    GivenName        VARCHAR(20),
    FamilyName       VARCHAR(30),
    Sex              VARCHAR(1),
    CustardBidPrice  FLOAT(2),
    CustardCode      VARCHAR(10),
    FavouriteCustard VARCHAR(10),
    CustardJedi      BOOLEAN,
    City             VARCHAR(50),
    PostCode         VARCHAR(20),
    Email            VARCHAR(100),
    Phone            VARCHAR(20),
    LastCustard      DATE,
    CustardQuota     INTEGER
);

ALTER TABLE docma.custard OWNER TO docma;

COPY docma.custard FROM '/data/custard100.csv' CSV HEADER;
