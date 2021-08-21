from mock_data import *
from default_scenarios import *
from utilities import *
from tabulate import tabulate
from pymongo import MongoClient
from predictions import *


def main_script():
    print("\nWelcome to the Sight++ Footfall Predictor !\n")

    # Retrieve all default scenarios
    options_dict = {"Option": [], "Yearly Seasonality": [], "Weekly Seasonality": [], "Daily Seasonality": []}
    while True:
        for option in scenarios:
            # Retrieve seasonality parameters
            yearly_seasonality = scenario_seasonality[option]["Yearly Seasonality"]
            weekly_seasonality = scenario_seasonality[option]["Weekly Seasonality"]
            daily_seasonality = scenario_seasonality[option]["Daily Seasonality"]
            # Append to dictionary
            options_dict["Option"].append(option)
            options_dict["Yearly Seasonality"].append(yearly_seasonality)
            options_dict["Weekly Seasonality"].append(weekly_seasonality)
            options_dict["Daily Seasonality"].append(daily_seasonality)

        options_df = pd.DataFrame(options_dict)
        print("\nThe table below lists several mock data sets including information about "
              "seasonality.\n")
        print(tabulate(options_df, tablefmt='pretty', headers='keys'))
        print("")
        input_number = input("Please select an option that matches the specifics of your venue using the index number "
                             "(e.g. '0'): ")
        user_choice = exception_handler_id(input_number, options_df)
        if user_choice == "Invalid":
            print("\n")
            return True

        else:
            selected_option = options_df.loc[user_choice][0]
            print(f"\nThe Sight++ Footfall Predictor is currently creating the data set for {selected_option}.\n"
                  f"This may take a few moments..\n")
            scenario = scenarios[selected_option]
            total_df, cum_visitors = synthesise_data(scenario, use_cases, start_ts, end_ts)
            devices = device_info[selected_option]
            # Insert data and selected scenario settings to database
            insert_to_mongodb(total_df, collection_ff, db)
            insert_to_mongodb(cum_visitors, collection_visits, db)
            print(f"\nHistorical data has been synthesised and is now used by machine learning algorithms to predict"
                  f" footfall 2 months ahead from now. Please, do not terminate the program.\nIn the meantime, you can"
                  f" analyse your data in the 'Historical Footfall' and 'Real-Time Footfall' sections of your MongoDB"
                  f" dashboard.\n")
            insert_to_mongodb(scenario, collection_scenario, db)
            insert_to_mongodb(devices, collection_devices, db)
            historical_data = retrieve_from_mongo(collection_ff, db)
            predictions = create_future_data(historical_data)
            insert_to_mongodb(predictions, collection_preds, db)
            print(f"\nTime series forecasting has now been completed and is ready for analysis in the 'Predictive"
                  f" Footfall' section of your MongoDB dashboard.\n")

            break

    return True


if __name__ == "__main__":
    cluster = MongoClient("mongodb+srv://sightpp:UCLSightPP2021@sightcluster.ea126.mongodb.net/myFirstDatabase"
                          "?retryWrites=true&w=majority")
    db = cluster["sight"]
    collection_ff = db["footfall"]
    collection_preds = db["predictions"]
    collection_scenario = db["scenario"]
    collection_devices = db["devices"]
    collection_visits = db["cumVisitCount"]
    main_script()
