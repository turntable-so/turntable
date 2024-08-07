import os

import ibis

from vinyl.lib.table import VinylTable


def _return_vinyl_table(cls):
    def wrapper(*args, **kwargs) -> VinylTable:
        adj_path_base = os.path.dirname(os.path.dirname(__file__))
        return VinylTable(
            ibis.read_parquet(
                os.path.join(adj_path_base, cls.path), table_name=cls.__name__
            )._arg
        )

    wrapper.description = cls.description
    wrapper.references = cls.references

    return wrapper


class ExampleDataset:
    description: str
    references: list[str] | None
    path: str


@_return_vinyl_table
class airports(ExampleDataset):
    description = """This dataset lists US airports, including airport code, city, state, latitude, and longitude. This dataset is a subset of the data compiled and published at http://ourairports.com/data/, and is in the public domain."""
    references = None
    path = "vinyl/data/airports.parquet"


@_return_vinyl_table
class anscombe(ExampleDataset):
    description = """Anscombe's Quartet is a famous dataset constructed by Francis Anscombe [1]_. Common summary statistics are identical for each subset of the data, despite the subsets having vastly different characteristics."""
    references = [
        "Anscombe, F. J. (1973). 'Graphs in Statistical Analysis'. American Statistician. 27 (1): 17-21. JSTOR 2682899."
    ]
    path = "vinyl/data/anscombe.parquet"


@_return_vinyl_table
class barley(ExampleDataset):
    description = """This dataset contains crop yields over different regions and different years in the 1930s. It was originally published by Immer in 1934 [1]_, and was popularized by Fisher (1947) [2]_ and Cleveland (1993) [3]_."""
    references = [
        "Immer, F.R., Hayes, H.D. and LeRoy Powers (1934) Statistical determination of barley varietal adaptation. Journal of the American Society for Agronomy 26, 403-419.",
        "Fisher, R.A. (1947) The Design of Experiments. 4th edition. Edinburgh: Oliver and Boyd.",
        "Cleveland, WS (1993) Visualizing data. Hobart Press",
    ]
    path = "vinyl/data/barley.parquet"


@_return_vinyl_table
class birdstrikes(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/birdstrikes.parquet"


@_return_vinyl_table
class budget(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/budget.parquet"


@_return_vinyl_table
class budgets(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/budgets.parquet"


@_return_vinyl_table
class burtin(ExampleDataset):
    description = """This is a famous dataset gathered by Will Burtin to explore the effectiveness of various antibiotics in treating a variety of bacterial infections. The data was first published in 1951; this dataset comes from https://github.com/mbostock/protovis, and is published there under a BSD license."""
    references = None
    path = "vinyl/data/burtin.parquet"


@_return_vinyl_table
class cars(ExampleDataset):
    description = """Acceleration, horsepower, fuel efficiency, weight, and other characteristics of different makes and models of cars. This dataset was originally published by Donoho et al (1982) [1]_, and was made public at http://lib.stat.cmu.edu/datasets/"""
    references = [
        "Donoho, David and Ramos, Ernesto (1982), ``PRIMDATA:  Data Sets for Use With PRIM-H'' (DRAFT)."
    ]
    path = "vinyl/data/cars.parquet"


@_return_vinyl_table
class climate(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/climate.parquet"


@_return_vinyl_table
class co2_concentration(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/co2_concentration.parquet"


@_return_vinyl_table
class countries(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/countries.parquet"


@_return_vinyl_table
class crimea(ExampleDataset):
    description = """This is a dataset containing monthly casualty counts from the Crimean war. It was originally published in 1858 by Florence Nightingale [1]_ in connection with her famous 'Coxcomb' charts."""
    references = [
        "Nightingale, F. (1858) 'Notes on Matters Affecting the Health, Efficiency and Hospital Administration of the British Army'. RCIN 1075240"
    ]
    path = "vinyl/data/crimea.parquet"


@_return_vinyl_table
class disasters(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/disasters.parquet"


@_return_vinyl_table
class driving(ExampleDataset):
    description = """This dataset tracks miles driven per capita along with gas prices annually from 1956 to 2010. It is based on the May 2, 2010 New York Times article 'Driving Shifts Into Reverse'. See http://mbostock.github.io/protovis/ex/driving.html."""
    references = [
        "Fairfield, Hannah. 'Driving Shifts Into Reverse.' New York Times, May 2, 2010"
    ]
    path = "vinyl/data/driving.parquet"


@_return_vinyl_table
class flare(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flare.parquet"


@_return_vinyl_table
class flare_dependencies(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flare_dependencies.parquet"


@_return_vinyl_table
class flights_10k(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_10k.parquet"


@_return_vinyl_table
class flights_200k(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_200k.parquet"


@_return_vinyl_table
class flights_20k(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_20k.parquet"


@_return_vinyl_table
class flights_2k(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_2k.parquet"


@_return_vinyl_table
class flights_3m(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_3m.parquet"


@_return_vinyl_table
class flights_5k(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_5k.parquet"


@_return_vinyl_table
class flights_airport(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/flights_airport.parquet"


@_return_vinyl_table
class gapminder(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/gapminder.parquet"


@_return_vinyl_table
class gapminder_health_income(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/gapminder_health_income.parquet"


@_return_vinyl_table
class github(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/github.parquet"


@_return_vinyl_table
class income(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/income.parquet"


@_return_vinyl_table
class iowa_electricity(ExampleDataset):
    description = """The state of Iowa has dramatically increased its production of renewable wind power in recent years. This file contains the annual net generation of electricity in the state by source in thousand megawatthours. The dataset was published in the public domain by the U.S. Energy Information Administration [1]_ and downloaded on May 6, 2018. It is useful for illustrating stacked area charts."""
    references = [
        "https://www.eia.gov/beta/electricity/data/browser/#/topic/0?agg=2,0,1&fuel=vvg&geo=00000g&sec=g&linechart=ELEC.GEN.OTH-IA-99.A~ELEC.GEN.COW-IA-99.A~ELEC.GEN.PEL-IA-99.A~ELEC.GEN.PC-IA-99.A~ELEC.GEN.NG-IA-99.A~~ELEC.GEN.NUC-IA-99.A~ELEC.GEN.HYC-IA-99.A~ELEC.GEN.AOR-IA-99.A~ELEC.GEN.HPS-IA-99.A~&columnchart=ELEC.GEN.ALL-IA-99.A&map=ELEC.GEN.ALL-IA-99.A&freq=A&start=2001&end=2017&ctype=linechart&ltype=pin&tab=overview&maptype=0&rse=0&pin="
    ]
    path = "vinyl/data/iowa_electricity.parquet"


@_return_vinyl_table
class iris(ExampleDataset):
    description = """This classic dataset contains lengths and widths of petals and sepals for 150 iris flowers, drawn from three species. It was introduced by R.A. Fisher in 1936 [1]_."""
    references = [
        "R. A. Fisher (1936). 'The use of multiple measurements in taxonomic problems'. Annals of Eugenics. 7 (2): 179-188."
    ]
    path = "vinyl/data/iris.parquet"


@_return_vinyl_table
class jobs(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/jobs.parquet"


@_return_vinyl_table
class la_riots(ExampleDataset):
    description = """More than 60 people lost their lives amid the looting and fires that ravaged Los Angeles for five days starting on April 29, 1992. This dataset contains metadata about each person, including the geographic coordinates of their death. It was compiled and published by the Los Angeles Times Data Desk [1]_."""
    references = ["http://spreadsheets.latimes.com/la-riots-deaths/"]
    path = "vinyl/data/la_riots.parquet"


@_return_vinyl_table
class londonCentroids(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/londonCentroids.parquet"


@_return_vinyl_table
class lookup_groups(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/lookup_groups.parquet"


@_return_vinyl_table
class lookup_people(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/lookup_people.parquet"


@_return_vinyl_table
class monarchs(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/monarchs.parquet"


@_return_vinyl_table
class normal_2d(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/normal_2d.parquet"


@_return_vinyl_table
class obesity(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/obesity.parquet"


@_return_vinyl_table
class ohlc(ExampleDataset):
    description = """This dataset contains the performance of the Chicago Board Options Exchange `Volatility Index <https://en.wikipedia.org/wiki/VIX>`_ in the summer of 2009."""
    references = None
    path = "vinyl/data/ohlc.parquet"


@_return_vinyl_table
class points(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/points.parquet"


@_return_vinyl_table
class population(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/population.parquet"


@_return_vinyl_table
class population_engineers_hurricanes(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/population_engineers_hurricanes.parquet"


@_return_vinyl_table
class seattle_temps(ExampleDataset):
    description = """This dataset contains hourly temperatures in Seattle during the full year of 2010. The dataset is drawn from public-domain `NOAA data <https://www.weather.gov/disclaimer>`_, and transformed using scripts available at http://github.com/vega/vega_datasets/."""
    references = None
    path = "vinyl/data/seattle_temps.parquet"


@_return_vinyl_table
class seattle_weather(ExampleDataset):
    description = """This dataset contains precipitation totals, temperature extremes, wind speed, and weather type recorded daily in Seattle from 2012 to 2015. The dataset is drawn from public-domain `NOAA data <https://www.weather.gov/disclaimer>`_, and transformed using scripts available at http://github.com/vega/vega_datasets/."""
    references = None
    path = "vinyl/data/seattle_weather.parquet"


@_return_vinyl_table
class sf_temps(ExampleDataset):
    description = """This dataset contains hourly temperatures in San Francisco during the full year of 2010. The dataset is drawn from public-domain `NOAA data <https://www.weather.gov/disclaimer>`_, and transformed using scripts available at http://github.com/vega/vega_datasets/."""
    references = None
    path = "vinyl/data/sf_temps.parquet"


@_return_vinyl_table
class sp500(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/sp500.parquet"


@_return_vinyl_table
class stocks(ExampleDataset):
    description = """Daily closing stock prices for AAPL, AMZN, GOOG, IBM, and MSFT between 2000 and 2010."""
    references = None
    path = "vinyl/data/stocks.parquet"


@_return_vinyl_table
class udistrict(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/udistrict.parquet"


@_return_vinyl_table
class unemployment(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/unemployment.parquet"


@_return_vinyl_table
class unemployment_across_industries(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/unemployment_across_industries.parquet"


@_return_vinyl_table
class uniform_2d(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/uniform_2d.parquet"


@_return_vinyl_table
class us_employment(ExampleDataset):
    description = """In the mid 2000s the global economy was hit by a crippling recession. One result: Massive job losses across the United States. The downturn in employment, and the slow recovery in hiring that followed, was tracked each month by the Current Employment Statistics [1]_ program at the U.S. Bureau of Labor Statistics. This file contains the monthly employment total in a variety of job categories from January 2006 through December 2015. The numbers are seasonally adjusted and reported in thousands. The data were downloaded on Nov. 11, 2018, and reformatted for use in this library. Because it was initially published by the U.S. government, it is in the public domain. Totals are included for the 22 'supersectors' [2]_ tracked by the BLS. The 'nonfarm' total is the category typically used by economists and journalists as a stand-in for the country's employment total. A calculated 'nonfarm_change' column has been appended with the month-to-month change in that supersector's employment. It is useful for illustrating how to make bar charts that report both negative and positive values."""
    references = [
        "https://www.bls.gov/ces/",
        "https://download.bls.gov/pub/time.series/ce/ce.supersector",
    ]
    path = "vinyl/data/us_employment.parquet"


@_return_vinyl_table
class us_state_capitals(ExampleDataset):
    description = """US state capitals with latitude and longitude."""
    references = None
    path = "vinyl/data/us_state_capitals.parquet"


@_return_vinyl_table
class volcano(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/volcano.parquet"


@_return_vinyl_table
class weather(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/weather.parquet"


@_return_vinyl_table
class weball26(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/weball26.parquet"


@_return_vinyl_table
class wheat(ExampleDataset):
    description = """In an 1822 letter to Parliament, William Playfair[1]_, a Scottish engineer who is often credited as the founder of statistical graphics, published an elegant chart on the price of wheat[2]_. It plots 250 years of prices alongside weekly wages and the reigning monarch. He intended to demonstrate that 'never at any former period was wheat so cheap, in proportion to mechanical labour, as it is at the present time.' The electronic dataset was created by Mike Bostock and released into the public domain."""
    references = [
        "https://en.wikipedia.org/wiki/William_Playfair",
        "http://dh101.humanities.ucla.edu/wp-content/uploads/2014/08/Vis_2.jpg",
    ]
    path = "vinyl/data/wheat.parquet"


@_return_vinyl_table
class windvectors(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/windvectors.parquet"


@_return_vinyl_table
class zipcodes(ExampleDataset):
    description = """None"""
    references = None
    path = "vinyl/data/zipcodes.parquet"
