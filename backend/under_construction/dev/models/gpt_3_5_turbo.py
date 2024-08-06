from vinyl import model, join
from vinyl import T
from dev.sources.california_schools.california_schools.main.satscores import Satscores
from dev.sources.california_schools.california_schools.main.schools import Schools
from dev.sources.california_schools.california_schools.main.frpm import Frpm


# question_id: 15
# db_id: california_schools
# question: Which active district has the highest average score in Reading?
# evidence: 
# SQL: SELECT T1.District FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Active' ORDER BY T2.AvgScrRead DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def highest_avg_reading_score_in_active_district(s: T, sa: T) -> T:
    j = join(s, sa, on=[s.CDSCode == sa.cds])
    j.filter(s.StatusType == "Active")
    j.aggregate(j.AvgScrRead.max())



# question_id: 16
# db_id: california_schools
# question: How many schools in merged Alameda have number of test takers less than 100?
# evidence: 
# SQL: SELECT COUNT(T1.CDSCode) FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Merged' AND T2.NumTstTakr < 100 AND T1.County = 'Alameda'
# difficulty: simple
@model(deps=[Schools, Satscores])
def num_schools_with_few_test_takers(s: T, ss: T) -> T:
    j = join(s, ss, on=[s.CDSCode == ss.cds])
    j.filter((s.County == "Alameda") & (s.StatusType == "Merged") & (ss.NumTstTakr < 100))
    return j.aggregate(j.CDSCode.count())



# question_id: 17
# db_id: california_schools
# question: What is the charter number of the school that the average score in Writing is 499?
# evidence: 
# SQL: SELECT T1.CharterNum FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T2.AvgScrWrite = 499
# difficulty: simple
@model(deps=[Schools, Satscores])
def charter_number_with_avg_score_writing_499(s: T, sa: T) -> T:
    j = join(s, sa, on=[s.CDSCode == sa.cds])
    j.filter(sa.AvgScrWrite == 499)
    return j.select(s.CharterNum)



# question_id: 18
# db_id: california_schools
# question: How many schools in Contra Costa (directly funded) have number of test takers not more than 250?
# evidence: 
# SQL: SELECT COUNT(T1.CDSCode) FROM frpm AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.`Charter Funding Type` = 'Directly funded' AND T1.`County Name` = 'Contra Costa' AND T2.NumTstTakr <= 250
# difficulty: simple
@model(deps=[Frpm, Schools, Satscores])
def schools_in_contra_costa(s: T, f: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
    j = join(j, f, on=[j.CDSCode == f.CDSCode])
    j.filter((s.County == "Contra Costa") & (f.Charter_Funding_Type == "Directly funded") & (ss.NumTstTakr <= 250))
    return j.aggregate(j.CDSCode.count())



# question_id: 19
# db_id: california_schools
# question: What is the phone number of the school that has the highest average score in Math?
# evidence: 
# SQL: SELECT T1.Phone FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds ORDER BY T2.AvgScrMath DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def highest_math_score_school_phone(s: T, ss: T) -> T:
    j = join(s, ss, on=[s.CDSCode == ss.cds])
    j.sort(-ss.AvgScrMath)
    result = j.select(s.Phone).limit(1)
    return result



# question_id: 20
# db_id: california_schools
# question: How many schools in Amador which the Low Grade is 9 and the High Grade is 12?
# evidence: 
# SQL: SELECT COUNT(T1.`School Name`) FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Amador' AND T1.`Low Grade` = 9 AND T1.`High Grade` = 12
# difficulty: simple
@model(deps=[Schools])
def schools_in_Amador_with_grade_9_to_12(s: T) -> T:
    j = s.filter((s.County == "Amador") & (s.Low_Grade == "9") & (s.High_Grade == "12"))
    return j.aggregate(j.CDSCode.count())



# question_id: 21
# db_id: california_schools
# question: In Los Angeles how many schools have more than 500 free meals but less than 700 free or reduced price meals for K-12?
# evidence: 
# SQL: SELECT COUNT(CDSCode) FROM frpm WHERE `County Name` = 'Los Angeles' AND `Free Meal Count (K-12)` > 500 AND `Free Meal Count (K-12)` < 700
# difficulty: simple
@model(deps=[Frpm, Schools])
def schools_with_specific_free_meals_count(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.filter((s.County == "Los Angeles") & (f.Free_Meal_Count__K_12_ > 500) & (f.FRPM_Count__K_12_ < 700))
    return j.aggregate(j.CDSCode.count())



# question_id: 22
# db_id: california_schools
# question: Which school in Contra Costa has the highest number of test takers?
# evidence: 
# SQL: SELECT sname FROM satscores WHERE cname = 'Contra Costa' AND sname IS NOT NULL ORDER BY NumTstTakr DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def school_with_highest_test_takers(s: T, sat: T) -> T:
    j = join(s, sat, on=[s.CDSCode == sat.cds])
    j.sort(-sat.NumTstTakr)
    j.select(s.School_Name)
    return j.limit(1)



# question_id: 23
# db_id: california_schools
# question: List the names of schools with more than 30 difference in enrollements between K-12 and ages 5-17? Please also give the full street adress of the schools.
# evidence: Diffrence in enrollement = `Enrollment (K-12)` - `Enrollment (Ages 5-17)`
# SQL: SELECT T1.School, T1.StreetAbr FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.`Enrollment (K-12)` - T2.`Enrollment (Ages 5-17)` > 30
# difficulty: moderate
@model(deps=[Frpm, Schools])
def schools_with_enrollment_difference(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.define({"enrollment_difference": j.Enrollment__K_12_ - j.Enrollment__Ages_5_17_})
    j.filter(j.enrollment_difference > 30)
    result = j.select(s.School_Name, s.MailStreet)
    return result


# question_id: 24
# db_id: california_schools
# question: Give the names of the schools with the percent eligible for free meals in K-12 is more than 0.1 and test takers whose test score is greater than or equal to 1500?
# evidence: 
# SQL: SELECT T2.`School Name` FROM satscores AS T1 INNER JOIN frpm AS T2 ON T1.cds = T2.CDSCode WHERE CAST(T2.`Free Meal Count (K-12)` AS REAL) / T2.`Enrollment (K-12)` > 0.1 AND T1.NumGE1500 > 0
# difficulty: moderate
@model(deps=[Frpm, Satscores])
def schools_with_high_eligibility_and_high_scores(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.cds])
    j.filter((j.Percent_____Eligible_Free__K_12_ > 0.1) & (j.NumGE1500 > 0))
    j.select(j.School_Name)
    return j



# question_id: 25
# db_id: california_schools
# question: Name schools in Riverside which the average of average math score for SAT is grater than 400, what is the funding type of these schools?
# evidence: Average of average math = sum(average math scores) / count(schools).
# SQL: SELECT T1.sname, T2.`Charter Funding Type` FROM satscores AS T1 INNER JOIN frpm AS T2 ON T1.cds = T2.CDSCode WHERE T2.`District Name` LIKE 'Riverside%' GROUP BY T1.sname, T2.`Charter Funding Type` HAVING CAST(SUM(T1.AvgScrMath) AS REAL) / COUNT(T1.cds) > 400
# difficulty: moderate
@model(deps=[Satscores, Schools])
def schools_with_avg_math_score_above_400_in_riverside(sa: T, s: T) -> T:
    j = join(sa, s, on=[sa.cds == s.CDSCode])
    j.filter(j.cname == "Riverside")
    j.aggregate(sa.AvgScrMath.mean(), group_by=[s.CDSCode])
    j.filter(j.AvgScrMath_mean > 400)
    j.select(s.School, s.FundingType)
    return j



# question_id: 26
# db_id: california_schools
# question: State the names and full communication address of high schools in Monterey which has more than 800 free or reduced price meals for ages 15-17?
# evidence: Full communication address should include Zip, Street, City, State
# SQL: SELECT T1.`School Name`, T2.Zip, T2.Street, T2.City, T2.State FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Monterey' AND T1.`Free Meal Count (Ages 5-17)` > 800 AND T1.`School Type` = 'High Schools (Public)'
# difficulty: moderate@model(deps=[Frpm, Schools])
def high_schools_communication_address_more_meals(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.filter((j.County_Name == "Monterey") & (j.FRPM_Count__Ages_5_17_ > 800) & (j.High_Grade == "12th grade"))
    return j.select(s.School_Name, s.MailStreet, s.MailCity, s.MailState, s.MailZip)


# question_id: 27
# db_id: california_schools
# question: What is the average score in writing for the schools that were opened after 1991 or closed before 2000? List the school names along with the score. Also, list the communication number of the schools if there is any.
# evidence: Communication number refers to phone number.
# SQL: SELECT T2.School, T1.AvgScrWrite, T2.Phone, strftime('%Y', T2.OpenDate), strftime('%Y', T2.ClosedDate) FROM schools AS T2 LEFT JOIN satscores AS T1 ON T2.CDSCode = T1.cds WHERE strftime('%Y', T2.OpenDate) > '1991' AND strftime('%Y', T2.ClosedDate) < '2000'
# difficulty: moderate
@model(deps=[Schools, Satscores])
def average_writing_score_after_1991_or_closed_before_2000(s: T, sat: T) -> T:
    j = join(s, sat, on=[s.CDSCode == sat.cds])
    j.filter((s.OpenDate > "1991-01-01") | (s.ClosedDate < "2000-01-01"))
    j.select(s.School, sat.AvgScrWrite, s.Phone)
    return j



# question_id: 28
# db_id: california_schools
# question: Consider the average difference between K-12 enrollment and 15-17 enrollment of schools that are locally funded, list the names and DOC type of schools which has a difference above this average.
# evidence: Difference between K-12 enrollment and 15-17 enrollment can be computed by `Enrollment (K-12)` - `Enrollment (Ages 5-17)`
# SQL: SELECT T2.School, T2.DOC FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.FundingType = 'Locally funded' AND (T1.`Enrollment (K-12)` - T1.`Enrollment (Ages 5-17)`) > (SELECT AVG(T3.`Enrollment (K-12)` - T3.`Enrollment (Ages 5-17)`) FROM frpm AS T3 INNER JOIN schools AS T4 ON T3.CDSCode = T4.CDSCode WHERE T4.FundingType = 'Locally funded')
# difficulty: challenging
@model(deps=[Frpm, Schools])
def above_average_enrollment_difference(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.filter(f.FundingType == "Locally funded")
    j.define({"enrollment_difference": j.Enrollment__K_12_ - j.Enrollment__Ages_5_17_})
    avg_diff = j.aggregate(j.enrollment_difference.mean())
    j.filter(j.enrollment_difference > avg_diff)
    return j.select([s.School_Name, f.DOCType])


# question_id: 29
# db_id: california_schools
# question: When did the first-through-twelfth-grade school with the largest enrollment open?
# evidence: K-12 means First-through-twelfth-grade
# SQL: SELECT T2.OpenDate FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T1.`Enrollment (K-12)` DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools])
def k12_school_with_largest_enrollment_open_date(s: T) -> T:
    j = s.filter(s.GSoffered == "K–12").sort(by=-s.Enrollment__K_12_).limit(1)
    return j.select(s.OpenDate)


