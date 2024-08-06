# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import california_schools # noqa F401 


@source(resource=california_schools)
class Schools:
    _table = "schools"
    _unique_name = "california_schools.california_schools.main.Schools"
    _schema = "main"
    _database = "california_schools"
    _twin_path = "data/california_schools/main/california_schools.duckdb"
    _path = "data/dev_databases/california_schools/california_schools.sqlite"
    _row_count = 17686
    _col_replace = {}

    CDSCode: t.String(nullable=False) = Field(description='''CDSCode''', primary_key=True)
    NCESDist: t.String(nullable=True) = Field(description='''This field represents the 7-digit National Center for Educational Statistics (NCES) school district identification number. The first 2 digits identify the state and the last 5 digits identify the school district. Combined, they make a unique 7-digit ID for each school district.''')
    NCESSchool: t.String(nullable=True) = Field(description='''This field represents the 5-digit NCES school identification number. The NCESSchool combined with the NCESDist form a unique 12-digit ID for each school.''')
    StatusType: t.String(nullable=False) = Field(description='''This field identifies the status of the district. . Additional context: Definitions of the valid status types are listed below:
·       Active: The district is in operation and providing instructional services.
·       Closed: The district is not in operation and no longer providing instructional services.
·       Merged: The district has combined with another district or districts.
·       Pending: The district has not opened for operation and instructional services yet, but plans to open within the next 9–12 months.''')
    County: t.String(nullable=False) = Field(description='''County name''')
    District: t.String(nullable=False) = Field(description='''District''')
    School: t.String(nullable=True) = Field(description='''School''')
    Street: t.String(nullable=True) = Field(description='''Street''')
    StreetAbr: t.String(nullable=True) = Field(description='''The abbreviated street address of the school, district, or administrative authority’s physical location.. Additional context: The abbreviated street address of the school, district, or administrative authority’s physical location. Note: Some records (primarily records of closed or retired schools) may not have data in this field.''')
    City: t.String(nullable=True) = Field(description='''City''')
    Zip: t.String(nullable=True) = Field(description='''Zip''')
    State: t.String(nullable=True) = Field(description='''State''')
    MailStreet: t.String(nullable=True) = Field(description='''MailStreet. Additional context: The unabbreviated mailing address of the school, district, or administrative authority. Note: 1) Some entities (primarily closed or retired schools) may not have data in this field; 2) Many active entities have not provided a mailing street address. For your convenience we have filled the unpopulated MailStreet cells with Street data.''')
    MailStrAbr: t.String(nullable=True) = Field(description='''nan. Additional context: the abbreviated mailing street address of the school, district, or administrative authority.Note: Many active entities have not provided a mailing street address. For your convenience we have filled the unpopulated MailStrAbr cells with StreetAbr data.''')
    MailCity: t.String(nullable=True) = Field(description='''nan. Additional context: The city associated with the mailing address of the school, district, or administrative authority. Note: Many entities have not provided a mailing address city. For your convenience we have filled the unpopulated MailCity cells with City data.''')
    MailZip: t.String(nullable=True) = Field(description='''nan. Additional context: The zip code associated with the mailing address of the school, district, or administrative authority. Note: Many entities have not provided a mailing address zip code. For your convenience we have filled the unpopulated MailZip cells with Zip data.''')
    MailState: t.String(nullable=True) = Field(description='''nan. Additional context: The state within the mailing address. For your convenience we have filled the unpopulated MailState cells with State data.''')
    Phone: t.String(nullable=True) = Field(description='''Phone''')
    Ext: t.String(nullable=True) = Field(description='''The phone number extension of the school, district, or administrative authority.. Additional context: The phone number extension of the school, district, or administrative authority.''')
    Website: t.String(nullable=True) = Field(description='''The website address of the school, district, or administrative authority.. Additional context: The website address of the school, district, or administrative authority.''')
    OpenDate: t.Date(nullable=True) = Field(description='''The date the school opened.''')
    ClosedDate: t.Date(nullable=True) = Field(description='''The date the school closed.''')
    Charter: t.Int64(nullable=True) = Field(description='''This field identifies a charter school. . Additional context: The field is coded as follows:

·       1 = The school is a charter

·       0 = The school is not a charter''')
    CharterNum: t.String(nullable=True) = Field(description='''The charter school number,. Additional context: 4-digit number assigned to a charter school.''')
    FundingType: t.String(nullable=True) = Field(description='''Indicates the charter school funding type. Additional context: Values are as follows:

·       Not in CS (California School) funding model

·       Locally funded

·       Directly funded''')
    DOC: t.String(nullable=False) = Field(description='''District Ownership Code. Additional context: The District Ownership Code (DOC) is the numeric code used to identify the category of the Administrative Authority.
•       00 - County Office of Education
•       02 – State Board of Education
•       03 – Statewide Benefit Charter
•       31 – State Special Schools
•       34 – Non-school Location*
•       52 – Elementary School District
•       54 – Unified School District
•       56 – High School District
•       98 – Regional Occupational Center/Program (ROC/P)

*Only the California Education Authority has been included in the non-school location category.''')
    DOCType: t.String(nullable=False) = Field(description='''The District Ownership Code Type is the text description of the DOC category.. Additional context: (See text values in DOC field description above)''')
    SOC: t.String(nullable=True) = Field(description='''The School Ownership Code is a numeric code used to identify the type of school.. Additional context: •      08 - Preschool      
•       09 – Special Education Schools (Public)
•      11 – Youth Authority Facilities (CEA)
•       13 – Opportunity Schools
•       14 – Juvenile Court Schools
•       15 – Other County or District Programs
•       31 – State Special Schools
•       60 – Elementary School (Public)
•       61 – Elementary School in 1 School District (Public)
•       62 – Intermediate/Middle Schools (Public)
•       63 – Alternative Schools of Choice
•       64 – Junior High Schools (Public)
•       65 – K-12 Schools (Public)
•       66 – High Schools (Public)
•       67 – High Schools in 1 School District (Public)
•       68 – Continuation High Schools
•       69 – District Community Day Schools
•       70 – Adult Education Centers
•       98 – Regional Occupational Center/Program (ROC/P)''')
    SOCType: t.String(nullable=True) = Field(description='''The School Ownership Code Type is the text description of the type of school.. Additional context: The School Ownership Code Type is the text description of the type of school.''')
    EdOpsCode: t.String(nullable=True) = Field(description='''The Education Option Code is a short text description of the type of education offered.. Additional context: 
•      ALTSOC – Alternative School of Choice
•      COMM – County Community School
•       COMMDAY – Community Day School
•       CON – Continuation School
•       JUV – Juvenile Court School
•       OPP – Opportunity School
•       YTH – Youth Authority School
•       SSS – State Special School
•       SPEC – Special Education School
•       TRAD – Traditional
•       ROP – Regional Occupational Program
•       HOMHOS – Home and Hospital
•       SPECON – District Consortia Special Education School''')
    EdOpsName: t.String(nullable=True) = Field(description='''Educational Option Name. Additional context: The Educational Option Name is the long text description of the type of education being offered.''')
    EILCode: t.String(nullable=True) = Field(description='''The Educational Instruction Level Code is a short text description of the institution's type relative to the grade range served.. Additional context: •       A – Adult
•       ELEM – Elementary
•       ELEMHIGH – Elementary-High Combination
•       HS – High School
•       INTMIDJR – Intermediate/Middle/Junior High
•       PS – Preschool
•       UG – Ungraded''')
    EILName: t.String(nullable=True) = Field(description='''The Educational Instruction Level Name is the long text description of the institution’s type relative to the grade range served.. Additional context: The Educational Instruction Level Name is the long text description of the institution’s type relative to the grade range served.''')
    GSoffered: t.String(nullable=True) = Field(description='''The grade span offered is the lowest grade and the highest grade offered or supported by the school, district, or administrative authority. This field might differ from the grade span served as reported in the most recent certified California Longitudinal Pupil Achievement (CALPADS) Fall 1 data collection.. Additional context: For example XYZ School might display the following data:

GSoffered = P–Adult

GSserved = K–12''')
    GSserved: t.String(nullable=True) = Field(description='''It is the lowest grade and the highest grade of student enrollment as reported in the most recent certified CALPADS Fall 1 data collection. Only K–12 enrollment is reported through CALPADS. This field may differ from the grade span offered.. Additional context: 

1.     Only K–12 enrollment is reported through CALPADS

2.     Note: Special programs at independent study, alternative education, and special education schools will often exceed the typical grade span for schools of that type''')
    Virtual: t.String(nullable=True) = Field(description='''This field identifies the type of virtual instruction offered by the school. Virtual instruction is instruction in which students and teachers are separated by time and/or location, and interaction occurs via computers and/or telecommunications technologies. . Additional context: The field is coded as follows:

·       F = Exclusively Virtual – The school has no physical building where students meet with each other or with teachers, all instruction is virtual.

·       V = Primarily Virtual – The school focuses on a systematic program of virtual instruction but includes some physical meetings among students or with teachers.

·       C = Primarily Classroom – The school offers virtual courses but virtual instruction is not the primary means of instruction.

·       N = Not Virtual – The school does not offer any virtual instruction.

·       P = Partial Virtual – The school offers some, but not all, instruction through virtual instruction. Note: This value was retired and replaced with the Primarily Virtual and Primarily Classroom values beginning with the 2016–17 school year.''')
    Magnet: t.Int64(nullable=True) = Field(description='''This field identifies whether a school is a magnet school and/or provides a magnet program. . Additional context: The field is coded as follows:

·       Y = Magnet - The school is a magnet school and/or offers a magnet program.

·       N = Not Magnet - The school is not a magnet school and/or does not offer a magnet program.



Note: Preschools and adult education centers do not contain a magnet school indicator.''')
    Latitude: t.Float64(nullable=True) = Field(description='''The angular distance (expressed in degrees) between the location of the school, district, or administrative authority and the equator measured north to south.. Additional context: The angular distance (expressed in degrees) between the location of the school, district, or administrative authority and the equator measured north to south.''')
    Longitude: t.Float64(nullable=True) = Field(description='''The angular distance (expressed in degrees) between the location of the school, district, or administrative authority and the prime meridian (Greenwich, England) measured from west to east.. Additional context: The angular distance (expressed in degrees) between the location of the school, district, or administrative authority and the prime meridian (Greenwich, England) measured from west to east.''')
    AdmFName1: t.String(nullable=True) = Field(description='''administrator's first name. Additional context: The superintendent’s or principal’s first name.



Only active and pending districts and schools will display administrator information, if applicable.''')
    AdmLName1: t.String(nullable=True) = Field(description='''administrator's last name. Additional context: The superintendent’s or principal’s last name.


Only active and pending districts and schools will display administrator information, if applicable.''')
    AdmEmail1: t.String(nullable=True) = Field(description='''administrator's email address. Additional context: The superintendent’s or principal’s email address.



Only active and pending districts and schools will display administrator information, if applicable.''')
    AdmFName2: t.String(nullable=True) = Field(description='''nan. Additional context: SAME as 1''')
    AdmLName2: t.String(nullable=True)
    AdmEmail2: t.String(nullable=True)
    AdmFName3: t.String(nullable=True) = Field(description='''nan. Additional context: not useful''')
    AdmLName3: t.String(nullable=True) = Field(description='''nan. Additional context: not useful''')
    AdmEmail3: t.String(nullable=True) = Field(description='''nan. Additional context: not useful''')
    LastUpdate: t.Date(nullable=False) = Field(description='''nan. Additional context: when is this record updated last time''')

