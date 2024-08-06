# What is the highest eligible free rate for K-12 students in the schools in Alameda County?

from vinyl import model, join
from vinyl import T
from dev.sources.california_schools.california_schools.main.satscores import Satscores
from dev.sources.california_schools.california_schools.main.schools import Schools
from dev.sources.california_schools.california_schools.main.frpm import Frpm


# question_id: 0
# db_id: california_schools
# question: What is the highest eligible free rate for K-12 students in the schools in Alameda County?
# evidence: Eligible free rate for K-12 = `Free Meal Count (K-12)` / `Enrollment (K-12)`
# SQL: SELECT `Free Meal Count (K-12)` / `Enrollment (K-12)` FROM frpm WHERE `County Name` = 'Alameda' ORDER BY (CAST(`Free Meal Count (K-12)` AS REAL) / `Enrollment (K-12)`) DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def worst_reading_scores(s: T, ss: T) -> T:
    j = join(s, ss, on=[s.CDSCode == ss.cds])
    j.order_by("AvgScrRead", ascending=True)
    j.limit(5)
    return j


# question_id: 2
# db_id: california_schools
# question: Please list the zip code of all the charter schools in Fresno County Office of Education.
# evidence: Charter schools refers to `Charter School (Y/N)` = 1 in the table fprm
# SQL: SELECT T2.Zip FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T1.`District Name` = 'Fresno County Office of Education' AND T1.`Charter School (Y/N)` = 1
# difficulty: simple
@model(deps=[Frpm, Schools])
def charter_schools_zip_in_fresno(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.filter(
        (f.Charter_School__Y_N_ == 1)
        & (f.District_Name == "Fresno County Office of Education")
    )
    return j.select(s.Zip)


# question_id: 3
# db_id: california_schools
# question: What is the unabbreviated mailing address of the school with the highest FRPM count for K-12 students?
# evidence:
# SQL: SELECT T2.MailStreet FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T1.`FRPM Count (K-12)` DESC LIMIT 1
# difficulty: simple
@model(deps=[Frpm, Schools])
def unabbreviated_mailing_address_of_highest_FRPM_school(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.sort(by=-f.FRPM_Count__K_12_)
    j.select(j.MailStreet)
    j.limit(1)
    return j


# question_id: 4
# db_id: california_schools
# question: Please list the phone numbers of the direct charter-funded schools that are opened after 2000/1/1.
# evidence: Charter schools refers to `Charter School (Y/N)` = 1 in the frpm
# SQL: SELECT T2.Phone FROM frpm AS T1 INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode WHERE T1.`Charter Funding Type` = 'Directly funded' AND T1.`Charter School (Y/N)` = 1 AND T2.OpenDate > '2000-01-01'
# difficulty: moderate
@model(deps=[Frpm, Schools])
def direct_charter_schools_phone_numbers(f: T, s: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j.filter(f.Charter_School__Y_N_ == 1)
    j.filter(s.OpenDate > "2000-01-01")
    j.filter(f.Charter_Funding_Type == "Directly funded")
    j.select(s.Phone)

    return j


# question_id: 5
# db_id: california_schools
# question: How many schools with an average score in Math under 400 in the SAT test are exclusively virtual?
# evidence: Exclusively virtual refers to Virtual = 'F'
# SQL: SELECT COUNT(DISTINCT T2.School) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE T2.Virtual = 'F' AND T1.AvgScrMath < 400
# difficulty: simple
@model(deps=[Schools, Satscores])
def virtual_schools_low_sat_math(s: T, sat: T) -> T:
    j = join(s, sat, on=[s.CDSCode == sat.cds])
    j.filter((j.Virtual == "F") & (j.AvgScrMath < 400))
    j.aggregate(j.CDSCode.count())

    return j


# question_id: 6
# db_id: california_schools
# question: Among the schools with the SAT test takers of over 500, please list the schools that are magnet schools or offer a magnet program.
# evidence: Magnet schools or offer a magnet program means that Magnet = 1
# SQL: SELECT T2.School FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE T2.Magnet = 1 AND T1.NumTstTakr > 500
# difficulty: simple
@model(deps=[Schools, Satscores])
def magnet_schools_with_high_SAT_takers(s: T, sat: T) -> T:
    j = join(s, sat, on=[s.CDSCode == sat.cds])
    j.filter(j.NumTstTakr > 500)
    j.filter(j.Magnet == 1)
    j.select(s.School)
    return j


# question_id: 7
# db_id: california_schools
# question: What is the phone number of the school that has the highest number of test takers with an SAT score of over 1500?
# evidence:
# SQL: SELECT T2.Phone FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode ORDER BY T1.NumGE1500 DESC LIMIT 1
# difficulty: simple
@model(deps=[Schools, Satscores])
def highest_scoring_school_phone(s: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
    j.filter(ss.NumGE1500 > 0)
    j.sort(-ss.NumGE1500)
    result = j.select(s.Phone).limit(1)
    return result


# question_id: 9
# db_id: california_schools
# question: Among the schools with the average score in Math over 560 in the SAT test, how many schools are directly charter-funded?
# evidence:
# SQL: SELECT COUNT(T2.`School Code`) FROM satscores AS T1 INNER JOIN frpm AS T2 ON T1.cds = T2.CDSCode WHERE T1.AvgScrMath > 560 AND T2.`Charter Funding Type` = 'Directly funded'
# difficulty: simple
@model(deps=[Frpm, Schools, Satscores])
def avg_score_oer_560_sat(f: T, s: T, ss: T) -> T:
    j = join(ss, s, on=[ss.cds == s.CDSCode])
    j = join(j, f, on=[j.CDSCode == f.CDSCode])
    j.filter(j.AvgScrMath > 560)
    j.filter(j.Charter_Funding_Type == "Directly funded")
    j.aggregate(j.School_Name.count())

    return j


# question_id: 1
# db_id: california_schools
# question: Please list the lowest three eligible free rates for students aged 5-17 in continuation schools.
# evidence: Eligible free rates for students aged 5-17 = `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)`
# SQL: SELECT `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` FROM frpm WHERE `Educational Option Type` = 'Continuation School' AND `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` IS NOT NULL ORDER BY `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)` ASC LIMIT 3
# difficulty: moderate
@model(deps=[Schools, Frpm])
def lowest_three_eligible_free_rates_continuation_schools(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.filter(s.Educational_Option_Type == "Continuation School")
    j.filter((f.Enrollment__Ages_5_17_ > 0) & (f.Free_Meal_Count__Ages_5_17_ > 0))
    j.define(
        {"eligible_free_rate": f.Free_Meal_Count__Ages_5_17_ / f.Enrollment__Ages_5_17_}
    )
    j.sort(j.eligible_free_rate)
    j.select([j.School, j.eligible_free_rate]).limit(3)

    return j


# question_id: 8
# db_id: california_schools
# question: What is the number of SAT test takers of the schools with the highest FRPM count for K-12 students?
# evidence:
# SQL: SELECT NumTstTakr FROM satscores WHERE cds = ( SELECT CDSCode FROM frpm ORDER BY `FRPM Count (K-12)` DESC LIMIT 1 )
# difficulty: simple
@model(deps=[Schools, Satscores, Frpm])
def highest_frpm_school_sat_takers(s: T, sat: T, f: T) -> T:
    j = join(f, s, on=[f.CDSCode == s.CDSCode])
    j2 = join(j, sat, on=[j.CDSCode == sat.cds])
    j2.aggregate({"highest_frpm_count": j2.FRPM_Count__K_12_.max()})

    return j2


# question_id: 10
# db_id: california_schools
# question: For the school with the highest average score in Reading in the SAT test, what is its FRPM count for students aged 5-17?
# evidence:
# SQL: SELECT T2.`FRPM Count (Ages 5-17)` FROM satscores AS T1 INNER JOIN frpm AS T2 ON T1.cds = T2.CDSCode ORDER BY T1.AvgScrRead DESC LIMIT 1
# difficulty: simple
@model(deps=[Satscores, Frpm])
def highest_reading_school_frpm(sa: T, f: T) -> T:
    j = join(sa, f, on=[f.CDSCode == sa.cds])
    j.sort(-sa.AvgScrRead)
    j.select(f.FRPM_Count__Ages_5_17_)
    j.limit(1)
    return j


# question_id: 11
# db_id: california_schools
# question: Please list the codes of the schools with a total enrollment of over 500.
# evidence: Total enrollment can be represented by `Enrollment (K-12)` + `Enrollment (Ages 5-17)`
# SQL: SELECT T2.CDSCode FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode WHERE T2.`Enrollment (K-12)` + T2.`Enrollment (Ages 5-17)` > 500
# difficulty: simple
@model(deps=[Schools, Frpm])
def schools_with_over_500_enrollment(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.define({"total_enrollment": j.Enrollment__K_12_ + j.Enrollment__Ages_5_17_})
    j.filter(j.total_enrollment > 500)
    return j.select(j.CDSCode)


# question_id: 12
# db_id: california_schools
# question: Among the schools with an SAT excellence rate of over 0.3, what is the highest eligible free rate for students aged 5-17?
# evidence: Excellence rate = NumGE1500 / NumTstTakr; Eligible free rates for students aged 5-17 = `Free Meal Count (Ages 5-17)` / `Enrollment (Ages 5-17)`
# SQL: SELECT MAX(CAST(T1.`Free Meal Count (Ages 5-17)` AS REAL) / T1.`Enrollment (Ages 5-17)`) FROM frpm AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE CAST(T2.NumGE1500 AS REAL) / T2.NumTstTakr > 0.3
# difficulty: moderate
@model(deps=[Schools, Satscores, Frpm])
def highest_eligible_free_rate_for_students_aged_5_17(s: T, sa: T, f: T) -> T:
    j = join(sa, s, on=[sa.cds == s.CDSCode])
    j2 = join(j, f, on=[j.CDSCode == f.CDSCode])
    j2.filter(j2.NumGE1500 / j2.NumTstTakr > 0.3)
    j2.aggregate(
        {
            "highest_eligible_free_rate": j2.Free_Meal_Count__Ages_5_17_
            / j2.Enrollment__Ages_5_17_.max()
        }
    )

    return j2


# question_id: 13
# db_id: california_schools
# question: Please list the phone numbers of the schools with the top 3 SAT excellence rate.
# evidence: Excellence rate = NumGE1500 / NumTstTakr
# SQL: SELECT T1.Phone FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds ORDER BY CAST(T2.NumGE1500 AS REAL) / T2.NumTstTakr DESC LIMIT 3
# difficulty: simple
@model(deps=[Schools, Satscores])
def top_3_sat_excellence_school_phones(s: T, sat: T) -> T:
    j = join(s, sat, on=[s.CDSCode == sat.cds])
    j.define({"excellence_rate": j.NumGE1500 / j.NumTstTakr})
    j.order_by(j.excellence_rate.desc())
    j.limit(3)
    j.select([j.Phone])
    return j


# question_id: 14
# db_id: california_schools
# question: List the top five schools, by descending order, from the highest to the lowest, the most number of Enrollment (Ages 5-17). Please give their NCES school identification number.
# evidence:
# SQL: SELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5
# difficulty: simple
@model(deps=[Schools, Frpm])
def top_five_schools_by_enrollment(s: T, f: T) -> T:
    j = join(s, f, on=[s.CDSCode == f.CDSCode])
    j.aggregate(
        {
            "NCES_school_id": j.NCESSchool,
            "enrollment_ages_5_17": j.Enrollment__Ages_5_17_,
        },
        by=["NCES_school_id"],
        sort="-enrollment_ages_5_17",
        limit=5,
    )
    return j


# question_id: 8
# db_id: california_schools
# question: What is the number of SAT test takers of the schools with the highest FRPM count for K-12 students?
# evidence:
# SQL: SELECT NumTstTakr FROM satscores WHERE cds = ( SELECT CDSCode FROM frpm ORDER BY `FRPM Count (K-12)` DESC LIMIT 1 )
# difficulty: simple
@model(deps=[Satscores])
def highest_frpm_sat_test_takers(f: T, s: T, st: T) -> T:
    max_frpm = f.aggregate({"max_frpm": f.FRPM_Count__K_12_.max()}, as_frame=True)
    s_with_max_frpm = join(f, s, on=[f.CDSCode == s.CDSCode])
    s_with_max_frpm.filter(s_with_max_frpm.FRPM_Count__K_12_ == max_frpm.max_frpm)
    result = join(s_with_max_frpm, st, on=[s.CDSCode == st.cds])
    result.aggregate({"num_sat_test_takers": result.NumTstTakr.sum()})
    return result
