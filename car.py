"""
Car class for testing AI and GitHub integration.
"""


class Car:
    """Represents a car with basic properties and operations."""
    
    def __init__(self, make, model, year, color="Unknown"):
        """
        Initialize a new Car instance.
        
        Args:
            make (str): The manufacturer of the car
            model (str): The model name
            year (int): The year of manufacture
            color (str): The color of the car (default: "Unknown")
        """
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.odometer = 0
    
    def drive(self, miles):
        """
        Drive the car for a specified number of miles.
        
        Args:
            miles (float): Number of miles to drive
            
        Returns:
            float: New odometer reading
        """
        if miles < 0:
            raise ValueError("Miles cannot be negative")
        self.odometer += miles
        return self.odometer
    
    def get_description(self):
        """
        Get a formatted description of the car.
        
        Returns:
            str: Description of the car
        """
        return f"{self.year} {self.color} {self.make} {self.model}"
    
    def get_odometer(self):
        """
        Get the current odometer reading.
        
        Returns:
            float: Current odometer reading in miles
        """
        return self.odometer
    
    def __str__(self):
        """String representation of the car."""
        return f"{self.get_description()} - {self.odometer:,} miles"
    
    def __repr__(self):
        """Developer-friendly representation of the car."""
        return f"Car(make='{self.make}', model='{self.model}', year={self.year}, color='{self.color}')"
