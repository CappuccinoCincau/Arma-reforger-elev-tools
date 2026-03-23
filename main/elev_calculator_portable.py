from utils import *
from ballistic_data import ballistic_data_info

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'   # Reset color

# Handle input
def get_ballistic_data():
    # Get data from config ballistic data
    list_data = list(ballistic_data_info.keys())
    print("Available ballistic data:")
    # Display the menu choice
    for i, b_name in enumerate(list_data):
        range_list = ballistic_data_info[b_name].keys()
        min_range = min(range_list)
        max_range = max(range_list)
        print(f"{i+1}. {b_name} " +" | Supported Range(m): "+f"{min_range}-{max_range}")
    # Handle user input
    while True:
        try:
            select_data = int(input(f"Select the following ballistic data: "))
            if 1 <= select_data <= len(list_data):
                selected_key = list_data[select_data - 1]
                selected_min_range = min(ballistic_data_info[selected_key].keys())
                selected_max_range = max(ballistic_data_info[selected_key].keys())
                print(f"You Selected {selected_key}\n")
                return ballistic_data_info[selected_key], selected_min_range, selected_max_range
            else:
                print("Invalid Selection!")
        except ValueError as e:
            print(str(e))

def get_range_input(min_range, max_range):
    while True:
        try:
            range_to_target = float(input("Range to target(m): "))
            if min_range <= range_to_target <= max_range:
                return float(range_to_target)
            else:
                print("Invalid Range!")
        except ValueError as e:
            print(str(e))

def get_elevation_input():
    while True:
        elevation_difference = input("Elevation difference higher or lower(+/-): ")
        if elevation_difference == '':
            return 0
        try:
            return int(elevation_difference)
        except ValueError as e:
            print(str(e))

def get_coordinates():
    while True:
        x1, y1 = [float(i.strip()) for i in input("Enter Source x, y: ").split(',')]
        x2, y2 = [float(i.strip()) for i in input("Enter Target x, y: ").split(',')]
        try:
            return float(x1),float(y1),float(x2),float(y2)
        except ValueError as e:
            print(str(e))
            
def end_menu():
    while True:
        user_input = input("Do you want to recalculate? Y/N: ")
        if user_input.lower() == "y":
            print("\n")
            main()
        elif user_input.lower() == "n":
            exit()
        else:
            print("Invalid Input!")

# Running main program
def main():
    ballistic_data, ballistic_min_range, ballistic_max_range = get_ballistic_data()
    while True:
        measurement_method = input("Manual measurement (Without Coordinates)? Y/N: ")
        if measurement_method.lower() == "y":
            range_to_target = get_range_input(ballistic_min_range,ballistic_max_range)
            elevation_difference = get_elevation_input()
            elevation_mils = calculate_elevation(range_to_target, ballistic_data, elevation_difference)
            break
        elif measurement_method.lower() == "n":
            x1,y1,x2,y2 = get_coordinates()
            degrees_angle, mills_angle, range_to_target = calculate_position_angle(x1, y1, x2, y2)
            if ballistic_min_range <= range_to_target <= ballistic_max_range:
                elevation_difference = get_elevation_input()
                elevation_mils = calculate_elevation(range_to_target, ballistic_data, elevation_difference)
                print("Coordinates: " + Colors.YELLOW + f"({x1}, {y1})" + Colors.ENDC + " to " + Colors.YELLOW + f"({x2}, {y2})" + Colors.ENDC)
                print(f"Degrees (Bearing from North): " + Colors.GREEN + f"{degrees_angle:.2f} °" + Colors.ENDC + f" | Mills: "+ Colors.GREEN + f"{mills_angle:.2f}" + Colors.ENDC)
                break
            else:
                print(f"Invalid Range Please Select Another Charge! Calculated range: {range_to_target:.2f}\n")
                main()
        else:
            print("Invalid input. Please try again.")

    print(f"Distance(m): "+ Colors.BLUE+f"{range_to_target:.2f}"+Colors.ENDC)
    print(f"Required Elevation(Mils): " + Colors.RED + f"{elevation_mils}" + Colors.ENDC)
    end_menu()

if __name__ == "__main__":
    main()