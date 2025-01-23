#ifndef EXCEPTIONSBASE_H
#define EXCEPTIONSBASE_H

#include <exception>
#include <string>

/**
 * @class GenericError
 * @brief Exception class for handling SNMP errors in the ezsnmp library.
 *
 * This class extends the standard std::exception class to provide
 * detailed error messages specific to SNMP operations.
 */
class GenericError : public std::exception {
  public:
   GenericError(std::string const& message);
   virtual char const* what() const noexcept override;

  private:
   std::string m_msg;
};

/**
 * @class ConnectionError
 * @brief Exception class for SNMP connection errors.
 *
 * This class represents an error that occurs during an SNMP connection attempt.
 * It inherits from the GenericError base class.
 *
 * @param message A descriptive error message.
 */
class ConnectionError : public GenericError {
  public:
   ConnectionError(std::string const& message);
};

/**
 * @class TimeoutError
 * @brief Exception class for handling SNMP timeout errors.
 *
 * This class represents an error that occurs when an SNMP operation times out.
 * It inherits from GenericError.
 *
 * @param message A descriptive message about the timeout error.
 */
class TimeoutError : public GenericError {
  public:
   TimeoutError(std::string const& message);
};

/**
 * @class UnknownObjectIDError
 * @brief Exception class for unknown SNMP Object ID errors.
 *
 * This exception is thrown when an unknown SNMP Object ID is encountered.
 *
 * @details This class inherits from GenericError and provides additional
 * information about the error through its message.
 *
 * @param message A string containing the error message.
 */
class UnknownObjectIDError : public GenericError {
  public:
   UnknownObjectIDError(std::string const& message);
};

/**
 * @class NoSuchNameError
 * @brief Exception class for handling SNMP "No Such Name" errors.
 *
 * This class represents an error that occurs when an SNMP operation
 * encounters a "No Such Name" error, indicating that the requested
 * object does not exist.
 *
 * @extends GenericError
 */
class NoSuchNameError : public GenericError {
  public:
   NoSuchNameError(std::string const& message);
};

/**
 * @class NoSuchObjectError
 * @brief Exception class for handling SNMP "No Such Object" errors.
 *
 * This exception is thrown when an SNMP operation encounters a "No Such Object" error.
 *
 * @param message A detailed error message.
 */
class NoSuchObjectError : public GenericError {
  public:
   NoSuchObjectError(std::string const& message);
};

/**
 * @class NoSuchInstanceError
 * @brief Exception class for handling SNMP "No Such Instance" errors.
 *
 * This exception is thrown when an SNMP operation encounters a "No Such Instance" error,
 * indicating that the requested instance does not exist.
 *
 * @extends GenericError
 */
class NoSuchInstanceError : public GenericError {
  public:
   NoSuchInstanceError(std::string const& message);
};

/**
 * @class UndeterminedTypeError
 * @brief Exception class for undetermined SNMP type errors.
 *
 * This exception is thrown when an SNMP type cannot be determined.
 *
 * @extends GenericError
 *
 * @param message A descriptive error message.
 */
class UndeterminedTypeError : public GenericError {
  public:
   UndeterminedTypeError(std::string const& message);
};

/**
 * @class ParseError
 * @brief Exception class for handling SNMP parse errors.
 *
 * This exception is thrown when an error occurs while parsing SNMP command line arguments.
 *
 * @extends GenericError
 *
 * @param message A descriptive error message.
 */
class ParseError : public GenericError {
  public:
   ParseError(std::string const& message);
};

/**
 * @class PacketError
 * @brief Exception class for handling SNMP packet errors.
 *
 * This exception is thrown when an error occurs related to SNMP packet processing.
 *
 * @extends GenericError
 *
 * @param message A descriptive error message.
 */
class PacketError : public GenericError {
  public:
   PacketError(std::string const& message);
};

#endif // EXCEPTIONSBASE_H