import telnetlib3
import asyncio
import struct
import logging
import re  

def parse_who(raw_data):
    lines = raw_data.splitlines()
    logging.debug(f"Response to 'who': {lines}")
    
    # 1. Identify the header line and detected columns
    header_line = None
    for line in lines:
        if "CALLSIGN" in line.upper() and ("TYPE" in line.upper() or "NAME" in line.upper()):
            header_line = line
            break
    
    # Fallback to default headers if no header line is found
    if not header_line:
        logging.warning("No header found in WHO output, using default fallback")
        header_line = "CALLSIGN   TYPE       STATE      STARTED            NAME             AVG RTT"

    # 2. Map column names to their starting indices
    h_up = header_line.upper()
    possible_cols = [
        ("callsign", "CALLSIGN"),
        ("type", "TYPE"),
        ("state", "STATE"),
        ("started", "STARTED"),
        ("name", "NAME"),
        ("average_rtt", "AVG RTT"),
    ]
    
    col_mapping = []
    for key, name in possible_cols:
        idx = h_up.find(name)
        if idx != -1:
            col_mapping.append((key, idx))
    
    col_mapping.sort(key=lambda x: x[1])

    # 3. Parse each row using the detected offsets
    payload = []
    for line in lines:
        line_up = line.upper()
        # Skip header, prompt, command echo, and empty lines
        if "CALLSIGN" in line_up or "DXSPIDER" in line_up or not line.strip() or line.strip().lower() == "who":
            continue
            
        row = {}
        for i in range(len(col_mapping)):
            key, start = col_mapping[i]
            if i < len(col_mapping) - 1:
                end = col_mapping[i+1][1]
            else:
                end = len(line) + 50 # Capture till end
            
            val = line[start:end].strip()
            row[key] = val
        
        # Ensure 'started' contains the timestamp even if it's shifted
        # In some formats, 'state' might contain 'prompt 1' and 'started' is correct.
        # In others, 'state' might BE missing and 'started' is the second field.
        
        # The web application expects these keys specifically:
        # callsign, type, started, name, average_rtt
        final_row = {
            "callsign": row.get("callsign", ""),
            "type": row.get("type", ""),
            "started": row.get("started", row.get("state", "")),
            "name": row.get("name", ""),
            "average_rtt": row.get("average_rtt", "")
        }
        
        # If 'started' is empty but 'state' looks like a timestamp, prefer it
        if not final_row["started"] and row.get("state"):
            final_row["started"] = row["state"]

        payload.append(final_row)
        
    return payload

async def fetch_who_and_version(host, port, user, password=None):
    logging.debug(f"Connecting to {host}:{port} for WHO and SH/VERSION")
    WAIT_LOGIN = b"login:"
    WAIT_PASS = b"password:"
    WAIT_FOR = b"dxspider >"

    reader, writer = await telnetlib3.open_connection(host, port, encoding=None)
    who_data = ""
    version_info = "Unknown"

    try:
        await reader.readuntil(WAIT_LOGIN)
        writer.write(user.encode('utf-8') + b'\n')
        if password:
            try:
                await asyncio.wait_for(reader.readuntil(WAIT_PASS), timeout=5)
                writer.write(password.encode('utf-8') + b'\n')
            except asyncio.TimeoutError:
                logging.error("Timeout waiting for password prompt")
                return [], "Login timeout"

        await reader.readuntil(WAIT_FOR)
        logging.debug("Login successful")

        writer.write(b'who\n')
        who_response = await reader.readuntil(WAIT_FOR)
        who_data = who_response.decode('utf-8')

        writer.write(b'sh/version\n')
        version_response = await reader.readuntil(WAIT_FOR)
        res = version_response.decode('utf-8').strip().splitlines()
        logging.debug(f"Full SH/VERSION Response:\n{res}")

        for line in res:
            logging.debug(f"Processing Line: {line}")
            match = re.search(r"DXSpider v([\d.]+) \(build (\d+)", line)
            if match:
                version_info = f"DXSpider v{match.group(1)} build {match.group(2)}"
                logging.debug(f"Extracted DXSpider Version: {version_info}")
                break  
        else:
            logging.debug("No valid DXSpider version found in the response.")

    except EOFError:
        logging.error("End of buffer reached unexpectedly")
    except Exception as e:
        logging.error(f"Error retrieving WHO and version info: {e}")
    finally:
        writer.close()
        reader.feed_eof()
        logging.debug("Connection closed")

    return parse_who(who_data), version_info
