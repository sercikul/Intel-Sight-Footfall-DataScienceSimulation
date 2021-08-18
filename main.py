from mock_data import *
from default_devices import *
from utilities import *
from tabulate import tabulate
from pymongo import MongoClient
from predictions import *


def main_script():
    print("\nWelcome to the Sight++ Footfall Predictor !\n")

    # Retrieve all default scenarios
    options_dict = {"Option": [], "Yearly Seasonality": [], "Weekly Seasonality": [], "Daily Seasonality": [],
                    "Only Business Days": []}
    while True:
        for option in scenarios:
            # Retrieve parameters
            yearly_seasonality = scenarios[option]["Yearly Seasonality"]
            weekly_seasonality = scenarios[option]["Weekly Seasonality"]
            daily_seasonality = scenarios[option]["Daily Seasonality"]
            only_bd = scenarios[option]["Only Business Days"]
            # Append to dictionary
            options_dict["Option"].append(option)
            options_dict["Yearly Seasonality"].append(yearly_seasonality)
            options_dict["Weekly Seasonality"].append(weekly_seasonality)
            options_dict["Daily Seasonality"].append(daily_seasonality)
            options_dict["Only Business Days"].append(only_bd)

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
            devices = scenario_devices[selected_option]
            total_df = synthesise_data(devices, use_cases, start_ts, end_ts)
            # WORKS: insert_to_mongodb(total_df, collection_ff)

            print(f"\nHistorical data has been synthesised and is now used by machine learning algorithms to predict"
                  f" footfall 2 months ahead from now. Please, do not terminate the program.\nIn the meantime, you can"
                  f" analyse your data in the 'Historical Footfall' and 'Real-Time Footfall' sections of your MongoDB"
                  f" dashboard.\n")

            historical_data = retrieve_from_mongo(collection_ff)
            predictions = predict_future(historical_data)
            # WORKS: insert_to_mongodb(predictions, collection_preds)
            print(f"\nTime series forecasting has now been completed and is ready for analysis in the 'Predictive"
                  f" Footfall' section of your MongoDB dashboard.\n")
            break

    return True


if __name__ == "__main__":
    cluster = MongoClient("INSERT CONNECTION STRING HERE")
    db = cluster["sight"]
    collection_ff = db["footfall"]
    collection_preds = db["predictions"]
    main_script()
