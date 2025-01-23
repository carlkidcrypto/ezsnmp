#ifndef EXCEPTIONSBASE_H
#define EXCEPTIONSBASE_H

#include <exception>
#include <string>

/**
 * @class GenericErrorBase
 * @brief Exception class for handling SNMP errors in the ezsnmp library.
 *
 * This class extends the standard std::exception class to provide
 * detailed error messages specific to SNMP operations.
 */
class GenericErrorBase : public std::exception {
  public:
   GenericErrorBase(std::string const& message);
   virtual char const* what() const noexcept override;

  private:
   std::string m_msg;
};

/**
 * @class ConnectionErrorBase
 * @brief Exception class for SNMP connection errors.
 *
 * This class represents an error that occurs during an SNMP connection attempt.
 * It inherits from the GenericErrorBase base class.
 *
 * @param message A descriptive error message.
 */
class ConnectionErrorBase : public GenericErrorBase {
  public:
   ConnectionErrorBase(std::string const& message);
};

/**
 * @class TimeoutErrorBase
 * @brief Exception class for handling SNMP timeout errors.
 *
 * This class represents an error that occurs when an SNMP operation times out.
 * It inherits from GenericErrorBase.
 *
 * @param message A descriptive message about the timeout error.
 */
class TimeoutErrorBase : public GenericErrorBase {
  public:
   TimeoutErrorBase(std::string const& message);
};

/**
 * @class UnknownObjectIDErrorBase
 * @brief Exception class for unknown SNMP Object ID errors.
 *
 * This exception is thrown when an unknown SNMP Object ID is encountered.
 *
 * @details This class inherits from GenericErrorBase and provides additional
 * information about the error through its message.
 *
 * @param message A string containing the error message.
 */
class UnknownObjectIDErrorBase : public GenericErrorBase {
  public:
   UnknownObjectIDErrorBase(std::string const& message);
};

/**
 * @class NoSuchNameErrorBase
 * @brief Exception class for handling SNMP "No Such Name" errors.
 *
 * This class represents an error that occurs when an SNMP operation
 * encounters a "No Such Name" error, indicating that the requested
 * object does not exist.
 *
 * @extends GenericErrorBase
 */
class NoSuchNameErrorBase : public GenericErrorBase {
  public:
   NoSuchNameErrorBase(std::string const& message);
};

/**
 * @class NoSuchObjectErrorBase
 * @brief Exception class for handling SNMP "No Such Object" errors.
 *
 * This exception is thrown when an SNMP operation encounters a "No Such Object" error.
 *
 * @param message A detailed error message.
 */
class NoSuchObjectErrorBase : public GenericErrorBase {
  public:
   NoSuchObjectErrorBase(std::string const& message);
};

/**
 * @class NoSuchInstanceErrorBase
 * @brief Exception class for handling SNMP "No Such Instance" errors.
 *
 * This exception is thrown when an SNMP operation encounters a "No Such Instance" error,
 * indicating that the requested instance does not exist.
 *
 * @extends GenericErrorBase
 */
class NoSuchInstanceErrorBase : public GenericErrorBase {
  public:
   NoSuchInstanceErrorBase(std::string const& message);
};

/**
 * @class UndeterminedTypeErrorBase
 * @brief Exception class for undetermined SNMP type errors.
 *
 * This exception is thrown when an SNMP type cannot be determined.
 *
 * @extends GenericErrorBase
 *
 * @param message A descriptive error message.
 */
class UndeterminedTypeErrorBase : public GenericErrorBase {
  public:
   UndeterminedTypeErrorBase(std::string const& message);
};

/**
 * @class ParseErrorBase
 * @brief Exception class for handling SNMP parse errors.
 *
 * This exception is thrown when an error occurs while parsing SNMP command line arguments.
 *
 * @extends GenericErrorBase
 *
 * @param message A descriptive error message.
 */
class ParseErrorBase : public GenericErrorBase {
  public:
   ParseErrorBase(std::string const& message);
};

/**
 * @class PacketErrorBase
 * @brief Exception class for handling SNMP packet errors.
 *
 * This exception is thrown when an error occurs related to SNMP packet processing.
 *
 * @extends GenericErrorBase
 *
 * @param message A descriptive error message.
 */
class PacketErrorBase : public GenericErrorBase {
  public:
   PacketErrorBase(std::string const& message);
};

#endif // EXCEPTIONSBASE_H