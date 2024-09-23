# import random
# import xml.etree.ElementTree as ET
# from xml.dom.minidom import parseString

# def generate_tasks_data(num_seconds, num_tasks, num_creators, filename, power_range=(1, 3), deadline_range=(1, 2)):
#     root = ET.Element('tasks')

#     task_id = 1
#     tasks_per_second = [0] * num_seconds
#     for _ in range(num_tasks):
#         tasks_per_second[random.randint(0, num_seconds - 1)] += 1

#     creators = [f"veh{creator_id}" for creator_id in range(1, num_creators + 1)]
#     active_tasks = {creator: [] for creator in creators}

#     for second in range(num_seconds):
#         for _ in range(tasks_per_second[second]):
#             available_creators = [creator for creator, deadlines in active_tasks.items() if not deadlines or min(deadlines) > second]
#             if not available_creators:
#                 continue
#             creator = random.choice(available_creators)

#             if second + deadline_range[1] >= num_seconds:
#                 continue

#             deadline = random.randint(second + deadline_range[0], min(second + deadline_range[1], num_seconds - 1))

#             size = (14/10) * (deadline - second)
#             if size < 1:
#                 continue

#             task_elem = ET.SubElement(root, 'task', {
#                 'id': f"task{task_id}",
#                 'name': f"Task_{task_id}",
#                 'creation_time': f"{second}",
#                 'deadline': f"{deadline}",
#                 'power_needed': f"{random.uniform(*power_range):.2f}",
#                 'size': f"{size:.2f}",
#                 'creator': creator
#             })
#             active_tasks[creator].append(deadline)
#             task_id += 1

#         for creator in active_tasks:
#             active_tasks[creator] = [d for d in active_tasks[creator] if d > second]

#     rough_string = ET.tostring(root, 'utf-8')
#     reparsed = parseString(rough_string)
#     pretty_xml_as_string = reparsed.toprettyxml(indent="  ")

#     with open(filename, 'w', encoding='utf-8') as f:
#         f.write(pretty_xml_as_string)

# num_seconds = 100
# num_tasks = 300
# num_creators = 100
# filename = 'D:\\tasks_data.xml'

# generate_tasks_data(num_seconds, num_tasks, num_creators, filename, power_range=(1, 3), deadline_range=(1, 2))
# print(f"Data successfully saved to {filename}.")

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import random

def generate_tasks_data(num_seconds, num_tasks, num_creators, filename, period=20):
    root = ET.Element('tasks')
    for second in range(num_seconds):
        cycle_second = second % period  # Reset every 20 seconds
        for task_id in range(1, num_tasks + 1):
            creator_id = random.randint(1, num_creators)
            deadline = cycle_second + random.randint(1, 5)  # Deadline within the next 1 to 5 seconds
            power_needed = random.uniform(1, 3)
            task_elem = ET.SubElement(root, 'task', {
                'id': f"task{task_id}",
                'name': f"Task_{task_id}",
                'creation_time': f"{cycle_second}",
                'deadline': f"{deadline}",
                'power_needed': f"{power_needed:.2f}",
                'size': f"{random.uniform(1, 3):.2f}",
                'creator': f"veh{creator_id}"
            })

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="  ")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_as_string)

generate_tasks_data(900, 300, 100, 'D:\\tasks_data_offline.xml')
filename = 'D:\\tasks_data_offline.xml'
print(f"Data successfully saved to {filename}.")
