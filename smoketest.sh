#!/bin/bash

# Define the base URL for the Meal Max API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

##############################
#
#  Health checks
#
##############################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##############################
#
#  Kitchen model checks
#
##############################

#Function to clear the meals from the kitchen
clear_meals() {
  echo "Clearing meals from the kitchen..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals cleared successfully."
  else
    echo "Failed to clear meals."
    exit 1
  fi
}

# Function to create a new meal
create_meal() {
  name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal: $name ($cuisine, $price, $difficulty)..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$name\", \"cuisine\": \"$cuisine\", \"price\": $price, \"difficulty\": \"$difficulty\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal created successfully: $name."
  else
    echo "Failed to create meal: $name."
    exit 1
  fi
}

# Function to delete a meal by ID
delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

# Function to get a meal by ID
get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
    echo "Meal retrieved successfully by ID ($meal_id)."
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

# Function to get a meal by name
get_meal_by_name() {
  name=$1

  echo "Getting meal by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$name")
  if echo "$response" | grep -q '"status": "success"'; then
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name $name):"
      echo "$response" | jq .
    fi
    echo "Meal retrieved successfully by name ($name)."
  else
    echo "Failed to get meal by name ($name)."
    exit 1
  fi
}

#Function to update meal stats
update_meal_stats(){
  meal_id=$1
  result=$2

  echo "Updating meal stats of ID: $meal_id ($result)..."
  curl -s -X POST "$BASE_URL/update-meal-stats"  | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Updated ID $meal_id stats successfully: $result."
  else
    echo "Failed to update meal stats for ID $meal_id."
    exit 1
  fi
 
}

# Function to get the leaderboard
get_leaderboard() {
  sort=$1
  echo "Getting leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/get-leaderboard" -H "Content-Type: application/json" \
    -d "{\"sort\": \"$sort\"}")
  echo $response
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully: $response."
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}

##############################
#
#  Battle model / Random Utils checks
#
##############################


#Function to start a battle
battle() {
  echo "Starting battle..."
  response=$(curl -s -X Get "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Winner of battle: $response."
  else
    echo "Failed to start battle."
    exit 1
  fi

}

#Function to clear the combatants list
clear_combatants() {
  echo "Clearing combatants from the battle..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants list cleared successfully."
  else
    echo "Failed to clear combatants list."
    exit 1
  fi
}

#Function to get the battle score of a combatant
get_battle_score() {
  meal=$1
  
  echo "$meal"
  echo "Getting battle score of $meal..."

  response=$(curl -s -X GET "$BASE_URL/get-battle-score/$meal")

   echo "$response"
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle score of $meal retrieved successfully: $response."
  else
    echo "Failed to retrieve battle score of $meal."
    exit 1
  fi
}

#Function to get the combatants list
get_combatants() {
    echo "Getting combatants list..."
  response=$(curl -s -X Get "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants list retrieved successfully: $response."
  else
    echo "Failed to retrieve combatants list."
    exit 1
  fi

}

#Function to prep a combatant for battle
prep_combatant() {
  meal=$1
  
  
  echo "Prepping $meal for battle..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal\", \"cuisine\": \"$cuisine\", \"price\": $price, \"difficulty\": \"$difficulty\"}" )
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "$meal prepped for battle successfully."
  else
    echo "Failed to prep $meal for battle."
    exit 1
  fi

}

#Function to get random float
get_random() {
  echo "Getting random float..."
  response=$(curl -s -X GET "$BASE_URL/get-random")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random float retrieved successfully: $response."
  else
    echo "Failed to retrieve random float."
    exit 1
  fi
}

# Health checks
check_health
check_db



# Clear the kitchen
clear_meals

# Create meals
create_meal "Spaghetti" "Italian" 12.5 "MED"
create_meal "Sushi" "Japanese" 15.0 "HIGH"
create_meal "Tacos" "Mexican" 8.5 "LOW"

# Get a meal by ID
get_meal_by_id 1

#Get a meal by name
get_meal_by_name "Sushi"

#Updates meal stats by ID
#update_meal_stats 1 'win'



# Delete a meal by ID
delete_meal_by_id 3

# Get the leaderboard after deletion
#get_leaderboard


# Get list of combatants before adding combatants
get_combatants


# Prep combatants
prep_combatant "Spaghetti"
prep_combatant "Sushi"

# Get list of combatants after adding meals
get_combatants

# Get battle score of a combatant
#get_battle_score "Spaghetti"
#get_battle_score "Sushi"

# Start a battle
battle

# Get the leaderboard
#get_leaderboard "wins"

# Clear the combatants
clear_combatants

# Get list of combatants
get_combatants

# Get random float
#get_random


echo "All smoketests completed successfully!"
