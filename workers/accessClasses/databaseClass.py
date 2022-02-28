try:
    from mysql.connector import MySQLConnection, Error
    import configparser
except ImportError as impEr:
    raise impEr


class NoConfigException(Exception):
    """A Custom Execption class to be raised if there is no db config file given to create a db connection"""


class Database:
    """Class meant to be generalised to create a db connection from a given config and perform CRUD operations"""

    def __init__(self, config_file: str = ''):

        self.config_file = config_file

        if not self.config_file:
            raise NoConfigException("No Config File Given")

    def parse_config(self, section: str = ''):
        """Method to be called which will parse the config file given and return a dict with appropriate db connection information"""

        # creating a parser obj and parsing config
        parser = configparser.ConfigParser()
        parser.read(self.config_file)

        try:
            db = {}
            # if there is a section in our config matching the given section it will be extracted and looped through
            if parser.has_section(section):
                items = parser.items(section)
                for item in items:
                    # this unpacks the tuple into a k/v pair in a dict
                    db[item[0]] = item[1]

        except:
            raise Exception(f"{section} is not found in {self.config_file}")

        # return the db dict if no exception raised
        return db

    def read_conn(self):
        """Method to call parse_config method with the section being myRead"""

        db_config = self.parse_config(section="myRead")

        # create a null variable to represent the connection

        conn = None

        try:
            # try creating a connection using a dict as the arg
            conn = MySQLConnection(**db_config)

            if not conn.is_connected():
                print("\n i couldn't connect to the database \n")

        except Error as e:
            raise e

        finally:
            if conn is not None and conn.is_connected():
                return conn

    def write_conn(self):
        """Creates a connection with a user having write permissions"""

        db_config = self.parse_config(section="myWrite")
        conn = None
        try:
            conn = MySQLConnection(**db_config)
            if not conn.is_connected():
                print("\n i couldn't connect to the database")
        except Error as e:
            raise e
        finally:
            if conn is not None and conn.is_connected():
                return conn
