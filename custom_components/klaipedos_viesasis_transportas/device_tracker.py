import requests

def get_optimized_bus_data():
    url = "https://www.stops.lt/klaipeda/gps_full.txt"
    response = requests.get(url)
    lines = response.text.splitlines()
    
    buses = []
    
    for line in lines:
        if not line: continue
        
        # Skaidome eilutę (CSV formatas)
        data = line.split(',')
        
        # Pagrindiniai laukai
        transport_type = data[0]  # Autobusai / Maršrutiniai taksi
        route_num = data[1]       # Pvz: "8" (Tai rodysime žemėlapyje)
        vehicle_id = data[3].replace(" ", "_").lower() # Pvz: "21_kwmt" (Unikalus ID)
        
        # Sukuriame unikalų ID sistemai
        # Pridedame prefix'ą, kad būtų lengviau filtruoti/šalinti per UI
        unique_entity_id = f"klaipeda_bus_{vehicle_id}"
        
        bus_entry = {
            "unique_id": unique_entity_id,  # Sisteminį ID HA naudos integracijos valdymui
            "route": route_num,            # Žemėlapio etiketei (Label)
            "lat": float(data[5]) / 1000000,
            "lon": float(data[4]) / 1000000,
            "speed": data[6],
            "bearing": data[7],
            "friendly_name": f"Maršrutas {route_num}" # HA rodys šį pavadinimą
        }
        
        buses.append(bus_entry)
        
    return buses
