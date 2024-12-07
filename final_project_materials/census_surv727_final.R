# Load the libraries
library(tidycensus)
library(tidyverse)

censuskey=read_file("censuskey.txt")

# Set your Census API Key (replace with your key)
census_api_key(censuskey, overwrite = TRUE, install=T)

# Define state groups
blue_wall <- c("Wisconsin", "Michigan", "Pennsylvania")
south <- c("North Carolina", "Georgia")
sunbelt <- c("Nevada", "Arizona")
all_states <- c(blue_wall, south, sunbelt)


# Specify the variables you want to analyze 
# Variables for education
variables <- c(
  median_age = "B01002_001",
  total_population = "B01003_001",
  median_income = "B19013_001",
  total_pop_25_plus = "B15003_001",  # Total population 25 and older
  bachelors_degree = "B15003_022",  # Bachelor's degree
  masters_degree = "B15003_023",    # Master's degree
  professional_degree = "B15003_024", # Professional degree
  doctorate_degree = "B15003_025",   # Doctorate degree
  race_white = "B02001_002",
  race_black = "B02001_003",
  race_hispanic = "B03003_003"
)


# Fetch data
demographics <- get_acs(
  geography = "state",
  variables = variables,
  state = all_states,
  year = 2022, # Adjust the year if needed
  survey = "acs5"
)



# Transform data into wide format
wide_demographics <- demographics %>%
  pivot_wider(
    names_from = variable,
    values_from = estimate
  ) %>%
  group_by(NAME) %>%
  summarize(
    # Aggregate only numeric columns
    across(where(is.numeric), ~ sum(.x, na.rm = TRUE)),
    .groups = "drop"  # Ungroup after summarizing
  )



# Add region groups
wide_demographics <- wide_demographics %>%
  mutate(region = case_when(
    NAME %in% blue_wall ~ "Blue Wall",
    NAME %in% south ~ "South",
    NAME %in% sunbelt ~ "Sunbelt"
  ))

percent_demo=wide_demographics%>%
  mutate(
    percent_white = (race_white / total_population) * 100,
    percent_black = (race_black / total_population) * 100,
    percent_hispanic = (race_hispanic / total_population) * 100,
    percent_bachelors_or_higher = (
      (bachelors_degree + masters_degree + professional_degree + doctorate_degree) / 
        total_pop_25_plus
    ) * 100
  )

# Summarize by region
regional_summary <- percent_demo %>%
  group_by(region) %>%
  summarize(
    median_age = mean(median_age, na.rm = TRUE),
    median_income = mean(median_income, na.rm = TRUE),
    percent_white = mean(percent_white, na.rm = TRUE),
    percent_black = mean(percent_black, na.rm = TRUE),
    percent_hispanic = mean(percent_hispanic, na.rm = TRUE),
    percent_bachelors_or_higher = mean(percent_bachelors_or_higher, na.rm = TRUE)
  )



# Example: Median income by region
ggplot(state_demographics %>% filter(variable == "median_income"), aes(x = region, y = estimate)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  labs(title = "Median Income by Region", x = "Region", y = "Median Income") +
  theme_minimal()
