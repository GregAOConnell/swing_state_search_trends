library(rvest)
library(httr)
library(dplyr)
library(lubridate)
library(gtrendsR)# Install and load gtrendsR package


# Define search term and swing states
search_terms <- c("migrant crime", "Project 2025", "transgender", "tariff", "abortion")
swing_states <- c("US-WI", "US-MI", "US-PA", "US-NV", "US-AZ", "US-NC", "US-GA")
time_range <- "today 3-m" # Last 5 years

# Initialize list to store results
results_list <- list()


# Retrieve Google Trends data for each state
for (state in swing_states) {
 
  trend_data <- tryCatch({
    gtrends(keyword = search_terms, geo = state, time = time_range, low_search_volume = T)
  }, error = function(e) {
    NULL
  })
  if (!is.null(trend_data)) {
    results_list[[state]] <- trend_data$interest_over_time
  }
Sys.sleep(70)
print(1)
  
}

# Combine results into one data frame
all_data <- do.call(rbind, results_list)

# Ensure state information is included
all_data$state <- rep(swing_states, sapply(results_list, nrow))

# Fetch US-wide Google Trends data
us_trends <- tryCatch({
  gtrends(keyword = search_terms, geo = "US", time = time_range, low_search_volume = TRUE)
}, error = function(e) {
  NULL
})

# Extract the "interest over time" component
if (!is.null(us_trends)) {
  us_trends_data <- us_trends$interest_over_time
} else {
  stop("Failed to fetch US trends data.")
}




# Save data to a CSV for further analysis
write.csv(all_data, "trends_swing_states.csv", row.names = FALSE)


# Save the US trends to a CSV file
write.csv(us_trends_data, "us_search_trends.csv", row.names = FALSE)

# Display the first few rows of the data
print(head(all_data))



# Ensure both datasets have the same type for the `hits` column
us_trends <- us_trends %>%
  mutate(hits = as.numeric(hits))%>%
  replace_na(list(hits = 0))# Convert `hits` column to numeric

# Combine the datasets
combined_trends <- bind_rows(swing_state_trends, us_trends)

# Write the combined dataset to a new CSV file
write_csv(combined_trends, "combined_search_trends.csv")

cat("Combined dataset saved to 'combined_search_trends.csv'")
