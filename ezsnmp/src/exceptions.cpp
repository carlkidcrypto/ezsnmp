#include "exceptions.h"

GenericError::GenericError(const std::string& message) : m_msg(message) {}

const char* GenericError::what() const noexcept {
    return m_msg.c_str();
}

ConnectionError::ConnectionError(const std::string& message) : GenericError(message) {}

TimeoutError::TimeoutError(const std::string& message) : GenericError(message) {}

UnknownObjectIDError::UnknownObjectIDError(const std::string& message) : GenericError(message) {}

NoSuchNameError::NoSuchNameError(const std::string& message) : GenericError(message) {}

NoSuchObjectError::NoSuchObjectError(const std::string& message) : GenericError(message) {}

NoSuchInstanceError::NoSuchInstanceError(const std::string& message) : GenericError(message) {}

UndeterminedTypeError::UndeterminedTypeError(const std::string& message) : GenericError(message) {}

ParseError::ParseError(const std::string& message) : GenericError(message) {}

PacketError::PacketError(const std::string& message) : GenericError(message) {}