#!/bin/bash

containers=(
  computers_category_filter_0 computers_category_filter_1 computers_category_filter_2 computers_category_filter_3
  2000s_published_year_filter_0 2000s_published_year_filter_1 2000s_published_year_filter_2 2000s_published_year_filter_3
  title_contains_filter_0 title_contains_filter_1 title_contains_filter_2 title_contains_filter_3
  decades_accumulator_0 decades_accumulator_1 decades_accumulator_2 decades_accumulator_3
  1990s_published_year_filter_0 1990s_published_year_filter_1 1990s_published_year_filter_2 1990s_published_year_filter_3
  reviews_counter_0 reviews_counter_1 reviews_counter_2 reviews_counter_3
  fiction_category_filter_0 fiction_category_filter_1 fiction_category_filter_2 fiction_category_filter_3
  sentiment_analyzer_0 sentiment_analyzer_1 sentiment_analyzer_2 sentiment_analyzer_3
  avg_rating_accumulator sentiment_score_accumulator
)

random_sleep() {
  local x=$1
  local y=$2
  local interval=$((RANDOM % (y - x + 1) + x))
  echo $interval
}

random_container() {
  local index=$((RANDOM % ${#containers[@]}))
  echo ${containers[$index]}
}

while true; do
  sleep_time=$(random_sleep 3 7) 
  sleep $sleep_time
  
  container=$(random_container)
  echo "Killing container: $container"
  docker kill $container
done
