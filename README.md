<div align="center">

# ARC-V2-Util

**Shared utilities for the ARC V2 ecosystem.**

*Reusable · lightweight · ARC-native*

<br>

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python\&logoColor=white)](#)
[![ARC V2](https://img.shields.io/badge/ARC%20V2-Utility-blue)](#)
[![Status](https://img.shields.io/badge/status-active%20development-orange)](#)

</div>


## What is ARC-V2-Util?

ARC-V2-Util is a collection of **shared utility components** for projects within the ARC V2 ecosystem.

The goal is to provide small, reusable building blocks for common concerns without requiring each ARC component to implement them independently.

> [!NOTE]
> ARC-V2-Util is expected to be **extended in the future** as additional utilities become useful across the ARC V2 ecosystem.

## Table of Contents

* [What is ARC-V2-Util?](#what-is-arc-v2-util)
* [Utilities](#utilities)

  * [`Constant`](#constant)
  * [`retry`](#retry)
  * [Errors](#errors)
* [Installation](#installation)
* [Usage](#usage)
* [Design](#design)
* [Development Status](#development-status)


## Utilities

### `Constant`

`Constant` provides a small configuration abstraction that combines:

* a default value
* automatic type inference
* optional explicit type declaration
* environment-variable overrides
* type validation
* convenient access to the resolved value

The constant derives its name from the assignment and resolves its value from the corresponding environment variable when available.

```python
from arc_v2_util.constants import Constant

PORT = Constant(default=7842)

DEBUG = Constant(default=False)

NAME = Constant(default="ARC")
```

The resolved value can be accessed through `.value`:

```python
PORT.value
DEBUG.value
NAME.value
```

`Constant` also supports normal Python-style conversion and comparisons through its implemented methods.

#### Explicit types

```python
PORT = Constant(default=7842, type=int)
```

An explicitly declared type must match the default value, otherwise `ConstantTypeError` is raised.

#### Environment overrides

Given:

```python
PORT = Constant(default=7842)
```

the environment can override the default:

```bash
export PORT=9000
```

The resulting value becomes:

```python
PORT.value  # 9000
```

### `retry`

`retry` provides a simple asynchronous retry mechanism for awaitable functions.

```python
from arc_v2_util.retry import retry

result = await retry(
    my_function,
    attempts=3,
    delay=2.0,
)
```

The function is retried until it succeeds or the configured number of attempts is exhausted.

By default:

| Option     |       Default |
| ---------- | ------------: |
| `attempts` |           `3` |
| `delay`    | `2.0` seconds |

After all attempts fail, `RetryError` is raised with the collected errors.

### Errors

ARC-V2-Util defines a small hierarchy for utility-specific errors:

```text
ARCUtilError^
└── RetryError
```

`ConstantTypeError` is used for invalid constant values or type conversions.

Example:

```python
from arc_v2_util.errors import ConstantTypeError, RetryError
```

## Installation

Add ARC-V2-Util as a dependency of your ARC V2 project.

```bash
uv add git+https://github.com/ARC-V2-AI/ARC-V2-Util.git
```

## Usage

ARC-V2-Util is intended to be used directly by ARC V2 components.

A typical project might use several utilities together:

```python
from arc_v2_util.constants import Constant
from arc_v2_util.retry import retry

PORT = Constant(default=7842)
DEBUG = Constant(default=False)


async def connect():
    ...
    

async def start():
    await retry(
        connect,
        attempts=5,
        delay=1.0,
    )
```

The utilities are deliberately independent so projects only need to use the components they require.

---

## Design

ARC-V2-Util follows a simple principle:

> **Provide common building blocks without becoming another framework.**

Utilities should remain:

* small
* reusable
* predictable
* easy to integrate
* independent from individual ARC services

ARC-V2-Util should support the wider ARC V2 ecosystem without taking responsibility for service installation, supervision, lifecycle management, or application-specific behavior.

---

## Development Status

ARC-V2-Util is under **active development**.

The current utility set is intentionally small and may expand as recurring patterns emerge across ARC V2 projects.

> [!NOTE]
> New utilities should solve broadly reusable problems within the ARC V2 ecosystem rather than introducing application-specific functionality.

---

<div align="center">

**ARC-V2-Util**

*Shared building blocks for ARC V2.*

</div>
