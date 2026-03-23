import math

def degree_to_mills(degree):
    return degree * (6400 / 360)

def calculate_position_angle(x1, y1, x2, y2):
    # Calculate the difference in coordinates
    delta_x = x2 - x1
    delta_y = y2 - y1
    
    # Calculate the angle in radians using math.atan2(y, x)
    theta = math.atan2(delta_x, delta_y)
    degrees_bearing = math.degrees(theta)
    degrees_final = (degrees_bearing + 360) % 360

    # Calculate mills (1 degree is approximately 17.778 mills, 6400 mills in a circle)
    # Note: Different military standards use different values for mills (e.g., 6400 or 6000).
    # We will use 6400 mills for a full circle.
    mills = degree_to_mills(degrees_final)

    distance = math.dist((x1,y1),(x2,y2)) * 100

    return degrees_final, mills, distance

def calculate_elevation(distance_m, ballistic_data, elevation_difference_m):
    distances = sorted(ballistic_data.keys())
    if distance_m < distances[0]:
        base_elev = ballistic_data[distances[0]]
    elif distance_m > distances[-1]:
        base_elev = ballistic_data[distances[-1]] # Or handle as out of range
    else:
        # Simplified linear interpolation (for better accuracy use a library)
        for i in range(len(distances) - 1):
            if distances[i] <= distance_m <= distances[i+1]:
                d1 = distances[i]
                d2 = distances[i+1]
                e1 = ballistic_data[d1]
                e2 = ballistic_data[d2]
                # Formula: e1 + (e2 - e1) * (distance_m - d1) / (d2 - d1)
                base_elev = e1 + (e2 - e1) * (distance_m - d1) / (d2 - d1)
                break
    
    # 2. Adjust for elevation difference
    # A common approximation is 1 mil per meter of elevation difference over distance.
    # More precisely, use the formula found in some guides: (elevation difference / distance) * 1000.
    # This is an approximation and might need truing in-game.
    elevation_adjustment_mils = (elevation_difference_m / distance_m) * 1000 if distance_m > 0 else 0
    
    # In Arma, if the fire position is higher than the target, you might add or subtract depending on the angle group.
    # General rule for high angle indirect fire: if target is higher, add mils; if lower, subtract.
    final_elevation_mils = base_elev + elevation_adjustment_mils
    return round(final_elevation_mils, 2)