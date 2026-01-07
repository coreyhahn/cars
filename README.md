# Cars

A simple Python project to test AI and GitHub integration.

## Overview

This repository contains a basic Car class implementation with properties and methods to demonstrate object-oriented programming in Python. It's designed to test AI-assisted development and GitHub integration features.

## Features

- **Car Class**: A simple class representing a car with:
  - Properties: make, model, year, color, odometer
  - Methods: drive(), get_description(), get_odometer()
  - String representations for easy display

- **Demo Script**: A demonstration showing how to create and interact with Car objects

## Usage

Run the demo script to see the Car class in action:

```bash
python3 demo.py
```

## Example

```python
from car import Car

# Create a new car
my_car = Car("Toyota", "Camry", 2020, "Blue")

# Drive the car
my_car.drive(150)

# Get car information
print(my_car)  # Output: 2020 Blue Toyota Camry - 150 miles
```

## Files

- `car.py` - Main Car class implementation
- `demo.py` - Demonstration script showing Car usage
- `.gitignore` - Git ignore rules for Python projects

## Testing AI and GitHub Integration

This repository serves as a test case for:
- AI-assisted code generation and modification
- GitHub pull requests and issue management
- Automated code review processes
- Integration between AI coding tools and version control
