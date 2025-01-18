#include "exceptions.h"

EzSnmpError::EzSnmpError(const std::string& message) : m_msg(message) {}

const char* EzSnmpError::what() const noexcept {
    return m_msg.c_str();
}

EzSnmpConnectionError::EzSnmpConnectionError(const std::string& message) : EzSnmpError(message) {}

EzSnmpTimeoutError::EzSnmpTimeoutError(const std::string& message) : EzSnmpConnectionError(message) {}

EzSnmpUnknownObjectIDError::EzSnmpUnknownObjectIDError(const std::string& message) : EzSnmpError(message) {}

EzSnmpNoSuchNameError::EzSnmpNoSuchNameError(const std::string& message) : EzSnmpError(message) {}

EzSnmpNoSuchObjectError::EzSnmpNoSuchObjectError(const std::string& message) : EzSnmpError(message) {}

EzSnmpNoSuchInstanceError::EzSnmpNoSuchInstanceError(const std::string& message) : EzSnmpError(message) {}

EzSnmpUndeterminedTypeError::EzSnmpUndeterminedTypeError(const std::string& message) : EzSnmpError(message) {}