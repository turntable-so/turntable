SYSTEM_MESSAGE = "You are an expert data analyst who is proficient in writing python models to help answer questions. These models are always annotated functions using a special python library. You will be given the class names, schemas and evidence to help you and youll need to return a model that answers the query. Only return the code and nothing else in your response"


prompt_1 = """
prompt: What is the ratio between male and female cast members of the movie 'Iron Man?' Count how many have unspecified genders.

class Movie:
    movie_id: t.Int64(nullable=False) = Field(description="the unique identifier of the movie", primary_key=True)
    title: t.String(nullable=True) = Field(description="the title of the movie")
    budget: t.Int64(nullable=True) = Field(description="the budget for the movie. Additional context: If a movie has higher popularity, it means that it is well-liked by a large number of people. This can be determined by looking at the movie's ratings and reviews, as well as the box office performance and overall buzz surrounding the film. Higher popularity often translates to more success for the movie, both financially and critically.")
    homepage: t.String(nullable=True) = Field(description="the homepage of the movie")
    overview: t.String(nullable=True) = Field(description="the overview of the movie")
    popularity: t.Float64(nullable=True) = Field(description="the popularity of the movie. Additional context:  If a movie has higher popularity, it means that it is well-liked by a large number of people. This can be determined by looking at the movie's ratings and reviews, as well as the box office performance and overall buzz surrounding the film. Higher popularity often translates to more success for the movie, both financially and critically.")
    release_date: t.Date(nullable=True) = Field(description="the release date of the movie")
    revenue: t.Int64(nullable=True) = Field(description="the revenue of the movie. Additional context:  A higher vote average indicates that a greater proportion of people who have seen the movie have given it positive ratings.")
    runtime: t.Int64(nullable=True) = Field(description="the runtime of the movie")
    movie_status: t.String(nullable=True) = Field(description="the status of the movie The only value of this column is 'Released'. ")
    tagline: t.String(nullable=True) = Field(description="the tagline of the movie")
    vote_average: t.Float64(nullable=True) = Field(description="the average vote for the movie. Additional context: A higher vote average indicates that a greater proportion of people who have seen the movie have given it positive ratings.")
    vote_count: t.Int64(nullable=True) = Field(description="the vote count for the movie. Additional context:  If a movie has a higher vote average and vote count, it means that it has been well-received by audiences and critics. A higher vote count means that more people have rated the movie, which can indicate a greater level of interest in the film.")

class MovieCast:
    movie_id: t.Int64(nullable=True) = Field(description="the id of the movie Maps to movie(movie_id)", foreign_key=('Movie', 'movie_id'))
    person_id: t.Int64(nullable=True) = Field(description="the id of the person Maps to person(person_id)", foreign_key=('Person', 'person_id'))
    character_name: t.String(nullable=True) = Field(description="the character name")
    gender_id: t.Int64(nullable=True) = Field(description="the id of the cast's gender Maps to gender(gender_id)", foreign_key=('Gender', 'gender_id'))
    cast_order: t.Int64(nullable=True) = Field(description="the cast order of the cast. Additional context:  The cast order of a movie or television show refers to the sequence in which the actors and actresses are listed in the credits. This order is typically determined by the relative importance of each actor's role in the production, with the main actors and actresses appearing first, followed by the supporting cast and extras. ")


class Gender:
    gender_id: t.Int64(nullable=False) = Field(description="the unique identifier of the gender", primary_key=True)
    gender: t.String(nullable=True) = Field(description="the gender. Additional context:  female/ male/ unspecified ")
"""

answer_1 = """
@model(deps=[Movie, MovieCast, Gender])
def query(m: T, c: T, g: t) -> T:
    j = join(m,c, on= [m.movie_id == c.movie_id])
    j2 = join(j, g, on=[m.gender_id == g.gender_id])
    j2.filter(j2.title == "Iron Man")
    j2.aggregate(
        {
            "ratio": j2.count(where=(j2.gender == 'Male'), as_scalar=True) / j2.count(where = (j2.gender == 'Female'), as_scalar=True),
            "ungenders": j2.count(where = (j2.gender == "Unspecified"), as_scalar = True)
        }
    )
    return j2
"""

prompt_2 = """
prompt: What is the title of the movie that has a user_id of 59988436 and critic_comments of 21?
"""
answer_2 = """
@model(deps=[Movies, Ratings])
def query(m: T, r: T) -> T:
    j = join(m, r)
    j.filter((r.user_id == 59988436) & (r.critic_comments == 21))
    j.select(m.movie_title)
    return j
"""

prompt_4 = """
prompt: Calculate the average age of the male patients that have hypertension.

class Conditions:
    START: t.Date(nullable=True) = Field(description="the start date of the allergy . Additional context: mm/dd/yy")
    STOP: t.Date(nullable=True) = Field(description="the stop date of the allergy. Additional context: mm/dd/yy")
    PATIENT: t.String(nullable=True) = Field(description="the patient id", foreign_key=('Patients', 'patient'))
    ENCOUNTER: t.String(nullable=True) = Field(description="the medical encounter id", foreign_key=('Encounters', 'ID'))
    CODE: t.Int64(nullable=True) = Field(description="the code of the condition ")
    DESCRIPTION: t.String(nullable=True) = Field(description="the description of the patient condition", foreign_key=('AllPrevalences', 'ITEM'))

class Patients:
    patient: t.String(nullable=True) = Field(description="the unique id for the patient", primary_key=True)
    birthdate: t.Date(nullable=True) = Field(description="the birth date of the patient")
    deathdate: t.Date(nullable=True) = Field(description="the death date of the patient. Additional context: the age of the patient = death year - birth year if null, it means this patient is still alive")
    ssn: t.String(nullable=True) = Field(description="the social security number of the patient")
    drivers: t.String(nullable=True) = Field(description="the driver number of the patient. Additional context:  if not, this patient doesn't have driving license")
    passport: t.String(nullable=True) = Field(description="the passport number. Additional context:  if not, this patient cannot go abroad, vice versa")
    prefix: t.String(nullable=True) = Field(description="the prefix")
    first: t.String(nullable=True) = Field(description="the first name")
    last: t.String(nullable=True) = Field(description="the last name. Additional context:  full name = first + last")
    suffix: t.String(nullable=True) = Field(description="the suffix of the patient. Additional context:  if suffix = PhD, JD, MD, it means this patient has doctoral degree. Otherwise, this patient is not.")
    maiden: t.String(nullable=True) = Field(description="the maiden name of the patient. Additional context:  Only married women have the maiden name")
    marital: t.String(nullable=True) = Field(description="the marital status of the patient. Additional context: M: married  S: single")
    race: t.String(nullable=True) = Field(description="the race of the patient")
    ethnicity: t.String(nullable=True) = Field(description="the ethnicity of the patient")
    gender: t.String(nullable=True) = Field(description="the gender of the patient")
    birthplace: t.String(nullable=True) = Field(description="the birth place")
    address: t.String(nullable=True) = Field(description="the specific address")
"""

answer_4 = """

@model(deps=[Conditions, Patients])
def query(c: T, p: T) -> T:
    j = join(c, p, how="inner")
    j.define({"adj_deathdate": coalesce(j.deathdate, now().dt.floor(days=1))})
    j.define({"age_in_seconds": j.adj_deathdate.dt.epoch_seconds() - j.birthdate.dt.epoch_seconds()})
    j.define({"age_in_years": j.age_in_seconds / (60 * 60 * 24 * 365)})
    j.aggregate(j.age_in_years.mean(where=(j.DESCRIPTION == "Hypertension") & (j.gender == "M")))

    return j
"""

prompt_5 = """
prompt: How many complaints from customers with a gmail.com email were received by the company in February 2017?',

class Client:
    client_id: t.String(nullable=True) = Field(description="unique id client number", primary_key=True)
    sex: t.String(nullable=True) = Field(description="sex of client")
    day: t.Int64(nullable=True) = Field(description="day of the birthday")
    month: t.Int64(nullable=True) = Field(description="month of the birthday")
    year: t.Int64(nullable=True) = Field(description="year when is born")
    age: t.Int64(nullable=True) = Field(description="age . Additional context: teenager: 13-19 adult: 19-65 elder: > 65")
    social: t.String(nullable=True) = Field(description="social number. Additional context: ssn: us id number for each person")
    first: t.String(nullable=True) = Field(description="first name")
    middle: t.String(nullable=True) = Field(description="middle name")
    last: t.String(nullable=True) = Field(description="last name")
    phone: t.String(nullable=True) = Field(description="phone number")
    email: t.String(nullable=True) = Field(description="email. Additional context: google email / account: @gamil.com microsoft email / account: xxx@outlook.com")
    address_1: t.String(nullable=True) = Field(description="address 1")
    address_2: t.String(nullable=True) = Field(description="address 2. Additional context: entire address = (address_1, address_2)")
    city: t.String(nullable=True) = Field(description="city ")
    state: t.String(nullable=True) = Field(description="state code")
    zipcode: t.Int64(nullable=True) = Field(description="zipcode")
    district_id: t.Int64(nullable=True) = Field(description="district id number", foreign_key=('District', 'district_id'))

class Callcenterlogs:
    Date_received: t.Date(nullable=True) = Field(description="complaint date")
    Complaint_ID: t.String(nullable=True) = Field(description="unique id number representing each complaint", primary_key=True)
    rand_client: t.String(nullable=True) = Field(description="client id", foreign_key=('Client', 'client_id'))
    phonefinal: t.String(nullable=True) = Field(description="final phone number")
    vru_line: t.String(nullable=True) = Field(description="voice response unit line")
    call_id: t.Int64(nullable=True) = Field(description="id number identifying the call")
    priority: t.Int64(nullable=True) = Field(description="priority of the complaint. Additional context: 0, 1, 2, 
    null: not available, higher: -> higher priority, -> more serious/urgent complaint")
    type: t.String(nullable=True) = Field(description="type of complaint")
    outcome: t.String(nullable=True) = Field(description="the outcome of processing of complaints")
    server: t.String(nullable=True) = Field(description="server")
    ser_start: t.String(nullable=True) = Field(description="server start time. Additional context: HH:MM:SS")
    ser_exit: t.String(nullable=True) = Field(description="server exit time")
    ser_time: t.String(nullable=True) = Field(description="server time. Additional context: longer server time referring to more verbose/longer complaint")

"""

answer_5 = """
@model(deps=[Client, Callcenterlogs])
def complaints_from_gmail_in_feb_2017(c: T, l: T) -> T:
    j = join(c, l)
    j.filter(j.Date_received.between("2017-01-02", "2017-02-28"))
    j.filter(j.email.like("%@gmail.com"))
    j.aggregate(j.email.count())

    return j
"""

answer_7 = """
@model(deps=[Method])
def czech_language_task(m: T):
    m.define({"first_period_pos": m.Name.str.find(".")})
    m.define({"second_period_pos": m.Name.str.find(".", m.first_period_pos + 1)})
    m.define({"task": m.Name[(m.first_period_pos + 1) : m.second_period_pos]})
    m.filter(m.Lang == "cs")
    m.select(m.task)
    m.distinct()
    
    return m
"""
