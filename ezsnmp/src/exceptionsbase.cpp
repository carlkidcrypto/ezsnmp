#include "exceptionsbase.h"

GenericError::GenericError(std::string const& message) : m_msg(message) {}

char const* GenericError::what() const noexcept { return m_msg.c_str(); }

ConnectionError::ConnectionError(std::string const& message) : GenericError(message) {}

TimeoutError::TimeoutError(std::string const& message) : GenericError(message) {}

UnknownObjectIDError::UnknownObjectIDError(std::string const& message) : GenericError(message) {}

NoSuchNameError::NoSuchNameError(std::string const& message) : GenericError(message) {}

NoSuchObjectError::NoSuchObjectError(std::string const& message) : GenericError(message) {}

NoSuchInstanceError::NoSuchInstanceError(std::string const& message) : GenericError(message) {}

UndeterminedTypeError::UndeterminedTypeError(std::string const& message) : GenericError(message) {}

ParseError::ParseError(std::string const& message) : GenericError(message) {}

PacketError::PacketError(std::string const& message) : GenericError(message) {}