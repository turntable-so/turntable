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
def highest_avg_score_reading_district_active(s: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
    j.filter(s.StatusType == "Active")
    j.aggregate({"highest_avg_read_score": j.AvgScrRead.avg()}, by=j.District)
    j.sort(by=-j.highest_avg_read_score)
    j.select(j.District).limit(1)
    return j



# question_id: 16
# db_id: california_schools
# question: How many schools in merged Alameda have number of test takers less than 100?
# evidence: 
# SQL: SELECT COUNT(T1.CDSCode) FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Merged' AND T2.NumTstTakr < 100 AND T1.County = 'Alameda'
# difficulty: simple
@model(deps=[Schools, Satscores])
def merged_alameda_schools_with_low_test_takers(s: T, ss: T) -> T:
    j = join(s, ss, on=[s.CDSCode == ss.cds])
    j.filter((s.StatusType == "Merged") & (s.County == "Alameda") & (ss.NumTstTakr < 100))
    return j.aggregate(j.CDSCode.count())



# question_id: 17
# db_id: california_schools
# question: What is the charter number of the school that the average score in Writing is 499?
# evidence: 
# SQL: SELECT T1.CharterNum FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T2.AvgScrWrite = 499
# difficulty: simple
@model(deps=[Schools, Satscores])
def charter_number_for_avg_score_499(s: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
    j.filter(ss.AvgScrWrite == 499)
    return j.select(s.CharterNum).limit(1)



# question_id: 18
# db_id: california_schools
# question: How many schools in Contra Costa (directly funded) have number of test takers not more than 250?
# evidence: 
# SQL: SELECT COUNT(T1.CDSCode) FROM frpm AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.`Charter Funding Type` = 'Directly funded' AND T1.`County Name` = 'Contra Costa' AND T2.NumTstTakr <= 250
# difficulty: simple
@model(deps=[Frpm, Schools, Satscores])
def contra_costa_directly_funded_schools_count(f: T, s: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
    j = join(j, f, on=[j.CDSCode == f.CDSCode])
    j.filter((f.Charter_Funding_Type == "Directly funded") & (s.County == "Contra Costa") & (ss.NumTstTakr <= 250))
    return j.aggregate(j.CDSCode.count())



# question_id: 19
# db_id: california_schools
# question: What is the phone number of the school that has the highest average score in Math?
# evidence: 
# SQL: SELECT T1.Phone FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds ORDER BY T2.AvgScrMath DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def highest_avg_score_math_phone(s: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
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
def schools_in_amador_grade_9_to_12(s: T) -> T:
    s.filter((s.County == "Amador") & (s.Low_Grade == "9") & (s.High_Grade == "12"))
    return s.aggregate(s.CDSCode.count())



# question_id: 21
# db_id: california_schools
# question: In Los Angeles how many schools have more than 500 free meals but less than 700 free or reduced price meals for K-12?
# evidence: 
# SQL: SELECT COUNT(CDSCode) FROM frpm WHERE `County Name` = 'Los Angeles' AND `Free Meal Count (K-12)` > 500 AND `Free Meal Count (K-12)` < 700
# difficulty: simple
@model(deps=[Frpm, Schools])
def schools_with_meal_criteria(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.filter((j.County_Name == "Los Angeles") & (j.Free_Meal_Count__K_12_ > 500) & (j.FRPM_Count__K_12_ < 700))
    return j.aggregate(j.School_Name.count())



# question_id: 22
# db_id: california_schools
# question: Which school in Contra Costa has the highest number of test takers?
# evidence: 
# SQL: SELECT sname FROM satscores WHERE cname = 'Contra Costa' AND sname IS NOT NULL ORDER BY NumTstTakr DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def school_highest_test_takers_contra_costa(s: T, sat: T) -> T:
    j = join(s, sat, on=[s.CDSCode == sat.cds])
    j.filter(s.County == "Contra Costa")
    j.sort(-sat.NumTstTakr)
    j.select(s.School).limit(1)
    return j



# question_id: 23
# db_id: california_schools
# question: List the names of schools with more than 30 difference in enrollements between K-12 and ages 5-17? Please also give the full street adress of the schools.
# evidence: Diffrence in enrollement = `Enrollment (K-12)` - `Enrollment (Ages 5-17)`
# SQL: SELECT T1.School, T1.StreetAbr FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.`Enrollment (K-12)` - T2.`Enrollment (Ages 5-17)` > 30
# difficulty: moderate
@model(deps=[Frpm, Schools])
def schools_with_enrollment_difference(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.define({"enrollment_diff": f.Enrollment__K_12_ - f.Enrollment__Ages_5_17_})
    j.filter(j.enrollment_diff.abs() > 30)
    return j.select({"School Name": s.School, "Full Street Address": s.Street})



# question_id: 24
# db_id: california_schools
# question: Give the names of the schools with the percent eligible for free meals in K-12 is more than 0.1 and test takers whose test score is greater than or equal to 1500?
# evidence: 
# SQL: SELECT T2.`School Name` FROM satscores AS T1 INNER JOIN frpm AS T2 ON T1.cds = T2.CDSCode WHERE CAST(T2.`Free Meal Count (K-12)` AS REAL) / T2.`Enrollment (K-12)` > 0.1 AND T1.NumGE1500 > 0
# difficulty: moderate
@model(deps=[Frpm, Satscores, Schools])
def schools_eligible_free_meals_high_scores(f: T, sat: T, s: T) -> T:
    j = join(f, sat, on=[f.CDSCode == sat.cds])
    j = join(j, s, on=[j.CDSCode == s.CDSCode])
    j.filter((j.Percent_____Eligible_Free__K_12_ > 0.1) & (j.NumGE1500 > 0))
    return j.select(s.School)



# question_id: 25
# db_id: california_schools
# question: Name schools in Riverside which the average of average math score for SAT is grater than 400, what is the funding type of these schools?
# evidence: Average of average math = sum(average math scores) / count(schools).
# SQL: SELECT T1.sname, T2.`Charter Funding Type` FROM satscores AS T1 INNER JOIN frpm AS T2 ON T1.cds = T2.CDSCode WHERE T2.`District Name` LIKE 'Riverside%' GROUP BY T1.sname, T2.`Charter Funding Type` HAVING CAST(SUM(T1.AvgScrMath) AS REAL) / COUNT(T1.cds) > 400
# difficulty: moderate
@model(deps=[Schools, Satscores])
def funding_type_of_schools_in_riverside_with_high_math_avg(s: T, ss: T) -> T:
    j = join(s, ss, on=[s.CDSCode == ss.cds])
    j.filter(s.County == "Riverside")
    avg_math_score = j.AvgScrMath.mean()
    j.filter(j.AvgScrMath > 400)
    return j.select(j.School, j.FundingType)



# question_id: 26
# db_id: california_schools
# question: State the names and full communication address of high schools in Monterey which has more than 800 free or reduced price meals for ages 15-17?
# evidence: Full communication address should include Zip, Street, City, State
# SQL: SELECT T1.`School Name`, T2.Zip, T2.Street, T2.City, T2.State FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.County = 'Monterey' AND T1.`Free Meal Count (Ages 5-17)` > 800 AND T1.`School Type` = 'High Schools (Public)'
# difficulty: moderate
@model(deps=[Schools, Frpm])
def high_schools_free_meals_monterey(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.filter((j.County == "Monterey") & (f.FRPM_Count__Ages_5_17_ > 800) & (s.EILCode == "HS"))
    j.select([s.School, s.Street, s.City, s.State, s.Zip])
    return j



# question_id: 27
# db_id: california_schools
# question: What is the average score in writing for the schools that were opened after 1991 or closed before 2000? List the school names along with the score. Also, list the communication number of the schools if there is any.
# evidence: Communication number refers to phone number.
# SQL: SELECT T2.School, T1.AvgScrWrite, T2.Phone, strftime('%Y', T2.OpenDate), strftime('%Y', T2.ClosedDate) FROM schools AS T2 LEFT JOIN satscores AS T1 ON T2.CDSCode = T1.cds WHERE strftime('%Y', T2.OpenDate) > '1991' AND strftime('%Y', T2.ClosedDate) < '2000'
# difficulty: moderate
@model(deps=[Schools, Satscores])
def average_score_writing_opened_or_closed(schools: T, scores: T) -> T:
    joined = join(schools, scores, on=[schools.CDSCode == scores.cds])
    joined.filter((joined.OpenDate > "1991-01-01") | (joined.ClosedDate < "2000-01-01"))
    joined.select([joined.School, joined.AvgScrWrite, joined.Phone])
    return joined



# question_id: 28
# db_id: california_schools
# question: Consider the average difference between K-12 enrollment and 15-17 enrollment of schools that are locally funded, list the names and DOC type of schools which has a difference above this average.
# evidence: Difference between K-12 enrollment and 15-17 enrollment can be computed by `Enrollment (K-12)` - `Enrollment (Ages 5-17)`
# SQL: SELECT T2.School, T2.DOC FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.FundingType = 'Locally funded' AND (T1.`Enrollment (K-12)` - T1.`Enrollment (Ages 5-17)`) > (SELECT AVG(T3.`Enrollment (K-12)` - T3.`Enrollment (Ages 5-17)`) FROM frpm AS T3 INNER JOIN schools AS T4 ON T3.CDSCode = T4.CDSCode WHERE T4.FundingType = 'Locally funded')
# difficulty: challenging
@model(deps=[Frpm, Schools])
def avg_diff_above_avg_local_funded(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.filter(f.Charter_Funding_Type == "Locally funded")
    j.define({"enrollment_diff": f.Enrollment__K_12_ - f.Enrollment__Ages_5_17_})
    avg_diff = j.enrollment_diff.mean()
    j.filter(j.enrollment_diff > avg_diff)
    return j.select([j.School_Name, j.DOCType])



# question_id: 29
# db_id: california_schools
# question: When did the first-through-twelfth-grade school with the largest enrollment open?
# evidence: K-12 means First-through-twelfth-grade
# SQL: SELECT T2.OpenDate FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T1.`Enrollment (K-12)` DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Frpm])
def school_with_largest_k12_opening(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.sort(by=-f.Enrollment__K_12_)
    j.select(s.OpenDate)
    j.limit(1)
    return j


