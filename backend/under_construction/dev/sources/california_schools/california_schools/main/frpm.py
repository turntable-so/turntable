# type: ignore
from vinyl import Field, source # noqa F401
from vinyl import types as t # noqa F401

from dev.resources import california_schools # noqa F401 


@source(resource=california_schools)
class Frpm:
    _table = "frpm"
    _unique_name = "california_schools.california_schools.main.Frpm"
    _schema = "main"
    _database = "california_schools"
    _twin_path = "data/california_schools/main/california_schools.duckdb"
    _path = "data/dev_databases/california_schools/california_schools.sqlite"
    _row_count = 9986
    _col_replace = {"Academic_Year": "Academic Year", "County_Code": "County Code", "District_Code": "District Code", "School_Code": "School Code", "County_Name": "County Name", "District_Name": "District Name", "School_Name": "School Name", "District_Type": "District Type", "School_Type": "School Type", "Educational_Option_Type": "Educational Option Type", "NSLP_Provision_Status": "NSLP Provision Status", "Charter_School__Y_N_": "Charter School (Y/N)", "Charter_School_Number": "Charter School Number", "Charter_Funding_Type": "Charter Funding Type", "Low_Grade": "Low Grade", "High_Grade": "High Grade", "Enrollment__K_12_": "Enrollment (K-12)", "Free_Meal_Count__K_12_": "Free Meal Count (K-12)", "Percent_____Eligible_Free__K_12_": "Percent (%) Eligible Free (K-12)", "FRPM_Count__K_12_": "FRPM Count (K-12)", "Percent_____Eligible_FRPM__K_12_": "Percent (%) Eligible FRPM (K-12)", "Enrollment__Ages_5_17_": "Enrollment (Ages 5-17)", "Free_Meal_Count__Ages_5_17_": "Free Meal Count (Ages 5-17)", "Percent_____Eligible_Free__Ages_5_17_": "Percent (%) Eligible Free (Ages 5-17)", "FRPM_Count__Ages_5_17_": "FRPM Count (Ages 5-17)", "Percent_____Eligible_FRPM__Ages_5_17_": "Percent (%) Eligible FRPM (Ages 5-17)", "_2013_14_CALPADS_Fall_1_Certification_Status": "2013-14 CALPADS Fall 1 Certification Status"}

    CDSCode: t.String(nullable=False) = Field(description='''CDSCode''', foreign_key=('Schools', 'CDSCode'), unique = True)
    Academic_Year: t.String(nullable=True) = Field(description='''Academic Year''')
    County_Code: t.String(nullable=True) = Field(description='''County Code''')
    District_Code: t.Int64(nullable=True) = Field(description='''District Code''')
    School_Code: t.String(nullable=True)
    County_Name: t.String(nullable=True) = Field(description='''County Code ''')
    District_Name: t.String(nullable=True)
    School_Name: t.String(nullable=True) = Field(description='''School Name ''')
    District_Type: t.String(nullable=True) = Field(description='''District Type''')
    School_Type: t.String(nullable=True)
    Educational_Option_Type: t.String(nullable=True) = Field(description='''Educational Option Type''')
    NSLP_Provision_Status: t.String(nullable=True) = Field(description='''NSLP Provision Status''')
    Charter_School__Y_N_: t.Int64(nullable=True) = Field(description='''Charter School (Y/N). Additional context: 0: N;
1: Y''')
    Charter_School_Number: t.String(nullable=True) = Field(description='''Charter School Number''')
    Charter_Funding_Type: t.String(nullable=True) = Field(description='''Charter Funding Type''')
    IRC: t.Int64(nullable=True) = Field(description='''nan. Additional context: Not useful''')
    Low_Grade: t.String(nullable=True) = Field(description='''Low Grade''')
    High_Grade: t.String(nullable=True) = Field(description='''High Grade''')
    Enrollment__K_12_: t.Float64(nullable=True) = Field(description='''Enrollment (K-12). Additional context: 

K-12: 1st grade - 12nd grade ''')
    Free_Meal_Count__K_12_: t.Float64(nullable=True) = Field(description='''Free Meal Count (K-12). Additional context: 

eligible free rate = Free Meal Count / Enrollment''')
    Percent_____Eligible_Free__K_12_: t.Float64(nullable=True)
    FRPM_Count__K_12_: t.Float64(nullable=True) = Field(description='''Free or Reduced Price Meal Count (K-12). Additional context: 

eligible FRPM rate = FRPM / Enrollment''')
    Percent_____Eligible_FRPM__K_12_: t.Float64(nullable=True)
    Enrollment__Ages_5_17_: t.Float64(nullable=True) = Field(description='''Enrollment (Ages 5-17)''')
    Free_Meal_Count__Ages_5_17_: t.Float64(nullable=True) = Field(description='''Free Meal Count (Ages 5-17). Additional context: 

eligible free rate = Free Meal Count / Enrollment''')
    Percent_____Eligible_Free__Ages_5_17_: t.Float64(nullable=True)
    FRPM_Count__Ages_5_17_: t.Float64(nullable=True)
    Percent_____Eligible_FRPM__Ages_5_17_: t.Float64(nullable=True)
    _2013_14_CALPADS_Fall_1_Certification_Status: t.Int64(nullable=True) = Field(description='''2013-14 CALPADS Fall 1 Certification Status''')

