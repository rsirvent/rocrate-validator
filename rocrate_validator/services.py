import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Union

import requests
import requests_cache

import rocrate_validator.log as logging
from rocrate_validator.constants import DEFAULT_PROFILE_IDENTIFIER
from rocrate_validator.events import Subscriber
from rocrate_validator.models import (Profile, Severity, ValidationResult,
                                      ValidationSettings, Validator)
from rocrate_validator.utils import URI, get_profiles_path

# set the default profiles path
DEFAULT_PROFILES_PATH = get_profiles_path()

# set up logging
logger = logging.getLogger(__name__)


def validate(settings: Union[dict, ValidationSettings],
             subscribers: Optional[list[Subscriber]] = None) -> ValidationResult:
    """
    Validate a RO-Crate against a profile
    """
    # if settings is a dict, convert to ValidationSettings
    settings = ValidationSettings.parse(settings)

    # parse the rocrate path
    rocrate_path: URI = URI(settings.data_path)
    logger.debug("Validating RO-Crate: %s", rocrate_path)

    # check if the RO-Crate exists
    if not rocrate_path.is_available():
        raise FileNotFoundError(f"RO-Crate not found: {rocrate_path}")

    # check if the requests cache is enabled
    if settings.http_cache_timeout > 0:
        # Set up requests cache
        requests_cache.install_cache(
            '/tmp/rocrate_validator_cache',
            expire_after=settings.http_cache_timeout,  # Cache expiration time in seconds
            backend='sqlite',  # Use SQLite backend
            allowable_methods=('GET',),  # Cache GET
            allowable_codes=(200, 302, 404)  # Cache responses with these status codes
        )

    # check if remote validation is enabled
    remote_validation = settings.remote_validation
    logger.debug("Remote validation: %s", remote_validation)
    if remote_validation:
        # create a validator
        validator = Validator(settings)
        logger.debug("Validator created. Starting validation...")
        if subscribers:
            for subscriber in subscribers:
                validator.add_subscriber(subscriber)
        # validate the RO-Crate
        result = validator.validate()
        logger.debug("Validation completed: %s", result)
        return result

    def __do_validate__(settings: ValidationSettings):
        # create a validator
        validator = Validator(settings)
        logger.debug("Validator created. Starting validation...")
        if subscribers:
            for subscriber in subscribers:
                validator.add_subscriber(subscriber)
        # validate the RO-Crate
        result = validator.validate()
        logger.debug("Validation completed: %s", result)
        return result

    def __extract_and_validate_rocrate__(rocrate_path: Path):
        # store the original data path
        original_data_path = settings.data_path

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # extract the RO-Crate to the temporary directory
                with zipfile.ZipFile(rocrate_path, "r") as zip_ref:
                    zip_ref.extractall(tmp_dir)
                    logger.debug("RO-Crate extracted to temporary directory: %s", tmp_dir)
                # update the data path to point to the temporary directory
                settings.data_path = Path(tmp_dir)
                # continue with the validation process
                return __do_validate__(settings)
            finally:
                # restore the original data path
                settings.data_path = original_data_path
                logger.debug("Original data path restored: %s", original_data_path)

    # check if the RO-Crate is a remote RO-Crate,
    # i.e., if the RO-Crate is a URL. If so, download the RO-Crate
    # and extract it to a temporary directory. We support either http or https
    # or ftp protocols to download the remote RO-Crate.
    if rocrate_path.scheme in ('http', 'https', 'ftp'):
        logger.debug("RO-Crate is a remote RO-Crate")
        # create a temp folder to store the downloaded RO-Crate
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            # download the remote RO-Crate
            with requests.get(rocrate_path.uri, stream=True, allow_redirects=True) as r:
                with open(tmp_file.name, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            logger.debug("RO-Crate downloaded to temporary file: %s", tmp_file.name)
            # continue with the validation process by extracting the RO-Crate and validating it
            return __extract_and_validate_rocrate__(Path(tmp_file.name))

    # check if the RO-Crate is a ZIP file
    elif rocrate_path.as_path().suffix == ".zip":
        logger.debug("RO-Crate is a local ZIP file")
        # continue with the validation process by extracting the RO-Crate and validating it
        return __extract_and_validate_rocrate__(rocrate_path.as_path())

    # if the RO-Crate is not a ZIP file, directly validate the RO-Crate
    elif rocrate_path.is_local_directory():
        logger.debug("RO-Crate is a local directory")
        settings.data_path = rocrate_path.as_path()
        return __do_validate__(settings)
    else:
        raise ValueError(
            f"Invalid RO-Crate URI: {rocrate_path}. "
            "It MUST be a local directory or a ZIP file (local or remote).")


def get_profiles(profiles_path: Path = DEFAULT_PROFILES_PATH, publicID: str = None, severity=Severity.OPTIONAL) -> list[Profile]:
    """
    Load the profiles from the given path
    """
    profiles = Profile.load_profiles(profiles_path, publicID=publicID, severity=severity)
    logger.debug("Profiles loaded: %s", profiles)
    return profiles


def get_profile(profiles_path: Path = DEFAULT_PROFILES_PATH,
                profile_identifier: str = DEFAULT_PROFILE_IDENTIFIER, publicID: str = None) -> Profile:
    """
    Load the profiles from the given path
    """
    profile_path = profiles_path / profile_identifier
    if not Path(profiles_path).exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    profile = Profile.load(profiles_path, f"{profiles_path}/{profile_identifier}",
                           publicID=publicID, severity=Severity.OPTIONAL)
    logger.debug("Profile loaded: %s", profile)
    return profile
