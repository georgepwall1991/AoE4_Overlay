import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from overlay.logging_func import get_logger
from overlay.settings import settings

import threading

logger = get_logger(__name__)
session = requests.session()


def close_session():
    """ Closes the requests session """
    session.close()


def find_player(text: str) -> bool:
    """ Tries to find a player based on a text containing either name, steam_id or profile_id
    Returns `True` if the player was found. Settings are automatically updated."""

    # Save the current player settings
    old = (settings.player_name, settings.profile_id, settings.steam_id)

    # First try if it's a profile id
    try:
        url = f"https://aoe4world.com/api/v0/players/{text}"
        resp = json.loads(session.get(url, timeout=10).text)
        if 'name' in resp:
            settings.profile_id = resp['profile_id']
            settings.player_name = resp['name']
            settings.steam_id = resp.get('steam_id')
            logger.info(
                f"Found player by profile_id: {settings.player_name} ({settings.profile_id})"
            )
            return True
    except json.decoder.JSONDecodeError:
        logger.debug(f"Invalid JSON response when looking up player '{text}' by profile_id")
    except Exception:
        logger.exception(f"Error looking up player '{text}' by profile_id")

    # Then try query
    try:
        url = f"https://aoe4world.com/api/v0/players/search?query={text}"
        resp = json.loads(session.get(url, timeout=10).text)
        if resp['players']:
            settings.profile_id = resp['players'][0]['profile_id']
            settings.player_name = resp['players'][0]['name']
            settings.steam_id = resp['players'][0].get('steam_id')
            logger.info(
                f"Found player by query: {settings.player_name} ({settings.profile_id})"
            )
            return True
    except Exception:
        logger.exception(f"Error searching for player '{text}' by query")

    logger.info(f"Failed to find a player with: {text}")
    settings.player_name, settings.profile_id, settings.steam_id = old
    return False


def get_full_match_history(amount: int) -> Optional[List[Any]]:
    """ Gets match history and adds some data its missing"""

    url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/games?limit={amount}"
    try:
        resp = session.get(url, timeout=10).text
        data = json.loads(resp)
        return data['games']
    except Exception:
        logger.exception(f"Error fetching match history for profile {settings.profile_id}")
        return None


def get_rating_history(leaderboard_id: int, amount: int = 100) -> Optional[List[Any]]:
    """Gets rating history for a specific leaderboard.

    Args:
        leaderboard_id: The leaderboard ID (17=1v1, 18=2v2, 19=3v3, 20=4v4)
        amount: Number of rating entries to retrieve

    Returns:
        List of rating history entries or None on error
    """
    url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/ratings/{leaderboard_id}?limit={amount}"
    try:
        resp = session.get(url, timeout=10).text
        data = json.loads(resp)
        return data.get('ratings', [])
    except Exception:
        logger.exception(f"Error fetching rating history for profile {settings.profile_id}, leaderboard {leaderboard_id}")
        return None


def get_leaderboard_data(leaderboard_id: int) -> Optional[Dict[str, Any]]:
    """Gets leaderboard data for a specific leaderboard.

    Args:
        leaderboard_id: The leaderboard ID (17=1v1, 18=2v2, 19=3v3, 20=4v4)

    Returns:
        Dictionary with leaderboard data or None on error
    """
    url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/games?leaderboard={leaderboard_id}&limit=1"
    try:
        resp = session.get(url, timeout=10).text
        data = json.loads(resp)
        # Return player stats from the leaderboard
        return data
    except Exception:
        logger.exception(f"Error fetching leaderboard data for profile {settings.profile_id}, leaderboard {leaderboard_id}")
        return None


class Api_checker:

    def __init__(self):
        self.stop_event = threading.Event()
        self.force_check_event = threading.Event()
        self.last_match_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.last_rating_timestamp = datetime(1900, 1, 1, 0, 0, 0)

    def reset(self):
        """ Resets last timestamps"""
        self.last_match_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.last_rating_timestamp = datetime(1900, 1, 1, 0, 0, 0)
        self.force_check_event.set()

    def sleep(self, seconds: int) -> bool:
        """ Sleeps while checking for stop_event
        Returns `True` if we need to stop the parent function"""
        if self.stop_event.is_set():
            return True
        
        # Wait for either stop_event or force_check_event, or timeout
        # We need to wait for 'seconds', but can be interrupted by force_check
        if self.force_check_event.is_set():
            self.force_check_event.clear()
            return False

        start_time = time.time()
        while time.time() - start_time < seconds:
            remaining = seconds - (time.time() - start_time)
            if remaining <= 0:
                break
            
            if self.stop_event.is_set():
                return True
            
            wait_time = min(remaining, 0.5)
            if self.force_check_event.wait(timeout=wait_time):
                self.force_check_event.clear()
                return False
                
        return self.stop_event.is_set()

    def check_for_new_game(self,
                           delayed_seconds: int = 0
                           ) -> Optional[Dict[str, Any]]:
        """ Continously check if there are a new game being played
        Returns match data if there is a new game"""

        if self.sleep(delayed_seconds):
            return None

        while not self.stop_event.is_set():
            result = self.get_data()
            if result is not None:
                return result

            if self.sleep(settings.interval):
                return None

    def get_data(self) -> Optional[Dict[str, Any]]:
        if self.stop_event.is_set():
            return None

        # Get last match from aoe4world.com
        try:
            url = f"https://aoe4world.com/api/v0/players/{settings.profile_id}/games/last"
            resp = session.get(url, timeout=10)
            data = json.loads(resp.text)
        except Exception:
            logger.exception(f"Error fetching last game for profile {settings.profile_id}")
            return None

        if self.stop_event.is_set():
            return None
        if "error" in data:
            return None

        # Calc old leaderboard id
        data['leaderboard_id'] = 0
        try:
            data['leaderboard_id'] = int(data['kind'][-1]) + 16
        except Exception:
            logger.debug(f"Could not parse leaderboard_id from kind '{data.get('kind')}', defaulting to 0")

        # Calc started time
        started = datetime.strptime(data['started_at'],
                                    "%Y-%m-%dT%H:%M:%S.000Z")
        data['started_sec'] = started.timestamp()

        # Show the last game
        if started > self.last_match_timestamp:  # and data['ongoing']:
            self.last_match_timestamp = started
            return data

    @property
    def force_stop(self):
        return self.stop_event.is_set()

    @force_stop.setter
    def force_stop(self, value):
        if value:
            self.stop_event.set()
        else:
            self.stop_event.clear()