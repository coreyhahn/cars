"""
Simple tests for the Car class.
"""

from car import Car


def test_car_creation():
    """Test creating a car instance."""
    car = Car("Toyota", "Camry", 2020, "Blue")
    assert car.make == "Toyota"
    assert car.model == "Camry"
    assert car.year == 2020
    assert car.color == "Blue"
    assert car.odometer == 0
    print("✓ Car creation test passed")


def test_car_drive():
    """Test driving a car."""
    car = Car("Honda", "Civic", 2019)
    result = car.drive(100)
    assert car.odometer == 100
    assert result == 100
    
    car.drive(50)
    assert car.odometer == 150
    print("✓ Car drive test passed")


def test_car_description():
    """Test car description."""
    car = Car("Ford", "Mustang", 2021, "Black")
    description = car.get_description()
    assert description == "2021 Black Ford Mustang"
    print("✓ Car description test passed")


def test_car_negative_miles():
    """Test that negative miles raises an error."""
    car = Car("Tesla", "Model 3", 2022, "White")
    try:
        car.drive(-10)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Miles cannot be negative"
        print("✓ Negative miles test passed")


def test_car_string_representation():
    """Test string representation of car."""
    car = Car("BMW", "X5", 2020, "Silver")
    car.drive(1234)
    car_str = str(car)
    assert "BMW" in car_str
    assert "X5" in car_str
    assert "1,234" in car_str
    print("✓ String representation test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Car class tests...\n")
    test_car_creation()
    test_car_drive()
    test_car_description()
    test_car_negative_miles()
    test_car_string_representation()
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()
