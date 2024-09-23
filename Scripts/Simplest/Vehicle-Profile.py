import random
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from math import cos, sin, radians, pi
import random

def generate_initial_states(num_vehicles, movement_range):
    return [{
        'x0': random.uniform(movement_range[0], movement_range[1]),
        'y0': random.uniform(movement_range[0], movement_range[1]),
        'angle': random.uniform(0, 360),
        'type': random.choice(vehicle_types),
        'speed': random.uniform(1, 3),
        'pos': random.uniform(0, 100),
        'lane': random.randint(1, 3)
    } for _ in range(num_vehicles)]

def update_position(state, timestep, period):
    if timestep % period == 0:
        return state['x0'], state['y0'], state['angle']

    rad = radians(state['angle'])
    dx = state['speed'] * cos(rad)
    dy = state['speed'] * sin(rad)
    new_x = state['x0'] + dx * (timestep % period)
    new_y = state['y0'] + dy * (timestep % period)

    if new_x < 0:
        new_x = -new_x
        state['angle'] = (180 - state['angle']) % 360
    elif new_x > 10:
        new_x = 20 - new_x
        state['angle'] = (180 - state['angle']) % 360

    if new_y < 0:
        new_y = -new_y
        state['angle'] = (-state['angle']) % 360
    elif new_y > 10:
        new_y = 20 - new_y
        state['angle'] = (-state['angle']) % 360

    return new_x, new_y, state['angle']

def generate_vehicle_data(num_timesteps, num_vehicles, filename, period=20):
    root = ET.Element('fcd-export')
    initial_states = generate_initial_states(num_vehicles, (0, 10))

    for timestep in range(num_timesteps):
        time_step_elem = ET.SubElement(root, 'timestep', time=f"{timestep}.00")
        for vehicle_id, vehicle_data in vehicles.items():
            ET.SubElement(time_step_elem, 'vehicle', {
                'id': vehicle_id,
                'x': f"{vehicle_data['x']:.2f}",
                'y': f"{vehicle_data['y']:.2f}",
                'angle': f"{vehicle_data['angle']:.2f}",
                'type': vehicle_data['type'],
                'speed': f"{vehicle_data['speed']:.2f}",
                'pos': f"{vehicle_data['pos']:.2f}",
                'lane': f"{vehicle_data['lane']}"
            })

            vehicle_data['speed'], vehicle_data['angle'] = update_speed_and_angle(
                vehicle_data['speed'], vehicle_data['angle'], speed_change_range, angle_change_range, max_speed=3
            )

            vehicle_data['x'], vehicle_data['y'], vehicle_data['angle'] = random_movement(
                vehicle_data['x'], vehicle_data['y'], vehicle_data['speed'], vehicle_data['angle'], movement_range=(0, 10)
            )

            vehicle_data['pos'] += vehicle_data['speed'] * 0.1
            vehicle_data['lane'] = update_lane(vehicle_data['lane'], lane_change_range)

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)

generate_vehicle_data(900, 100, 'D:\\vehicles_data_offline.xml')
filename = 'D:\\vehicles_data_offline.xml'

generate_vehicle_data(num_timesteps, num_vehicles, vehicle_types, filename,
                      speed_change_range=(-4, 4), angle_change_range=(-90, 90),
                      movement_range=(0, 10), lane_change_range=(-1, 1))
print(f"Data successfully saved to {filename}.")