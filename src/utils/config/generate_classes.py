import __init__
import os
import configparser

# ROOT_DIR =  os.path.dirname(__file__)
CONFIG_PATH = os.path.join(__init__.ROOT_DIR,'config','config.ini')
SCHEMA_PATH = os.path.join(__init__.ROOT_DIR,'src','utils','config','schema.py')
MANAGER_PATH = os.path.join(__init__.ROOT_DIR,'src','utils','config','manager.py')

def read_config(config_path):
    try:
        print(f"Reading configuration from {config_path}")
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        return config
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        raise

def infer_type(value):
    try:
        int(value)
        return 'int'
    except ValueError:
        try:
            float(value)
            return 'float'
        except ValueError:
            if value.lower() in ('true', 'false'):
                return 'boolean'
            return 'str'

def generate_class(section, options):
    try:
        print(f"Generating class for section [{section}]")
        class_name = f"{section}Schema"
        class_code = f"\nclass {class_name}(ConfigSchema):\n"
        class_code += f"    \"\"\"\n    [{section}]\n    \"\"\"\n"
        class_code += f"    def __init__(self, config_section: SectionProxy) -> None:\n"
        class_code += f"        super().__init__(config_section)\n"
        
        for option in options:
            option_type = infer_type(options[option])
            print(f"  Adding property '{option}' of type '{option_type}'")
            class_code += f"    @property\n"
            class_code += f"    def {option}(self):\n"
            if option_type == 'int':
                class_code += f"        return self._config_section.getint('{option}')\n"
            elif option_type == 'float':
                class_code += f"        return self._config_section.getfloat('{option}')\n"
            elif option_type == 'boolean':
                class_code += f"        return self._config_section.getboolean('{option}')\n"
            else:
                class_code += f"        return self._config_section.get('{option}')\n"
        
        return class_code
    except Exception as e:
        print(f"Error generating class for section [{section}]: {e}")
        raise

def update_schema_file(config):
    try:
        print(f"Updating schema file: {SCHEMA_PATH}")
        schema_imports = "import __init__\nfrom configparser import SectionProxy\nimport os\n\n"
        schema_base_class = "class ConfigSchema:\n    def __init__(self, config_section: SectionProxy) -> None:\n        self._config_section = config_section\n"
        
        class_definitions = ""
        
        for section in config.sections():
            class_definitions += generate_class(section, config[section])
        
        with open(SCHEMA_PATH, 'w', encoding='utf-8') as f:
            f.write(schema_imports)
            f.write(schema_base_class)
            f.write(class_definitions)
        print(f"Schema file updated: {SCHEMA_PATH}")
    except Exception as e:
        print(f"Error updating schema file: {e}")
        raise

def update_manager_file(config):
    try:
        print(f"Updating manager file: {MANAGER_PATH}")
        manager_imports = "import __init__\nimport configparser\nimport os\nfrom .schema import (\n"
        for section in config.sections():
            manager_imports += f"    {section}Schema,\n"
        manager_imports += ")\n\n"
        
        manager_class = """
class ConfigManager(object):
    _instance = None
    
    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance
    
    def __init__(self, config_path: str= os.path.join(__init__.ROOT_DIR, 'config', 'config.ini')):
        self._config = configparser.ConfigParser()
        self._config.read(config_path ,encoding='utf-8')\n\n"""

        for section in config.sections():
            manager_class += f"        self.{section.lower()} = {section}Schema(self._config['{section}'])\n"

        with open(MANAGER_PATH, 'w', encoding='utf-8') as f:
            f.write(manager_imports)
            f.write(manager_class)
        print(f"Manager file updated: {MANAGER_PATH}")
    except Exception as e:
        print(f"Error updating manager file: {e}")
        raise

def main():
    try:
        config = read_config(CONFIG_PATH)
        update_schema_file(config)
        update_manager_file(config)
        print("Configuration and class generation completed successfully.")
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
