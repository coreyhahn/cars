"""
Demo script to showcase the Car class functionality.
"""

from car import Car


def main():
    """Demonstrate car operations."""
    print("=== Car Demo ===\n")
    
    # Create some cars
    car1 = Car("Toyota", "Camry", 2020, "Blue")
    car2 = Car("Honda", "Civic", 2019, "Red")
    car3 = Car("Ford", "Mustang", 2021, "Black")
    
    cars = [car1, car2, car3]
    
    # Display initial state
    print("Initial cars:")
    for car in cars:
        print(f"  {car}")
    
    print("\n--- Driving some cars ---")
    
    # Drive the cars
    car1.drive(150)
    print(f"Drove {car1.get_description()} for 150 miles")
    
    car2.drive(200)
    print(f"Drove {car2.get_description()} for 200 miles")
    
    car3.drive(75.5)
    print(f"Drove {car3.get_description()} for 75.5 miles")
    
    # Display updated state
    print("\nCars after driving:")
    for car in cars:
        print(f"  {car}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
