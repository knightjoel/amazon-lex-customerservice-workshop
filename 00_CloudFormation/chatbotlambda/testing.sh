#!/usr/bin/env bash


#lambda-local -l index.js -h handler -r us-east-1 -e apply-plan-input.json -t 60 -E {\"USER_DDB_TABLE\":\"lex-workshop-Users\"\,\"USER_DDB_TABLE_PHONE_INDEX\":\"phoneindex\"\,\"AWS_REGION\":\"us-east-1\"\,\"USER_PLAN_DDB_TABLE\":\"lex-workshop-UserTravelPlansDDBTable-1W4YDS741OISG\"}

#lambda-local -l index.js -h handler -r us-east-1 -e check-plan-loggedin.json -t 60 -E {\"USER_DDB_TABLE\":\"lex-workshop-Users\"\,\"USER_DDB_TABLE_PHONE_INDEX\":\"phoneindex\"\,\"AWS_REGION\":\"us-east-1\"\,\"USER_PLAN_DDB_TABLE\":\"lex-workshop-UserTravelPlansDDBTable-1W4YDS741OISG\"}

#lambda-local -l index.js -h handler -r us-east-1 -e finish.json -t 60 -E {\"USER_DDB_TABLE\":\"lex-workshop-Users\"\,\"USER_DDB_TABLE_PHONE_INDEX\":\"phoneindex\"\,\"AWS_REGION\":\"us-east-1\"\,\"USER_PLAN_DDB_TABLE\":\"lex-workshop-UserTravelPlansDDBTable-1W4YDS741OISG\"}

#lambda-local -l index.js -h handler -r us-east-1 -e apply-plan-validate.json -t 60 -E {\"USER_DDB_TABLE\":\"lex-workshop-Users\"\,\"USER_DDB_TABLE_PHONE_INDEX\":\"phoneindex\"\,\"AWS_REGION\":\"us-east-1\"\,\"USER_PLAN_DDB_TABLE\":\"lex-workshop-UserTravelPlansDDBTable-1W4YDS741OISG\"\,\"PLAN_CATALOGUE_DDB_TABLE\":\"lex-workshop-TravelPlanCatalogDDBTable-VJ8OITVVRTBV\"}

lambda-local -l index.js -h handler -r us-east-1 -e list-plans.json -t 60 -E {\"USER_DDB_TABLE\":\"lex-workshop-Users\"\,\"USER_DDB_TABLE_PHONE_INDEX\":\"phoneindex\"\,\"AWS_REGION\":\"us-east-1\"\,\"USER_PLAN_DDB_TABLE\":\"lex-workshop-UserTravelPlansDDBTable-1W4YDS741OISG\"\,\"PLAN_CATALOGUE_DDB_TABLE\":\"lex-workshop-TravelPlanCatalogDDBTable-JRGT4BTPLNTC\"}
