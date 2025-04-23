#include "exceptionsbase.h"

GenericErrorBase::GenericErrorBase(std::string const& message) : m_msg(message) {}

char const* GenericErrorBase::what() const noexcept { return m_msg.c_str(); }

ConnectionErrorBase::ConnectionErrorBase(std::string const& message) : GenericErrorBase(message) {}

TimeoutErrorBase::TimeoutErrorBase(std::string const& message) : GenericErrorBase(message) {}

UnknownObjectIDErrorBase::UnknownObjectIDErrorBase(std::string const& message)
    : GenericErrorBase(message) {}

NoSuchNameErrorBase::NoSuchNameErrorBase(std::string const& message) : GenericErrorBase(message) {}

NoSuchObjectErrorBase::NoSuchObjectErrorBase(std::string const& message)
    : GenericErrorBase(message) {}

NoSuchInstanceErrorBase::NoSuchInstanceErrorBase(std::string const& message)
    : GenericErrorBase(message) {}

UndeterminedTypeErrorBase::UndeterminedTypeErrorBase(std::string const& message)
    : GenericErrorBase(message) {}

ParseErrorBase::ParseErrorBase(std::string const& message) : GenericErrorBase(message) {}

PacketErrorBase::PacketErrorBase(std::string const& message) : GenericErrorBase(message) {}