#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <exception>
#include <string>

/**
 * @class EzSnmpError
 * @brief Exception class for handling SNMP errors in the ezsnmp library.
 *
 * This class extends the standard std::exception class to provide
 * detailed error messages specific to SNMP operations.
 *
 * @note This class is part of the ezsnmp library.
 */
class EzSnmpError : public std::exception {
public:
    EzSnmpError(const std::string& message);
    virtual const char* what() const noexcept override;
private:
    std::string m_msg;
};

/**
 * @class EzSnmpConnectionError
 * @brief Exception class for SNMP connection errors.
 *
 * This class represents an error that occurs during an SNMP connection attempt.
 * It inherits from the EzSnmpError base class.
 *
 * @param message A descriptive error message.
 */
class EzSnmpConnectionError : public EzSnmpError {
public:
    EzSnmpConnectionError(const std::string& message);
};

/**
 * @class EzSnmpTimeoutError
 * @brief Exception class for handling SNMP timeout errors.
 *
 * This class represents an error that occurs when an SNMP operation times out.
 * It inherits from EzSnmpConnectionError.
 *
 * @param message A descriptive message about the timeout error.
 */
class EzSnmpTimeoutError : public EzSnmpConnectionError {
public:
    EzSnmpTimeoutError(const std::string& message);
};

/**
 * @class EzSnmpUnknownObjectIDError
 * @brief Exception class for unknown SNMP Object ID errors.
 *
 * This exception is thrown when an unknown SNMP Object ID is encountered.
 *
 * @details This class inherits from EzSnmpError and provides additional
 * information about the error through its message.
 *
 * @param message A string containing the error message.
 */
class EzSnmpUnknownObjectIDError : public EzSnmpError {
public:
    EzSnmpUnknownObjectIDError(const std::string& message);
};

/**
 * @class EzSnmpNoSuchNameError
 * @brief Exception class for handling SNMP "No Such Name" errors.
 *
 * This class represents an error that occurs when an SNMP operation
 * encounters a "No Such Name" error, indicating that the requested
 * object does not exist.
 *
 * @extends EzSnmpError
 */
class EzSnmpNoSuchNameError : public EzSnmpError {
public:
    EzSnmpNoSuchNameError(const std::string& message);
};

/**
 * @class EzSnmpNoSuchObjectError
 * @brief Exception class for handling SNMP "No Such Object" errors.
 *
 * This exception is thrown when an SNMP operation encounters a "No Such Object" error.
 *
 * @param message A detailed error message.
 */
class EzSnmpNoSuchObjectError : public EzSnmpError {
public:
    EzSnmpNoSuchObjectError(const std::string& message);
};

/**
 * @class EzSnmpNoSuchInstanceError
 * @brief Exception class for handling SNMP "No Such Instance" errors.
 *
 * This exception is thrown when an SNMP operation encounters a "No Such Instance" error,
 * indicating that the requested instance does not exist.
 *
 * @extends EzSnmpError
 */
class EzSnmpNoSuchInstanceError : public EzSnmpError {
public:
    EzSnmpNoSuchInstanceError(const std::string& message);
};

/**
 * @class EzSnmpUndeterminedTypeError
 * @brief Exception class for undetermined SNMP type errors.
 *
 * This exception is thrown when an SNMP type cannot be determined.
 *
 * @extends EzSnmpError
 *
 * @param message A descriptive error message.
 */
class EzSnmpUndeterminedTypeError : public EzSnmpError {
public:
    EzSnmpUndeterminedTypeError(const std::string& message);
};

#endif // EXCEPTIONS_H