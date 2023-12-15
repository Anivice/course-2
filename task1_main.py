#!/usr/bin/env python

import task1_header as coronavirus_uk_api
import pandas as pd
# import json  # FIXME: delete me later

structure = {
    "date":                 "date",
    "areaName":             "areaName",
    "daily_cases":          "newCasesByPublishDate",
    "cumulative_cases":     "cumCasesByPublishDate",

    # FIXME: the following two entries are always empty
    "daily_deaths":         "newDeathsByPublishDate",
    "cumulative_deaths":    "cumDeathsByPublishDate",

    "cumulative_vaccinated": "cumPeopleVaccinatedCompleteByVaccinationDate",
    "vaccination_age":      "vaccinationsAgeDemographics",
}

# TASK 2:
results_json_national = coronavirus_uk_api.get_API_data("areaType=nation", structure)
results_json_regional = coronavirus_uk_api.get_API_data("areaType=region", structure)

# Extracting the data lists from the responses
national_data_list = results_json_national.get('data', [])
regional_data_list = results_json_regional.get('data', [])

# TASK 3:
# Concatenating the data lists
combined_data = national_data_list + regional_data_list

# #######################################################################################################################
# # FIXME: DEBUG CODE
# # Open the file for reading
# file_name = "my_list.json"
#
# with open(file_name, "r") as file:
#     # Load JSON data from the file and parse it into a Python dictionary
#     combined_data = json.load(file)
# #######################################################################################################################

# TASK 4:
covid_data = pd.DataFrame(combined_data)

# TASK 5:
# Remove rows where the 'areaName' column is 'England'
covid_data = covid_data[covid_data['areaName'] != 'England']

# TASK 6:
# Rename the 'areaName' column to 'area'
covid_data.rename(columns={'areaName': 'area'}, inplace=True)

# ###########################################################################
# FIXME: DEBUG CODE
# # Set display options to show all rows and columns
# pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", 70)
# pd.set_option("display.width", 1000)
# #############################################################################

# task 7:
# Convert the 'Date' column to datetime type
covid_data['date'] = pd.to_datetime(covid_data['date'])

# task 8:
# Print a general summary of the DataFrame
print("DataFrame Summary:\n")
print(covid_data.info())

# Calculate and print the amount of missing data for each column
print("\nMissing Data Summary:")
for column in covid_data.columns:
    # Count of missing (null) values
    missing_count = covid_data[column].isnull().sum()

    # Percentage of missing values
    missing_percentage = (missing_count / len(covid_data)) * 100

    print(f"{column}: Missing Count = {missing_count}, Missing Percentage = {missing_percentage:.2f}%")


# task 9:
# Assuming covid_data is your DataFrame
def fill_missing_with_recent(group):
    # Sort the group by date
    group = group.sort_values(by='date', ascending=False)

    # Fill missing values with the next valid observation
    group[cumulative_columns] = group[cumulative_columns].bfill()

    return group


# List of columns to apply the function to
cumulative_columns = ['cumulative_deaths', 'cumulative_cases', 'cumulative_vaccinated']

# Group the data by 'area', apply the custom function, and then recombine the groups
covid_data = covid_data.groupby('area').apply(fill_missing_with_recent)

# Reset the index if it becomes multi-level after grouping
covid_data.reset_index(drop=True, inplace=True)


# task 10:
# FIXME: this action is going to erase all the data since there is no record in cumulative_deaths
# FIXME: !! cumulative_columns_bugged should be the same as cumulative_columns but it will erase all the data,
#  so 'cumulative_deaths' is excluded !!
cumulative_columns_bugged = ['cumulative_cases', 'cumulative_vaccinated']
# Drop rows where any of the specified columns have missing values
covid_data = covid_data.dropna(subset=cumulative_columns_bugged)
covid_data.reset_index(drop=True, inplace=True)

# task 11:
# Sort the DataFrame by 'area' and 'date' to ensure correct order for rolling calculations
covid_data.sort_values(by=['area', 'date'], inplace=True)

# Calculate the 7-day rolling average for each area
covid_data['daily_cases_roll_avg'] = (covid_data.groupby('area')['daily_cases']
                                      .rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
                                      )
covid_data['daily_deaths_roll_avg'] = (covid_data.groupby('area')['daily_deaths']
                                       .rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
                                       )

# TASK 12:
# Drop the 'daily_deaths' and 'daily_cases' columns
covid_data = covid_data.drop(columns=['daily_deaths', 'daily_cases'])

# task 13:
# Create the new DataFrame
covid_data_vaccinations = covid_data[['date', 'area', 'vaccination_age']].copy()

# Expand the 'vaccination_age' column
covid_data_vaccinations = covid_data_vaccinations.join(pd.DataFrame(covid_data_vaccinations['vaccination_age'].tolist()))

# Drop the 'vaccination_age' column from the original DataFrame
covid_data = covid_data.drop('vaccination_age', axis=1)

# task 14:
expanded_data = []

# Iterate through each row in the DataFrame
for index, row in covid_data_vaccinations.iterrows():
    base_data = {
        'date': row['date'],
        'area': row['area']
    }

    for age_data in row['vaccination_age']:
        # Combine the base data with the age-specific data
        combined_data = {**base_data, **age_data}
        expanded_data.append(combined_data)

# Create a new DataFrame from the expanded data
covid_data_vaccinations_wide = pd.DataFrame(expanded_data)

# Define the mapping for renaming columns
column_mapping = {
    'age': 'age',
    'VaccineRegisterPopulationByVaccinationDate': 'VaccineRegisterPopulationByVaccinationDate',
    'cumPeopleVaccinatedCompleteByVaccinationDate': 'cumPeopleVaccinatedCompleteByVaccinationDate',
    'newPeopleVaccinatedCompleteByVaccinationDate': 'newPeopleVaccinatedCompleteByVaccinationDate',
    'cumPeopleVaccinatedFirstDoseByVaccinationDate': 'cumPeopleVaccinatedFirstDoseByVaccinationDate',
    'newPeopleVaccinatedFirstDoseByVaccinationDate': 'newPeopleVaccinatedFirstDoseByVaccinationDate',
    'cumPeopleVaccinatedSecondDoseByVaccinationDate': 'cumPeopleVaccinatedSecondDoseByVaccinationDate',
    'newPeopleVaccinatedSecondDoseByVaccinationDate': 'newPeopleVaccinatedSecondDoseByVaccinationDate',
    'cumVaccinationFirstDoseUptakeByVaccinationDatePercentage':
        'cumVaccinationFirstDoseUptakeByVaccinationDatePercentage',
    'cumVaccinationCompleteCoverageByVaccinationDatePercentage':
        'cumVaccinationCompleteCoverageByVaccinationDatePercentage',
    'cumVaccinationSecondDoseUptakeByVaccinationDatePercentage':
        'cumVaccinationSecondDoseUptakeByVaccinationDatePercentage'
}

covid_data_vaccinations_wide.rename(columns=column_mapping, inplace=True)

# TODO: This script is not completed. it contains a lot of debug code and not yet fully tested. BUGs I found are marked
# TODO: in FIXME section.
