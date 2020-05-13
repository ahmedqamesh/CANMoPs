#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ALl kind of constants used in CANopen.

Documentation of official CANopen constants is taken from the official CANopen
specification [CiA301]_.

:Author: Ahmed Qamesh
:Contact: ahmed.qamesh@cern.ch
:Organization: Bergische Universität Wuppertal
"""
from math import inf
# Third party modules
from aenum import IntEnum
from canlib import canlib

MAX_DATABYTES = 8
""":obj:`int` : The maxmimum number of data bytes in a standard |CAN|
message"""
MSGHEADER = 'ID DLC  D0--D1--D2--D3--D4--D5--D6--D7' + '    Time '# * (MAX_DATABYTES * 4 - 4) + 'TIME'
""":obj:`str` : Used as header for output of |CAN| messages"""
PSPP_REGISTERS = {'ChipID1': 0, 'ChipID2': 1, 'ADCR1': 2, 'ADCR2': 3, 'DIN': 4,
                  'DIN': 4, 'DOUT': 5, 'Bypass': 6, 'ADCmux': 7, 'ADCL1': 8,
                  'ADCL2': 9, 'Control': 10, 'BGHI': 11, 'BGLO': 12}
""":obj:`dict` : Keys are |PSPP| register names and values are their number."""
PSPPMONVALS = {'Temperature1': 0, 'Temperature2': 1, 'Voltage': 2}
""":obj:`dict` : Keys are names of monitoring values and values are their
relative position."""

CANLIB_BITRATES = {
    1000000: canlib.canBITRATE_1M,
    500000: canlib.canBITRATE_500K,
    250000: canlib.canBITRATE_250K,
    125000: canlib.canBITRATE_125K,
    100000: canlib.canBITRATE_100K,
    62000: canlib.canBITRATE_62K,
    50000: canlib.canBITRATE_50K,
    83000: canlib.canBITRATE_83K,
    10000: canlib.canBITRATE_10K,
}
""":obj:`dict` : Translate integer bitrates given in bit/s to :mod:`canlib`
constants"""


class STATUS(IntEnum):
    """Default status codes for |CAN| nodes"""
    INITIALIZING = 0
    STOPPED = 4
    OPERATIONAL = 5
    PREOPERATIONAL = 127


class COBID(IntEnum):
    """Default |COBID|\ s used by CANopen_."""
    NMT_MASTER = 0
    EMCY = 0x80
    TPDO0 = 0x180
    TPDO1 = 0x280
    SDO_TX = 0x580
    SDO_RX = 0x600
    NMT_ERROR_CTRL = 0x700


class ATTR(IntEnum):
    """Access attributes for data objects"""

    RO = 1
    """Read only access"""
    WO = 2
    """Write only access"""
    RW = 3
    """Read and write access"""
    CONST = 4
    """Read only access, value is constant.

    The value may change in |NMT| state Initialisation. The value shall not
    change in the |NMT| states preoperation, operational and stopped.
    """

    @classmethod
    def _missing_name_(cls, name):
        for member in cls:
            if member.name.lower() == name.lower():
                return member


class VARTYPE(IntEnum):
    """Object dictionary data types according to [CiA301]_.

    Numbers correspond to |OD| indices where they are defined. The free indices
    in between are marked as reserved.
    """
    BOOLEAN = 1
    INTEGER8 = 2
    INTEGER16 = 3
    INTEGER32 = 4
    UNSIGNED8 = 5
    UNSIGNED16 = 6
    UNSIGNED32 = 7
    REAL32 = 8
    VISISBLE_STRING = 9
    OCTET_STRING = 0xa
    UNICODE_STRING = 0xb
    TIME_OF_DAY = 0xc
    TIME_DIFFERENCE = 0xd
    DOMAIN = 0xf
    INTEGER24 = 0x10
    REAL64 = 0x11
    INTEGER40 = 0x12
    INTEGER48 = 0x13
    INTEGER56 = 0x14
    INTEGER64 = 0x15
    UNSIGNED24 = 0x16
    UNSIGNED40 = 0x18
    UNSIGNED48 = 0x19
    UNSIGNED56 = 0x1a
    UNSIGNED64 = 0x1b
    PDO_COMMUNICATION_PARAMETER = 0x20
    PDO_MAPPING = 0x21
    SDO_PARAMETER = 0x22
    IDENTITY = 0x23
    

def LIMITS(vartype, minimum, maximum):
    if vartype is None:
        return None, None
    retmin = -inf if minimum is None else minimum
    retmax = inf if maximum is None else maximum
    if vartype.name.startswith('UNSIGNED'):
        retmin = max(0, retmin)
        retmax = min(2 ** (int(vartype.name.strip('UNSIGNED'))) - 1, retmax)
    return retmin, retmax


class ENTRYTYPE(IntEnum):
    """Object Dictionary object definitions

    Object codes and documenation correspond to [CiA301]_.
    """

    NULL = 0
    """An object with no data fields"""
    DOMAIN = 2
    """Large variable amount of data, e.g. executable program code"""
    DEFTYPE = 5
    """Denotes a type definition

    Possible types may be such as a BOOLEAN, UNSIGNED16, FLOAT and so on.
    """
    DEFSTRUCT = 6
    """Defines a new record type e.g. the |PDO| mapping structure at 21h."""
    VAR = 7
    """A single value such as an UNSIGNED8, BOOLEAN, FLOAT, INTEGER16,
    VISIBLE STRING etc."""
    ARRAY = 8
    """A multiple data field object

    Each data field is a simple variable of the SAME basic data type e.g.
    array of UNSIGNED16 etc. Sub-index 0 is of UNSIGNED8 and therefore not
    part of the ARRAY data.
    """
    RECORD = 9
    """A multiple data field object

    The data fields may be any combination of simple variables. Sub-index 0 is
    of UNSIGNED8 and sub-index 255 is of UNSIGNED32 and therefore not part of
    the RECORD data.
    """


class sdoAbortCodes(IntEnum):
    """|SDO| abort codes as defined in [CiA301]_."""

    TOGGLE_BIT = 0x05030000
    """Toggle bit not alternated."""
    TIMEOUT = 0x05040000
    """|SDO| protocol timed out."""
    COMMAND = 0x05030001
    """Client/server command specifier not valid or unknown."""
    BLOCK_SIZE = 0x05040002
    """Invalid block size (block mode only)."""
    SEQUENCE_NUM = 0x05040003
    """Invalid sequence number (block mode only)."""
    CRC_ERROR = 0x05040004
    """|CRC| error (block mode only)."""
    OUT_OF_MEMORY = 0x05040005
    """Out of memory."""
    ACCESS = 0x06010000
    """Unsupported access to an object."""
    WO = 0x06010001
    """Attempt to read a write only object."""
    RO = 0x06010002
    """Attempt to write a read only object."""
    NO_OBJECT = 0x06020000
    """Object does not exist in the object dictionary."""
    PDO_MAPPING = 0x06040041
    """Object cannot be mapped to the |PDO|."""
    PDO_LENGTH = 0x06040042
    """The number and length of the objects to be mapped would exceed |PDO|
    length.
    """
    INCOMP_PARAM = 0x06040043
    """General parameter incompatibility reason."""
    INCOMP_INTERNAL = 0x06040047
    """General internal incompatibility in the device."""
    HARDWARE_ERROR = 0x06060000
    """Access failed due to an hardware error."""
    PARAM_LEN = 0x06070010
    """Data type does not match, length of service parameter does not match"""
    PARAM_LEN_HI = 0x06070012
    """Data type does not match, length of service parameter too high"""
    PARAM_LEN_LO = 0x06070013
    """Data type does not match, length of service parameter too low"""
    SUBINDEX = 0x06090011
    """Sub-index does not exist."""
    PARAM_VALUE = 0x06090030
    """Invalid value for parameter (download only)."""
    PARAM_VAL_HI = 0x06090031
    """Value of parameter written too high (download only)."""
    PARAM_VAL_LO = 0x06090032
    """Value of parameter written too low (download only)."""
    MAX_LESS_MIN = 0x06090036
    """Maximum value is less than minimum value."""
    RES_AVBL = 0x060A0023
    """Resource not available: |SDO| connection"""
    GENERAL_ERROR = 0x08000000
    """General error"""
    APP = 0x08000020
    """Data cannot be transferred or stored to the application."""
    APP_LOCAL = 0x08000021
    """Data cannot be transferred or stored to the application because of local
    control.
    """
    APP_STATE = 0x08000022
    """Data cannot be transferred or stored to the application because of the
    present device state.
    """
    NO_OD = 0x08000023
    """Object dictionary dynamic generation fails or no object dictionary is
    present (e.g. object dictionary is generated from file and generation fails
    because of an file error).
    """
    NO_DATA = 0x08000024
    """No data available"""
