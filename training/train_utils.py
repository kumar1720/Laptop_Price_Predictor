import re

def parse_memory(memory_str):
    memory_str = str(memory_str).upper()
    hdd = 0.0
    ssd = 0.0
    hybrid = 0.0
    flash = 0.0
    
    # Standardize string representations
    memory_str = memory_str.replace("GB", "").replace("TB", "000").replace(".0", "")
    
    # Split on '+' if dual storage exists
    parts = [p.strip() for p in memory_str.split("+")]
    
    for part in parts:
        # Match numeric values and storage types
        match = re.search(r'(\d+)\s*(SSD|HDD|HYBRID|FLASH STORAGE)', part)
        if match:
            value = float(match.group(1))
            st_type = match.group(2)
            
            if "SSD" in st_type:
                ssd += value
            elif "HDD" in st_type:
                hdd += value
            elif "HYBRID" in st_type:
                hybrid += value
            elif "FLASH" in st_type:
                flash += value
                
    return hdd, ssd, hybrid, flash

def extract_cpu_speed(cpu_str):
    match = re.search(r'(\d+(?:\.\d+)?)\s*GHZ', str(cpu_str), re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 2.5  # fallback default
