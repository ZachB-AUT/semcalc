
#!/bin/bash

# Project name
PROJECT_NAME="semcalc"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Create project structure
echo "Creating project structure..."
mkdir -p $PROJECT_NAME/{data_handler,scheduler,models}
mkdir -p $PROJECT_NAME/tests
touch $PROJECT_NAME/__init__.py

# Create source files
cat > $PROJECT_NAME/data_handler/__init__.py << EOL
# Package initialization for data_handler
EOL

cat > $PROJECT_NAME/data_handler/json_loader.py << EOL
"""
Handles loading and processing of course JSON data.
Includes semester extraction and data validation.
"""
EOL

cat > $PROJECT_NAME/data_handler/time_utils.py << EOL
"""
Utilities for handling time conversions and comparisons.
Includes functions for checking time slot overlaps.
"""
EOL

cat > $PROJECT_NAME/scheduler/__init__.py << EOL
# Package initialization for scheduler
EOL

cat > $PROJECT_NAME/scheduler/conflict_checker.py << EOL
"""
Handles detection of scheduling conflicts between courses.
Includes validation of semester course loads.
"""
EOL

cat > $PROJECT_NAME/scheduler/schedule_generator.py << EOL
"""
Core scheduling logic.
Generates possible course combinations that satisfy constraints.
"""
EOL

cat > $PROJECT_NAME/scheduler/constraints.py << EOL
"""
Defines scheduling constraints and scoring criteria.
Includes preference handling for early/late classes and days off.
"""
EOL

cat > $PROJECT_NAME/models/__init__.py << EOL
# Package initialization for models
EOL

cat > $PROJECT_NAME/models/course.py << EOL
"""
Course class definition.
Represents a course with its associated streams and sessions.
"""
EOL

cat > $PROJECT_NAME/models/session.py << EOL
"""
Session class definition.
Represents individual class sessions with times and locations.
"""
EOL

cat > $PROJECT_NAME/models/schedule.py << EOL
"""
Schedule class definition.
Represents a complete semester schedule with scoring methods.
"""
EOL

cat > $PROJECT_NAME/main.py << EOL
"""
Main entry point for the semester calculator.
Handles CLI interface and program flow.
"""

def main():
    pass

if __name__ == "__main__":
    main()
EOL

# Create requirements.txt
cat > requirements.txt << EOL
python-constraint==1.4.0
pytest==7.4.0
python-dateutil==2.8.2
EOL

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create basic test file
mkdir -p tests
cat > tests/test_basic.py << EOL
"""
Basic test suite for semester calculator.
"""

def test_placeholder():
    assert True
EOL

echo "Project setup complete!"
echo "Activate virtual environment with: source venv/bin/activate"
