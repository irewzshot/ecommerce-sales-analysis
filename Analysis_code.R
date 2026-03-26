install.packages("tidyverse")
install.packages("ggplot2")
install.packages("janitor")
library(tidyverse)
library(ggplot2)
library(janitor)
library(lubridate)

online_retail <- read_csv("~/online_retail_II.csv")

head(online_retail)
str(online_retail)
online_retail %>% 
  head(100) %>% 
  View()
summary(online_retail)

online_retail %>% 
  filter(Price < 0) %>% 
  select(Invoice, Description, 'Price', `Customer ID`,) %>% 
  View()

online_retail_clean <- online_retail %>% 
  filter(Description != "Adjust bad debt", Quantity > 0) %>% 
  drop_na('Customer ID') %>% 
  distinct()

print(online_retail_clean)

online_retail_clean <- online_retail_clean %>% 
  mutate(online_retail_clean, Revenue = Quantity * Price)

online_retail_clean %>% 
  head(100) %>% 
  View()

str(online_retail_clean)

monthly_revenue <- online_retail_clean %>% 
  mutate(Month = month(InvoiceDate, label = TRUE, abbr = FALSE)) %>% 
  group_by(Month) %>% 
  summarise(Total_revenue = sum(Revenue, na.rm = TRUE)) %>% 
  arrange(Month)

print(monthly_revenue)

top_10_items <- online_retail_clean %>%
  group_by(Description) %>% 
  summarise(Total_Revenue = sum(Revenue, na.rm = TRUE)) %>% 
  arrange(desc(Total_Revenue)) %>% 
  slice_max(Total_Revenue, n = 10)

print(top_10_items)

top_10_countries <- online_retail_clean %>%
  group_by(Country) %>% 
  summarise(Total_Revenue = sum(Revenue, na.rm = TRUE)) %>% 
  arrange(desc(Total_Revenue)) %>% 
  slice_max(Total_Revenue, n = 10)

print(top_10_countries)

rfm_table <- online_retail_clean %>%
  mutate(InvoiceDate = as.Date(InvoiceDate, format = "%m/%d/%Y")) %>%
  filter(!is.na(`Customer ID`), Price > 0) %>% # Clean data
  group_by(`Customer ID`) %>%
  summarise(
    Recency = as.numeric(as.Date("2012-01-01") - max(InvoiceDate)), # Adjust date to your data's end
    Frequency = n_distinct(Invoice),
    Monetary = sum(Revenue, na.rm = TRUE)
  )

rfm_scores <- rfm_table %>%
  mutate(
    R_Score = ntile(desc(Recency), 5), # desc() because lower recency = better score
    F_Score = ntile(Frequency, 5),
    M_Score = ntile(Monetary, 5),
    RFM_Combined = R_Score + F_Score + M_Score
  )

rfm_segments <- rfm_scores %>%
  mutate(Segment = case_when(
    R_Score >= 4 & F_Score >= 4 & M_Score >= 4 ~ "VIP",
    F_Score >= 4 ~ "Loyal",
    R_Score <= 2 ~ "At Risk",
    TRUE ~ "Others"
  ))

# View results
rfm_segments_results <- rfm_segments %>% 
  group_by(Segment) %>% 
  summarise(Count = n(), Avg_Monetary = mean(Monetary))

kpi_summary <- online_retail_clean %>% 
  summarise(
    Total_Revenue = sum(Revenue, na.rm = TRUE),
    Total_Invoices = n_distinct(Invoice),
    Total_Customers = n_distinct(`Customer ID`),
    AOV = Total_Revenue / Total_Invoices  # This is your KPI
  )

rfm_table <- rfm_table %>% 
  arrange(desc(Monetary))

write_csv(kpi_summary, "kpi_summary.csv")
write_csv(monthly_revenue, "monthly_revenue.csv")
write_csv(online_retail_clean, "online_retail_clean.csv")
write_csv(rfm_scores, "rfm_scores.csv")
write_csv(rfm_segments, "rfm_segments.csv")
write_csv(rfm_segments_results, "rfm_segments_results.csv")
write_csv(rfm_table, "rfm_table.csv")
write_csv(top_10_countries, "top_10_countries.csv")
write_csv(top_10_items, "top_10_items.csv")






















