# from bson import ObjectId
from collections import deque
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import Flask, redirect, url_for, flash, session,render_template
import datetime
import random
import string


import pandas as pd
import json

df=pd.read_csv('Flight Data.csv')

#TASK 1
def find_best_flights(source_city, dest_city):
    # Step 2: Filter the dataset based on user input
    filtered_df = df[(df['From City'] == source_city) & (df['To City'] == dest_city)]

    if filtered_df.empty:
        return {
            "message": f"No Direct flights found from {source_city} to {dest_city}.",
            "economy_flights": None,
            "business_flights": None,
            "duration_flights": None
        }

    # Step 3: Find the best flights based on fare (top 3 options)
    best_fare_economy = filtered_df[filtered_df['Economy Class Price (Rs)'] != -1].sort_values(by='Economy Class Price (Rs)').head(3)
    best_fare_business = filtered_df[filtered_df['Business Class Price (Rs)'] != -1].sort_values(by='Business Class Price (Rs)').head(3)

    # Display the best flights based on duration (top 3 options)
    best_duration_flights = filtered_df.sort_values(by='Duration (minutes)').head(3)

    return {
        "message": "Success",
        "economy_flights": best_fare_economy[['Flight ID', 'Economy Class Price (Rs)', 'Duration (minutes)']].to_dict(orient='records'),
        "business_flights": best_fare_business[['Flight ID', 'Business Class Price (Rs)', 'Duration (minutes)']].to_dict(orient='records'),
        "duration_flights": best_duration_flights[['Flight ID', 'Economy Class Price (Rs)', 'Duration (minutes)']].to_dict(orient='records')
    }

#TASK 5
def find_reachable_cities(source_city, min_kids_review):
    # Create a set to store reachable cities
    reachable_cities = set()

    # Create a queue for BFS traversal
    queue = deque()
    queue.append(source_city)

    while queue:
        current_city = queue.popleft()

        # Add the current city to reachable cities (excluding the source city)
        if current_city != source_city:
            reachable_cities.add(current_city)

        # Find all flights departing from the current city
        departing_flights = df[df['From City'] == current_city]

        for _, flight in departing_flights.iterrows():
            # Check if the flight's Kids Review meets the minimum requirement
            kids_review = flight['Kid_Review']
            if kids_review >= min_kids_review:
                next_city = flight['To City']

                # Ensure that we haven't visited the next city before
                if next_city not in reachable_cities:
                    queue.append(next_city)
        #if reachable_cities:
        reachable_cities.discard(source_city)  # Remove the source city from reachable cities
        # print(f"Reachable cities from {source_city} with a minimum kids review score of {min_kids_review}:")
        # print(', '.join(reachable_cities))

        # else:
        #     reachable_cities= (f"No reachable cities found from {source_city} with a minimum kids review score of {min_kids_review}.")

    return list(reachable_cities)

#TASK 2
def find_affordable_cities(source_city, available_time, budget, max_breaks):
    # Create a set to store reachable cities
    reachable_cities = set()

    # Create a queue for BFS traversal
    queue = deque()
    queue.append((source_city, 0, 0, 0))  # (City, Time, Cost, Breaks)

    while queue:
        current_city, current_time, current_cost, current_breaks = queue.popleft()

        # Check if the time exceeds the available time
        if current_time > available_time:
            continue

        # Check if the cost exceeds the budget
        if current_cost > budget:
            continue

        # Add the current city to reachable cities (excluding the source city)
        if current_city != source_city:
            reachable_cities.add(current_city)

        # Find all flights departing from the current city
        departing_flights = df[df['From City'] == current_city]

        for _, flight in departing_flights.iterrows():
            next_city = flight['To City']
            flight_time = flight['Duration (minutes)']
            flight_cost = flight['Economy Class Price (Rs)']

            # Check if the flight can be taken without exceeding time and budget constraints
            if (current_time + flight_time) <= available_time and \
               (current_cost + flight_cost) <= budget and \
               current_breaks <= max_breaks:

                queue.append((next_city, current_time + flight_time, current_cost + flight_cost, current_breaks))
        reachable_cities.discard(source_city)
    return list(reachable_cities)

app = Flask(__name__)
CORS(app)

@app.route('/task1', methods=['POST'])
def task1():
    data = request.get_json()
    source_city = data['source_city'].upper()
    dest_city = data['dest_city'].upper()


    results = find_best_flights(source_city, dest_city)
    # print(results)
    return jsonify(results)
    # return render_template('task1.html')

@app.route('/task5', methods=['POST'])
def task5():
    data=request.get_json()
    source_city = data['source_city'].upper()
    min_kids_review = data['min_kids_review']

    reachable_cities = find_reachable_cities(source_city, min_kids_review)
    return jsonify({"reachable_cities": reachable_cities})

@app.route('/task3', methods=['POST'])
def task3():
    data=request.get_json()
    source_city = data['source_city'].upper()
    available_time=data['available_time']
    budget=data['budget']
    max_breaks=data['max_breaks']

    reachable_city = find_affordable_cities(source_city,available_time, budget,max_breaks)
    return jsonify({"reachable_city": reachable_city})



if __name__ == '__main__':
    app.run(host='127.0.0.1', threaded=True,debug=True)