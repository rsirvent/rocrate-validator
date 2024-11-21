# rocrate-validator

[![Testing Pipeline Status](https://img.shields.io/github/actions/workflow/status/crs4/rocrate-validator/testing.yaml?label=Tests&logo=pytest)](https://github.com/crs4/rocrate-validator/actions/workflows/testing.yaml) [![Release Pipeline Status](https://img.shields.io/github/actions/workflow/status/crs4/rocrate-validator/release.yaml?label=Build&logo=python&logoColor=yellow)](https://github.com/crs4/rocrate-validator/actions/workflows/release.yaml) [![PyPI - Version](https://img.shields.io/pypi/v/roc-validator?logo=pypi&logoColor=green&label=PyPI)](https://pypi.org/project/roc-validator/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?logo=apache&logoColor=red)](https://opensource.org/licenses/Apache-2.0)

<!-- [![Build Status](https://repolab.crs4.it/lifemonitor/rocrate-validator/badges/develop/pipeline.svg)](https://repolab.crs4.it/lifemonitor/rocrate-validator/-/pipelines?page=1&scope=branches&ref=develop) -->

<!-- [![codecov](https://codecov.io/gh/crs4/rocrate-validator/branch/main/graph/badge.svg?token=3ZQZQZQZQZ)](https://codecov.io/gh/crs4/rocrate-validator) -->

A Python package to validate [RO-Crate](https://researchobject.github.io/ro-crate/)s.

-   Supports [CLI-based validation](#cli-based-validation) as well as [programmatic validation](#programmatic-validation) (so it can easily be used by Python code).
-   Implements an extensible validation framework to which new RO-Crate profiles
    can be added. Validation is based on SHACL shapes and Python code.
-   Currently, validation for the following profiles is implemented: RO-Crate
    (base profile), [Workflow
    RO-Crate](https://w3id.org/workflowhub/workflow-ro-crate),
    [Process Run
    Crate](https://w3id.org/ro/wfrun/process).
    [Workflow Run Crate](https://w3id.org/ro/wfrun/workflow),
    [Provenance Run Crate](https://w3id.org/ro/wfrun/provenance),
    [Workflow Testing RO-Crate](https://w3id.org/ro/wftest).

**Note**: this software is still work in progress. Feel free to try it out,
report positive and negative feedback. Do send a note (e.g., by opening an
Issue) before starting to develop patches you would like to contribute. The
implementation of validation code for additional RO-Crate profiles would be
particularly welcome.

## Installation

You can install the package using `pip` or `poetry`. The following instructions assume you have Python 3.8 or later installed.

#### [Optional Step: Create a Virtual Environment](#optional-step-create-a-virtual-environment)

It’s recommended to create a virtual environment before installing the package to avoid dependency conflicts. You can create one using the following command:

```bash
python3 -m venv .venv
```

Then, activate the virtual environment:

-   On **Unix** or **macOS**:

```bash
source .venv/bin/activate
```

-   On **Windows** (Command Prompt):

```bash
.venv\Scripts\activate
```

-   On **Windows** (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 1. Using `pip` (from PyPI)

You can install the package using `pip`:

```bash
pip install roc-validator
```

### 2. Using `poetry` (from source)

Clone the repository:

```bash
git clone https://github.com/kikkomep/rocrate-validator.git
```

Navigate to the project directory:

```bash
cd rocrate-validator
```

Ensure you have Poetry installed. If not, follow the instructions [here](https://python-poetry.org/docs/#installation). Then, install the package using `poetry`:

```bash
poetry install
```

## CLI-based Validation

After installation, use the `rocrate-validator` command to validate RO-Crates. You can run this in a virtual activated environment (if created in the [optional step](#optional-step-create-a-virtual-environment) above) or without a virtual environment if none was created.

### 1. Using the installed package

Run the validator using the following command:

```bash
rocrate-validator validate <path_to_rocrate>
```

where `<path_to_rocrate>` is the path to the RO-Crate you want to validate.

Type `rocrate-validator --help` for more information.

### 2. Using `poetry`

Run the validator using the following command:

```bash
poetry run rocrate-validator validate <path_to_rocrate>
```

where `<path_to_rocrate>` is the path to the RO-Crate you want to validate.

Type `rocrate-validator --help` for more information.

## Programmatic Validation

You can also integrate the package programmatically in your Python code. Here's an example:

```python

# Import the `services` and `models` module from the rocrate_validator package
from rocrate_validator import services, models

# Create an instance of `ValidationSettings` class to configure the validation
settings = services.ValidationSettings(
    # Set the path to the RO-Crate root directory
    rocrate_uri='/path/to/ro-crate',
    # Set the identifier of the RO-Crate profile to use for validation
    profile_identifier='ro-crate-1.1',
    # Set the requirement level for the validation
    requirement_severity=models.Severity.REQUIRED,
)

# Call the validation service with the settings
result = services.validate(settings)

# Check if the validation was successful
if not result.has_issues():
    print("RO-Crate is valid!")
else:
    print("RO-Crate is invalid!")
    # Explore the issues
    for issue in result.get_issues():
        # Every issue object has a reference to the check that failed, the severity of the issue, and a message describing the issue.
        print(f"Detected issue of severity {issue.severity.name} with check \"{issue.check.identifier}\": {issue.message}")
```

... that leads to the following output:

```bash
RO-Crate is invalid!
Detected issue of severity REQUIRED with check "ro-crate-1.1:root_entity_exists: The RO-Crate must contain a root entity.
```

## Running the tests

To run the tests, use the following command:

```bash
poetry run pytest
```

<!-- ## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) for details. -->

## License

This project is licensed under the terms of the Apache License 2.0. See the
[LICENSE](LICENSE) file for details.

## Acknowledgements

This work has been partially funded by the following sources:

-   the [BY-COVID](https://by-covid.org/) project (HORIZON Europe grant agreement number 101046203);
-   the [LIFEMap](https://www.thelifemap.it/) project, funded by the Italian Ministry of Health (Piano Operative Salute, Trajectory 3).

<img alt="Co-funded by the EU"
    src="https://raw.githubusercontent.com/crs4/rocrate-validator/develop/docs/img/eu-logo/EN_Co-fundedbytheEU_RGB_POS.png"
    width="250" align="right"/>
