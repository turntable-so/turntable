#!/bin/bash

# Load the environment variables from the .env file
source .env

# Function to extract the database name from the Supabase URL
extract_db_name() {
  local url=$1
  # Extract the database name from the URL
  echo $url | sed -E 's/^https?:\/\/([^.]+)\..*/\1/'
}

# Extract the database name from the Supabase URL
DB_NAME=$(extract_db_name $SUPABASE_URL)

# Run the supabase command with the extracted database name
supabase db pull --db-url postgres://postgres.${DB_NAME}:${SUPABASE_PASSWORD}@${SUPABASE_HOST}:5432/postgres