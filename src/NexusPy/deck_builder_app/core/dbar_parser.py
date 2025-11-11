import re

def parse_dbar_file(file_path):
    """
    Parses a DBAR .txt file from AnaREDE and extracts generation and load data.

    Args:
        file_path (str): The absolute path to the .txt deck file.

    Returns:
        dict: A dictionary containing structured data with two keys:
              'bars' -> a dict of bar data, keyed by bar number.
              'summary' -> a dict of the summary totals.
        Returns None if the file cannot be read.
    """
    try:
        with open(file_path, 'r', encoding='latin-1') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    bars = {}
    summary = {}
    is_summary_section = False

    for line in lines:
        # Check for the start of the summary section
        if line.strip().startswith('(TOTAIS'):
            is_summary_section = True
            continue

        if is_summary_section:
            # Parse summary lines
            if line.strip().startswith('(') and not line.strip().startswith('(TOTAL GERAL'):
                try:
                    # Extract agent name and values using regex for flexibility
                    match = re.match(r'\(([\w\s-]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', line.strip())
                    if match:
                        agent, gen_p, _, load_p, load_q = match.groups()
                        summary = {
                            'agent': agent.strip(),
                            'total_gen_p': float(gen_p),
                            'total_load_p': float(load_p),
                            'total_load_q': float(load_q)
                        }
                except (ValueError, IndexError):
                    continue # Ignore lines that don't match the summary format
        else:
            # Parse bar data lines
            if len(line) > 6 and line[6] == 'M':
                try:
                    bar_num = int(line[1:6])
                    
                    # Initialize bar if not present
                    if bar_num not in bars:
                        bars[bar_num] = {'num': bar_num, 'pg': 0.0, 'qg': 0.0, 'pl': 0.0, 'ql': 0.0}

                    # Try to parse generation (Pg, Qg)
                    try:
                        pg = float(line[39:45])
                        qg = float(line[45:51])
                        bars[bar_num]['pg'] += pg
                        bars[bar_num]['qg'] += qg
                    except (ValueError, IndexError):
                        pass # This part of the line might be empty

                    # Try to parse load (Pl, Ql)
                    try:
                        pl = float(line[59:65])
                        ql = float(line[65:71])
                        bars[bar_num]['pl'] += pl
                        bars[bar_num]['ql'] += ql
                    except (ValueError, IndexError):
                        pass # This part of the line might be empty

                except (ValueError, IndexError):
                    continue # Ignore lines that don't match the bar data format

    # Convert the bars dictionary to a list of its values
    bar_list = list(bars.values())
    
    return {'bars': bar_list, 'summary': summary}

if __name__ == '__main__':
    # Example usage for testing the parser directly
    # Note: You need to provide a valid path to a deck file
    test_file = 'path/to/your/deck/file.txt'
    if os.path.exists(test_file):
        parsed_data = parse_dbar_file(test_file)
        if parsed_data:
            import json
            print(json.dumps(parsed_data, indent=2))
    else:
        print(f"Test file not found: {test_file}")
        print("Please update the path in the test block to run a direct test.")
