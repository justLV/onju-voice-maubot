import asyncio
from nio import AsyncClient, MatrixRoom, RoomMessageText
import json
from ruamel.yaml import YAML
import os

yaml = YAML(typ='rt')  # 'rt' for "round trip"

json_fname = "rooms.json"
cred_fname = "credentials.json"
homeserver = "https://matrix.beeper.com"

got_credentials = False

device_id = None

if os.path.exists(cred_fname):
    print(f"Found {cred_fname}, using existing credentials")
    try:
        with open(cred_fname, 'r') as f:
            creds = json.load(f)
            user_id = creds['user_id']
            access_token = creds['access_token']
            device_id = creds['device_id']
    except Exception as e:
        print(f"Error loading credentials: {e}")
        exit(1)
else:
    user_id = input("User ID: @")
    user_id = f"@{user_id}:beeper.com"
    print(user_id)
    pw = input("Password: ")

async def main() -> None:
    if not device_id:
        print("No device ID found, logging in to get new device ID and access token")
        client = AsyncClient(homeserver, user_id)

        print(await client.login(password=pw))

        with open(cred_fname, 'w') as f:
            json.dump({
                "user_id": user_id,
                "access_token": client.access_token,
                "device_id": client.device_id
            }, f)

        print(f"Saved credentials to {cred_fname} for next time")

        with open('config.yaml', 'r') as file:
            config_yaml = yaml.load(file)

        config_yaml['user']['credentials']['id'] = user_id
        config_yaml['user']['credentials']['access_token'] = client.access_token
        config_yaml['user']['credentials']['device_id'] = client.device_id

        with open('config.yaml', 'w') as file:
            yaml.dump(config_yaml, file)

        print("Updated yaml for Maubot. Be patient for sync'ing of rooms...\n\n")
    else:
        print(f"Using existing credentials with device ID: {device_id}")
        client = AsyncClient(homeserver)

        client.user_id = user_id
        client.access_token = access_token
        client.device_id = device_id

    await client.sync(60000) # upper limit of 1 minute, shouldn't need to exceed but if so, increase

    rooms = client.rooms
    rooms_json = {}
    for room_id, room in rooms.items():

        names = [key for key in room.names.keys()]

        source = None
        for name in names:
            if 'bridge bot' in name.lower():
                source = name.split()[0]
                names.remove(name)
                break
        
        if(not source):
            source = room.display_name

        # names = list(filter(lambda x: x.lower() not in ["name_to_filter_1", "name_to_filter_2"], names))

        rooms_json[room_id] = {
            "source": source,
            "names": names
        }
        if(names):
            print(f"{names[0]} ({source})  [{len(names)}]")
        else:
            print(f"{room.display_name} ({source}) - No names found")

    print(f"\nFound {len(rooms_json)} rooms! Writing to {json_fname}")
    with open(json_fname, 'w') as f:
        f.write(json.dumps(rooms_json, indent=4))
    
    if not device_id:
        print(f"\nNow authorize this device ({client.device_id}) from Beeper and run `python -m maubot.standalone` to start the bot (recommended within tmux or a screen session)")
        print(f"Add blacklisted rooms to blacklist.txt")
    else:
        print(f"\nUpdated {json_fname}")
    await client.close()

asyncio.run(main())
