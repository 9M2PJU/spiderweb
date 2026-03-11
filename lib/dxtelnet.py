import telnetlib3
import asyncio
import struct
import logging
import re  

def parse_who(lines):
    lines = lines.splitlines()
    logging.debug(f"Response to 'who': {lines}")
    # Values mapped to template columns in plots.html
    row_headers = ("callsign", "type", "started", "name", "average_rtt")
    payload = []

    # Skip the first line and the last line (usually command and prompt)
    for i in range(1, len(lines) - 1):
        line = lines[i]
        
        # Skip empty lines or the header line
        if not line.strip() or line.strip().lower().startswith("callsign"):
            continue

        logging.debug(f"Parsing line ({i}): {line}")

        # DXSpider WHO output is fixed-width. We use absolute offsets from the start of the line.
        # Verified offsets: Callsign: 0-11, Type: 11-20, Started: 20-31, Name: 31-54, RTT: 54-70
        padded_line = (line + " " * 100).encode('utf-8')
        fieldstruct = struct.Struct("11s 9s 11s 23s 16s")

        try:
            fields = list(fieldstruct.unpack_from(padded_line))
            fields = [f.decode('utf-8').strip() for f in fields]
            payload.append(dict(zip(row_headers, fields)))
        except Exception as e:
            logging.error(f"Error parsing line {i}: {e}")
            
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
