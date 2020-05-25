import ctypes as ct

PROPERTY_START_OF_MEASUREMENT = {
    'type': ct.c_int(), 'value': 1, 'name': "START_OF_MEASUREMENT"}
PROPERTY_FIRST_TRIGGER = {
    'type': ct.c_int(), 'value': 2, 'name': "FIRST_TRIGGER"}
PROPERTY_USE_OFFSET = {
    'type': ct.c_int(), 'value': 3, 'name': "USE_OFFSET"}
PROPERTY_OFFSET = {
    'type': ct.c_int64(), 'value': 4, 'name': "OFFSET"}
PROPERTY_CHANNEL_MASK = {
    'type': ct.c_uint(), 'value': 5, 'name': "CHANNEL_MASK"}
PROPERTY_HLP_J1939 = {
    'type': ct.c_int(), 'value': 6, 'name': "HLP_J1939"}
PROPERTY_CALENDAR_TIME_STAMPS = {
    'type': ct.c_int(), 'value': 7, 'name': "CALENDAR_TIME_STAMPS"}
PROPERTY_WRITE_HEADER = {
    'type': ct.c_int(), 'value': 8, 'name': "WRITE_HEADER"}
PROPERTY_SEPARATOR_CHAR = {
    'type': ct.c_char(), 'value': 9, 'name': "SEPARATOR_CHAR"}
PROPERTY_DECIMAL_CHAR = {
    'type': ct.c_char(), 'value': 10, 'name': "DECIMAL_CHAR"}
PROPERTY_ID_IN_HEX = {
    'type': ct.c_int(), 'value': 11, 'name': "ID_IN_HEX"}
PROPERTY_DATA_IN_HEX = {
    'type': ct.c_int(), 'value': 12, 'name': "DATA_IN_HEX"}
PROPERTY_NUMBER_OF_TIME_DECIMALS = {
    'type': ct.c_int(), 'value': 13, 'name': "NUMBER_OF_TIME_DECIMALS"}
PROPERTY_NAME_MANGLING = {
    'type': ct.c_int(), 'value': 14, 'name': "NAME_MANGLING"}
PROPERTY_FILL_BLANKS = {
    'type': ct.c_int(), 'value': 15, 'name': "FILL_BLANKS"}
PROPERTY_SHOW_UNITS = {
    'type': ct.c_int(), 'value': 16, 'name': "SHOW_UNITS"}
PROPERTY_ISO8601_DECIMALS = {
    'type': ct.c_int(), 'value': 17, 'name': "ISO8601_DECIMALS"}
PROPERTY_MERGE_LINES = {
    'type': ct.c_int(), 'value': 18, 'name': "MERGE_LINES"}
PROPERTY_RESAMPLE_COLUMN = {
    'type': ct.c_int(), 'value': 19, 'name': "RESAMPLE_COLUMN"}
PROPERTY_VERSION = {
    'type': ct.c_int(), 'value': 20, 'name': "VERSION"}
PROPERTY_SHOW_COUNTER = {
    'type': ct.c_int(), 'value': 21, 'name': "SHOW_COUNTER"}
PROPERTY_CROP_PRETRIGGER = {
    'type': ct.c_int(), 'value': 22, 'name': "CROP_PRETRIGGER"}
PROPERTY_ENUM_VALUES = {
    'type': ct.c_int(), 'value': 23, 'name': "ENUM_VALUES"}
PROPERTY_SIZE_LIMIT = {
    'type': ct.c_uint(), 'value': 24, 'name': "SIZE_LIMIT"}
PROPERTY_TIME_LIMIT = {
    'type': ct.c_uint(), 'value': 25, 'name': "TIME_LIMIT"}
PROPERTY_LIMIT_DATA_BYTES = {
    'type': ct.c_int(), 'value': 26, 'name': "LIMIT_DATA_BYTES"}
PROPERTY_CREATION_DATE = {
    'type': ct.c_int64(), 'value': 27, 'name': "CREATION_DATE"}
PROPERTY_OVERWRITE = {
    'type': ct.c_int(), 'value': 28, 'name': "OVERWRITE"}
PROPERTY_SIGNAL_BASED = {
    'type': None, 'value': 1001, 'name': "SIGNAL_BASED"}
PROPERTY_SHOW_SIGNAL_SELECT = {
    'type': None, 'value': 1002, 'name': "SHOW_SIGNAL_SELECT"}
PROPERTY_ATTACHMENTS = {
    'type': None, 'value': 1003, 'name': "ATTACHMENTS"}
