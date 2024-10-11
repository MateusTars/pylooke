from datetime import datetime

def identifier_with_time(machine_id: str) -> str:
    formatted_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{machine_id}@@{formatted_time}"